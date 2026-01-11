"""
Async PPT Processor - Asynchronous orchestration of slide processing.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger, get_job_logger
from app.core.config import settings
from app.core.exceptions import (
    PPTParseError,
    LLMGenerationError,
    TTSError,
    VideoAssemblyError,
    JobCancelledError,
)
from app.services.ppt_parser import parse_ppt
from app.services.narration_chain import generate_narration_async, generate_narration_sync
from app.services.qa_chain import generate_mcqs_async, generate_mcqs_sync
from app.services.qa_validator import validate_and_fix_mcqs, validate_mcq_language
from app.services.tts_service import synthesize_speech
from app.services.slide_renderer import render_slide_image
from app.services.video_assembler import create_video
from app.services.video_stitcher import stitch_videos
from app.services.job_manager import job_manager
from app.models.job import (
    JobResult,
    SlideResult,
    SlideState,
    SlideProgress,
    MCQuestion,
)

logger = get_logger(__name__)


async def process_ppt_async(
    job_id: str,
    ppt_path: str,
    language: str = "en",
    max_slides: int = 5,
    generate_video: bool = True,
    generate_mcqs: bool = True,
) -> JobResult:
    """
    Process a PowerPoint file asynchronously with progress tracking.
    
    Args:
        job_id: Unique job identifier
        ppt_path: Path to the .pptx file
        language: Target language (en, fr, hi)
        max_slides: Maximum slides to process
        generate_video: Whether to generate video
        generate_mcqs: Whether to generate MCQs
    
    Returns:
        JobResult with all processed slides
    """
    job_logger = get_job_logger(job_id)
    job_logger.info(f"Starting async processing: {ppt_path}")
    
    start_time = datetime.utcnow()
    
    try:
        # Parse PowerPoint
        job_manager.update_progress(job_id, 5, current_step="Parsing presentation")
        
        try:
            all_slides = parse_ppt(ppt_path)
        except Exception as e:
            raise PPTParseError(str(e), Path(ppt_path).name)
        
        # Filter slides with text
        slides = [s for s in all_slides if s["has_text"]][:max_slides]
        total_slides = len(slides)
        
        if total_slides == 0:
            job_logger.warning("No slides with text found")
            result = JobResult(
                job_id=job_id,
                status="completed",
                filename=Path(ppt_path).name,
                language=language,
                slides=[],
                processing_time_seconds=0,
                created_at=start_time,
                completed_at=datetime.utcnow(),
            )
            return result
        
        # Get actual slide numbers for progress tracking
        slide_numbers = [s["slide_number"] for s in slides]
        job_manager.start_processing(job_id, total_slides, slide_numbers)
        job_logger.info(f"Processing {total_slides} slides: {slide_numbers}")
        
        results: list[SlideResult] = []
        video_paths: list[str] = []
        
        # Process each slide
        for idx, slide in enumerate(slides):
            slide_num = slide["slide_number"]
            slide_text = slide["text"]
            
            # Check for cancellation
            job_manager.check_cancellation(job_id)
            
            # Calculate progress
            base_progress = 10 + (idx * 80 // total_slides)
            job_manager.update_progress(
                job_id,
                base_progress,
                current_slide=slide_num,
                current_step=f"Processing slide {slide_num}"
            )
            
            slide_result = SlideResult(
                slide_number=slide_num,
                text=slide_text,
                has_text=True,
            )
            
            try:
                # Generate narration
                job_manager.update_slide_progress(job_id, slide_num, narration=SlideState.PROCESSING)
                job_manager.update_progress(
                    job_id, base_progress + 5,
                    current_step=f"Generating narration for slide {slide_num}"
                )
                
                narration = await generate_narration_async(slide_text, language)
                slide_result.narration = narration
                job_manager.update_slide_progress(job_id, slide_num, narration=SlideState.COMPLETED)
                
                # Generate MCQs
                if generate_mcqs:
                    job_logger.info(f"[MCQ] Starting MCQ generation for slide {slide_num}")
                    job_manager.update_slide_progress(job_id, slide_num, mcq=SlideState.PROCESSING)
                    job_manager.update_progress(
                        job_id, base_progress + 10,
                        current_step=f"Generating MCQs for slide {slide_num}"
                    )
                    # Improved prompt for MCQ generation
                    improved_prompt = (
                        f"Generate at least 3 multiple-choice questions (easy, medium, hard) based on the following slide text. "
                        f"Each question should have 4 options, one correct answer, and a difficulty label. "
                        f"Slide text: {slide_text}\n"
                    )
                    job_logger.info(f"[MCQ] Prompt: {improved_prompt}")
                    qa_raw = await generate_mcqs_async(improved_prompt, language)
                    job_logger.info(f"[MCQ] Raw output: {qa_raw}")
                    validated_qa = validate_and_fix_mcqs(qa_raw)
                    job_logger.info(f"[MCQ] Validated output: {validated_qa}")
                    # Retry if validation fails
                    if not validated_qa["questions"] or not validate_mcq_language(validated_qa, language):
                        job_logger.warning(f"[MCQ] Validation failed, retrying...")
                        qa_raw = await generate_mcqs_async(improved_prompt, language)
                        job_logger.info(f"[MCQ] Raw output (retry): {qa_raw}")
                        validated_qa = validate_and_fix_mcqs(qa_raw)
                        job_logger.info(f"[MCQ] Validated output (retry): {validated_qa}")
                        if not validate_mcq_language(validated_qa, language):
                            job_logger.error(f"[MCQ] MCQ language validation failed after retry.")
                            validated_qa = {"questions": []}
                    # Convert MCQ dicts to MCQuestion objects for each difficulty
                    qa_obj = {}
                    for diff in ["easy", "medium", "hard"]:
                        if validated_qa.get(diff):
                            qa_obj[diff] = [MCQuestion(**q) if not isinstance(q, MCQuestion) else q for q in validated_qa[diff]]
                    slide_result.qa = qa_obj
                    job_logger.info(f"[MCQ] Final MCQ object for slide {slide_num}: {qa_obj}")
                    job_manager.update_slide_progress(job_id, slide_num, mcq=SlideState.COMPLETED)
                
                # Generate video
                if generate_video and narration:
                    job_manager.update_slide_progress(job_id, slide_num, video=SlideState.PROCESSING)
                    job_manager.update_progress(
                        job_id, base_progress + 15,
                        current_step=f"Creating video for slide {slide_num}"
                    )
                    
                    # Run TTS and video assembly in thread pool (they're CPU-bound)
                    loop = asyncio.get_event_loop()
                    
                    audio_path = await loop.run_in_executor(
                        None, synthesize_speech, narration, language
                    )
                    slide_result.audio_path = audio_path
                    
                    image_path = await loop.run_in_executor(
                        None, render_slide_image, slide_text
                    )
                    slide_result.image_path = image_path
                    
                    video_path = await loop.run_in_executor(
                        None, create_video, image_path, audio_path
                    )
                    slide_result.video_path = video_path
                    video_paths.append(video_path)
                    
                    job_manager.update_slide_progress(job_id, slide_num, video=SlideState.COMPLETED)
            
            except JobCancelledError:
                raise
            except Exception as e:
                job_logger.error(f"Error processing slide {slide_num}: {e}")
                job_manager.update_slide_progress(
                    job_id, slide_num,
                    narration=SlideState.FAILED if not slide_result.narration else SlideState.COMPLETED,
                    mcq=SlideState.FAILED if generate_mcqs and not slide_result.qa else SlideState.COMPLETED,
                    video=SlideState.FAILED if generate_video and not slide_result.video_path else SlideState.COMPLETED,
                    error=str(e)
                )
            
            results.append(slide_result)
        
        # Stitch videos
        final_video_path = None
        if generate_video and len(video_paths) > 0:
            job_manager.update_progress(job_id, 95, current_step="Stitching final video")
            
            try:
                loop = asyncio.get_event_loop()
                final_video_path = await loop.run_in_executor(
                    None, stitch_videos, video_paths
                )
                job_logger.info(f"Final video created: {final_video_path}")
            except Exception as e:
                job_logger.error(f"Video stitching failed: {e}")
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Create result
        job_result = JobResult(
            job_id=job_id,
            status="completed",
            filename=Path(ppt_path).name,
            language=language,
            slides=results,
            final_video_path=final_video_path,
            processing_time_seconds=processing_time,
            created_at=start_time,
            completed_at=end_time,
        )
        
        job_logger.info(f"Processing completed in {processing_time:.2f}s")
        return job_result
    
    except JobCancelledError:
        job_logger.info("Job was cancelled")
        raise
    except Exception as e:
        job_logger.error(f"Processing failed: {e}")
        raise


async def run_processing_job(
    job_id: str,
    ppt_path: str,
    language: str,
    max_slides: int,
    generate_video: bool,
    generate_mcqs: bool,
) -> None:
    """
    Run a processing job in the background.
    
    This is the entry point for background task execution.
    """
    try:
        result = await process_ppt_async(
            job_id=job_id,
            ppt_path=ppt_path,
            language=language,
            max_slides=max_slides,
            generate_video=generate_video,
            generate_mcqs=generate_mcqs,
        )
        
        job_manager.complete_job(job_id, result)
        
    except JobCancelledError:
        # Already handled by job manager
        pass
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


# Keep sync version for backward compatibility
def process_ppt(ppt_path: str, language: str = "en", max_slides: int = 5) -> list[dict]:
    """
    Synchronous PPT processing (legacy support).
    
    For new code, use process_ppt_async instead.
    """
    logger.info(f"Processing PPT synchronously: {ppt_path}")
    
    all_slides = parse_ppt(ppt_path)
    slides = [s for s in all_slides if s["has_text"]][:max_slides]
    results = []
    
    for slide in slides:
        slide_num = slide["slide_number"]
        slide_text = slide["text"]
        
        logger.info(f"Processing slide {slide_num}")
        
        slide_result = {
            "slide_number": slide_num,
            "text": slide_text,
            "has_text": True,
            "narration": None,
            "qa": None,
            "audio": None,
            "video": None,
        }
        
        try:
            # Narration
            narration = generate_narration_sync(slide_text, language)
            slide_result["narration"] = narration
            
            # TTS & Video
            audio_path = synthesize_speech(narration, language)
            image_path = render_slide_image(slide_text)
            video_path = create_video(image_path, audio_path)
            
            slide_result["audio"] = audio_path
            slide_result["video"] = video_path
            
            # MCQs
            qa_raw = generate_mcqs_sync(slide_text, language)
            validated_qa = validate_and_fix_mcqs(qa_raw)
            
            if not validated_qa["questions"] or not validate_mcq_language(validated_qa, language):
                qa_raw = generate_mcqs_sync(slide_text, language)
                validated_qa = validate_and_fix_mcqs(qa_raw)
                
                if not validate_mcq_language(validated_qa, language):
                    validated_qa = {"questions": []}
            
            slide_result["qa"] = validated_qa
            
        except Exception as e:
            logger.error(f"Error processing slide {slide_num}: {e}")
        
        results.append(slide_result)
    
    return results
