# 🚀 Presentation Understanding Engine - Implementation Plan

## Table of Contents
1. [Project Overview](#project-overview)
2. [Phase 1: Backend Improvements](#phase-1-backend-improvements)
3. [Phase 2: Modern Frontend with Next.js](#phase-2-modern-frontend-with-nextjs)
4. [Phase 3: Advanced Features](#phase-3-advanced-features)
5. [Phase 4: Production Readiness](#phase-4-production-readiness)
6. [Technical Architecture](#technical-architecture)
7. [Timeline & Milestones](#timeline--milestones)

---

## Project Overview

### Current State
- FastAPI backend with PPT processing
- LLM-powered narration and MCQ generation
- Basic video generation pipeline
- No frontend UI

### Target State
- Robust, scalable backend with async processing
- Modern Next.js + Tailwind CSS frontend
- Real-time progress tracking
- Production-ready deployment

---

## Phase 1: Backend Improvements

### 1.1 Async LLM Processing
**Priority:** High | **Effort:** Medium

```python
# Current (blocking)
narration = narration_chain.invoke({"slide_text": text})

# Target (async)
narration = await narration_chain.ainvoke({"slide_text": text})
```

**Implementation:**
- [ ] Convert `narration_chain` to async with `ainvoke()`
- [ ] Convert `qa_chain` to async with `ainvoke()`
- [ ] Update `ppt_processor.py` to use `async def process_ppt()`
- [ ] Update `ppt_video_processor.py` to use `async def process_ppt_to_video()`
- [ ] Add connection pooling for Ollama

**Files to modify:**
- `app/services/narration_chain.py`
- `app/services/qa_chain.py`
- `app/services/ppt_processor.py`
- `app/services/ppt_video_processor.py`

---

### 1.2 Background Task Processing
**Priority:** High | **Effort:** Medium

**Implementation:**
- [ ] Create job queue system with Redis/Celery or FastAPI BackgroundTasks
- [ ] Add job status tracking (pending, processing, completed, failed)
- [ ] Create `/jobs/{job_id}/status` endpoint
- [ ] Return job_id immediately on upload, poll for results

**New files:**
```
app/
├── services/
│   └── job_manager.py      # Job queue management
├── api/
│   └── jobs.py             # Job status endpoints
└── models/
    └── job.py              # Job status models
```

**API Changes:**
```python
# POST /process-ppt → Returns immediately
{"job_id": "abc123", "status": "pending"}

# GET /jobs/abc123/status → Poll for progress
{"job_id": "abc123", "status": "processing", "progress": 45, "current_slide": 2}

# GET /jobs/abc123/result → Get final result
{"slides": [...], "final_video_path": "..."}
```

---

### 1.3 WebSocket Progress Streaming
**Priority:** Medium | **Effort:** Medium

**Implementation:**
- [ ] Add WebSocket endpoint `/ws/jobs/{job_id}`
- [ ] Stream real-time progress updates
- [ ] Include slide-by-slide completion events

**New endpoint:**
```python
@router.websocket("/ws/jobs/{job_id}")
async def job_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()
    while job_in_progress(job_id):
        progress = get_job_progress(job_id)
        await websocket.send_json(progress)
        await asyncio.sleep(0.5)
```

---

### 1.4 Proper Logging System
**Priority:** High | **Effort:** Low

**Implementation:**
- [ ] Replace all `print()` with `logging` module
- [ ] Add structured JSON logging
- [ ] Configure log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Add request ID tracking for traceability

**New file:** `app/core/logging.py`
```python
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
```

---

### 1.5 Configuration Management
**Priority:** High | **Effort:** Low

**Implementation:**
- [ ] Create `app/core/config.py` with Pydantic Settings
- [ ] Move all hardcoded values to environment variables
- [ ] Add `.env.example` file

**New file:** `app/core/config.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM Settings
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434"
    narration_temperature: float = 0.4
    qa_temperature: float = 0.3
    
    # TTS Settings
    tts_voice_en: str = "en-US-AriaNeural"
    tts_voice_fr: str = "fr-FR-DeniseNeural"
    tts_voice_hi: str = "hi-IN-SwaraNeural"
    
    # Video Settings
    video_width: int = 1280
    video_height: int = 720
    video_fps: int = 30
    
    # Storage
    upload_dir: str = "data/uploads"
    audio_dir: str = "data/audio"
    video_dir: str = "data/videos"
    
    # Limits
    max_slides: int = 10
    max_file_size_mb: int = 50
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

### 1.6 Error Handling & Recovery
**Priority:** High | **Effort:** Medium

**Implementation:**
- [ ] Create custom exception classes
- [ ] Add global exception handler
- [ ] Implement retry logic for LLM/TTS/FFmpeg failures
- [ ] Add circuit breaker for external services

**New file:** `app/core/exceptions.py`
```python
class PPTProcessingError(Exception):
    """Base exception for PPT processing"""
    pass

class LLMGenerationError(PPTProcessingError):
    """LLM failed to generate content"""
    pass

class TTSError(PPTProcessingError):
    """Text-to-speech conversion failed"""
    pass

class VideoAssemblyError(PPTProcessingError):
    """Video creation/stitching failed"""
    pass
```

---

### 1.7 File Cleanup & Storage Management
**Priority:** Medium | **Effort:** Low

**Implementation:**
- [ ] Add temp file cleanup after processing
- [ ] Implement file retention policy (delete after X days)
- [ ] Add storage usage monitoring
- [ ] Create cleanup background task

```python
async def cleanup_old_files(max_age_hours: int = 24):
    """Delete files older than max_age_hours"""
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    for dir in [AUDIO_DIR, VIDEO_DIR, IMAGE_DIR]:
        for file in dir.glob("*"):
            if file.stat().st_mtime < cutoff.timestamp():
                file.unlink()
```

---

### 1.8 Caching Layer
**Priority:** Medium | **Effort:** Medium

**Implementation:**
- [ ] Add Redis for caching
- [ ] Cache narrations by content hash
- [ ] Cache MCQs by content hash
- [ ] Add cache invalidation strategy

```python
import hashlib
from functools import lru_cache

def get_content_hash(text: str, language: str) -> str:
    return hashlib.sha256(f"{text}:{language}".encode()).hexdigest()[:16]

async def get_narration_cached(text: str, language: str) -> str:
    cache_key = f"narration:{get_content_hash(text, language)}"
    cached = await redis.get(cache_key)
    if cached:
        return cached
    narration = await generate_narration(text, language)
    await redis.set(cache_key, narration, ex=86400)  # 24h TTL
    return narration
```

---

### 1.9 Rate Limiting
**Priority:** Medium | **Effort:** Low

**Implementation:**
- [ ] Add slowapi for rate limiting
- [ ] Configure per-IP and per-endpoint limits
- [ ] Add rate limit headers to responses

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/process-ppt")
@limiter.limit("5/minute")
async def process_ppt_endpoint(...):
    ...
```

---

### 1.10 Input Validation & Security
**Priority:** High | **Effort:** Low

**Implementation:**
- [ ] Validate file magic bytes (not just extension)
- [ ] Add file size limits
- [ ] Sanitize filenames
- [ ] Add CORS configuration
- [ ] Implement API key authentication

```python
import magic

def validate_pptx(file_content: bytes) -> bool:
    mime = magic.from_buffer(file_content, mime=True)
    return mime == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
```

---

## Phase 2: Modern Frontend with Next.js

### 2.1 Project Setup
**Stack:** Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui

**Directory Structure:**
```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   ├── upload/
│   │   └── page.tsx             # Upload page
│   ├── processing/
│   │   └── [jobId]/
│   │       └── page.tsx         # Processing status page
│   ├── results/
│   │   └── [jobId]/
│   │       └── page.tsx         # Results page
│   └── api/                     # API routes (BFF pattern)
│       └── proxy/
│           └── [...path]/
│               └── route.ts
├── components/
│   ├── ui/                      # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── progress.tsx
│   │   ├── tabs.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Sidebar.tsx
│   ├── upload/
│   │   ├── DropZone.tsx
│   │   ├── FilePreview.tsx
│   │   └── UploadForm.tsx
│   ├── processing/
│   │   ├── ProgressTracker.tsx
│   │   ├── SlideProgress.tsx
│   │   └── LiveStatus.tsx
│   ├── results/
│   │   ├── SlideViewer.tsx
│   │   ├── NarrationPlayer.tsx
│   │   ├── MCQDisplay.tsx
│   │   ├── VideoPlayer.tsx
│   │   └── DownloadPanel.tsx
│   └── shared/
│       ├── LanguageSelector.tsx
│       └── LoadingSpinner.tsx
├── hooks/
│   ├── useUpload.ts
│   ├── useJobStatus.ts
│   ├── useWebSocket.ts
│   └── useResults.ts
├── lib/
│   ├── api.ts                   # API client
│   ├── utils.ts                 # Utility functions
│   └── constants.ts
├── types/
│   ├── api.ts                   # API response types
│   └── index.ts
├── styles/
│   └── globals.css
├── public/
│   └── ...
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

---

### 2.2 Setup Commands

```bash
# Create Next.js project
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir=false

cd frontend

# Install dependencies
npm install @tanstack/react-query axios framer-motion lucide-react
npm install react-dropzone react-hot-toast
npm install -D @types/node

# Setup shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card progress tabs badge dialog
npx shadcn-ui@latest add input label select slider toast
```

---

### 2.3 Core Pages & Components

#### 2.3.1 Home Page (`app/page.tsx`)
```tsx
// Hero section with animated background
// Feature highlights
// Quick start CTA → Upload page
// Recent processing history (if logged in)
```

#### 2.3.2 Upload Page (`app/upload/page.tsx`)
**Features:**
- Drag & drop file upload zone
- File type validation (.pptx only)
- File size indicator
- Language selector (EN/FR/HI)
- Max slides slider (1-10)
- Upload progress bar
- Submit button with loading state

**Wireframe:**
```
┌────────────────────────────────────────────────────────┐
│  📤 Upload Your Presentation                           │
├────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │                                                  │  │
│  │     📁 Drag & drop your .pptx file here         │  │
│  │         or click to browse                      │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  📄 selected-file.pptx (2.4 MB)              ✕ Remove │
│                                                        │
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Language: [EN▾] │  │ Max Slides: ◯────●──── 5    │  │
│  └─────────────────┘  └─────────────────────────────┘  │
│                                                        │
│  ☐ Generate Video    ☐ Generate MCQs                  │
│                                                        │
│           [ 🚀 Start Processing ]                      │
└────────────────────────────────────────────────────────┘
```

#### 2.3.3 Processing Page (`app/processing/[jobId]/page.tsx`)
**Features:**
- Real-time progress via WebSocket
- Slide-by-slide progress cards
- Current step indicator (Parsing → Narrating → TTS → Video)
- Estimated time remaining
- Cancel button
- Auto-redirect to results on completion

**Wireframe:**
```
┌────────────────────────────────────────────────────────┐
│  ⚙️ Processing: lecture.pptx                          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Overall Progress                                      │
│  ████████████████░░░░░░░░░░░░░░  45%                  │
│                                                        │
│  Current Step: Generating narration for Slide 3...    │
│  Estimated Time: ~2 minutes remaining                 │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Slide Progress                                   │  │
│  ├─────────────────────────────────────────────────┤  │
│  │ ✅ Slide 1  │ Narration ✓ │ MCQ ✓ │ Video ✓    │  │
│  │ ✅ Slide 2  │ Narration ✓ │ MCQ ✓ │ Video ✓    │  │
│  │ 🔄 Slide 3  │ Narration ⏳│ MCQ ○ │ Video ○    │  │
│  │ ○  Slide 4  │ Narration ○ │ MCQ ○ │ Video ○    │  │
│  │ ○  Slide 5  │ Narration ○ │ MCQ ○ │ Video ○    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│           [ Cancel Processing ]                        │
└────────────────────────────────────────────────────────┘
```

#### 2.3.4 Results Page (`app/results/[jobId]/page.tsx`)
**Features:**
- Tabbed interface (Slides | Video | MCQs | Downloads)
- Slide carousel with text + narration
- Audio player for each slide
- Video player for final video
- Interactive MCQ quiz mode
- Download buttons (PDF, Audio, Video, JSON)

**Wireframe:**
```
┌────────────────────────────────────────────────────────┐
│  ✅ Results: lecture.pptx                    [↓ Download]│
├────────────────────────────────────────────────────────┤
│  [ Slides ]  [ Video ]  [ Quiz ]  [ Export ]          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ◀  Slide 2 of 5  ▶                             │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │                                          │   │  │
│  │  │     [Slide Image/Text Preview]           │   │  │
│  │  │                                          │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  📖 Narration:                                  │  │
│  │  "In this slide, we explore the concept of..."  │  │
│  │                                                  │  │
│  │  🔊 ▶────────●────────── 0:45 / 1:23           │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  Slide Thumbnails:                                    │
│  [1] [2] [3] [4] [5]                                  │
└────────────────────────────────────────────────────────┘
```

---

### 2.4 API Client (`lib/api.ts`)

```typescript
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export interface UploadOptions {
  file: File;
  language: 'en' | 'fr' | 'hi';
  maxSlides: number;
  generateVideo: boolean;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_slide?: number;
  total_slides?: number;
  current_step?: string;
  error?: string;
}

export interface ProcessingResult {
  filename: string;
  language: string;
  slides: SlideResult[];
  final_video_path?: string;
}

export interface SlideResult {
  slide_number: number;
  text: string;
  narration: string;
  qa: { questions: MCQuestion[] };
  audio_path?: string;
  video_path?: string;
}

export interface MCQuestion {
  question: string;
  options: string[];
  answer: string;
  difficulty: 'easy' | 'medium';
}

// API Functions
export const uploadPresentation = async (options: UploadOptions): Promise<{ job_id: string }> => {
  const formData = new FormData();
  formData.append('file', options.file);
  formData.append('language', options.language);
  formData.append('max_slides', String(options.maxSlides));
  
  const endpoint = options.generateVideo ? '/process-ppt-video' : '/process-ppt';
  const response = await api.post(endpoint, formData);
  return response.data;
};

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await api.get(`/jobs/${jobId}/status`);
  return response.data;
};

export const getJobResult = async (jobId: string): Promise<ProcessingResult> => {
  const response = await api.get(`/jobs/${jobId}/result`);
  return response.data;
};

export const downloadFile = async (path: string): Promise<Blob> => {
  const response = await api.get(`/download`, {
    params: { path },
    responseType: 'blob',
  });
  return response.data;
};
```

---

### 2.5 WebSocket Hook (`hooks/useWebSocket.ts`)

```typescript
import { useEffect, useState, useCallback } from 'react';

export interface WSMessage {
  type: 'progress' | 'completed' | 'error';
  data: {
    progress: number;
    current_slide?: number;
    current_step?: string;
    result?: any;
    error?: string;
  };
}

export function useJobWebSocket(jobId: string | null) {
  const [status, setStatus] = useState<WSMessage['data'] | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/jobs/${jobId}`);

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setError('WebSocket connection failed');
    
    ws.onmessage = (event) => {
      const message: WSMessage = JSON.parse(event.data);
      setStatus(message.data);
      
      if (message.type === 'error') {
        setError(message.data.error || 'Processing failed');
      }
    };

    return () => ws.close();
  }, [jobId]);

  return { status, isConnected, error };
}
```

---

### 2.6 UI Components

#### DropZone Component
```tsx
// components/upload/DropZone.tsx
'use client';

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DropZoneProps {
  file: File | null;
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
}

export function DropZone({ file, onFileSelect, onFileRemove }: DropZoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles[0]) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  if (file) {
    return (
      <div className="flex items-center justify-between p-4 border rounded-lg bg-muted">
        <div className="flex items-center gap-3">
          <FileText className="h-8 w-8 text-primary" />
          <div>
            <p className="font-medium">{file.name}</p>
            <p className="text-sm text-muted-foreground">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        </div>
        <button onClick={onFileRemove} className="p-2 hover:bg-destructive/10 rounded">
          <X className="h-5 w-5 text-destructive" />
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors",
        isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
      )}
    >
      <input {...getInputProps()} />
      <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
      <p className="text-lg font-medium">
        {isDragActive ? "Drop your file here" : "Drag & drop your .pptx file"}
      </p>
      <p className="text-sm text-muted-foreground mt-2">
        or click to browse (max 50MB)
      </p>
    </div>
  );
}
```

#### Progress Tracker Component
```tsx
// components/processing/ProgressTracker.tsx
'use client';

import { Progress } from '@/components/ui/progress';
import { CheckCircle, Circle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SlideProgress {
  slide_number: number;
  narration: 'pending' | 'processing' | 'completed';
  mcq: 'pending' | 'processing' | 'completed';
  video: 'pending' | 'processing' | 'completed';
}

interface ProgressTrackerProps {
  overallProgress: number;
  currentStep: string;
  slides: SlideProgress[];
}

export function ProgressTracker({ overallProgress, currentStep, slides }: ProgressTrackerProps) {
  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Overall Progress</span>
          <span>{overallProgress}%</span>
        </div>
        <Progress value={overallProgress} className="h-3" />
        <p className="text-sm text-muted-foreground">{currentStep}</p>
      </div>

      {/* Slide-by-slide Progress */}
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-muted px-4 py-2 font-medium">Slide Progress</div>
        <div className="divide-y">
          {slides.map((slide) => (
            <div key={slide.slide_number} className="flex items-center px-4 py-3 gap-4">
              <span className="w-20">Slide {slide.slide_number}</span>
              <StatusIcon status={slide.narration} label="Narration" />
              <StatusIcon status={slide.mcq} label="MCQ" />
              <StatusIcon status={slide.video} label="Video" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatusIcon({ status, label }: { status: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5 text-sm">
      {status === 'completed' && <CheckCircle className="h-4 w-4 text-green-500" />}
      {status === 'processing' && <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />}
      {status === 'pending' && <Circle className="h-4 w-4 text-muted-foreground" />}
      <span className={cn(
        status === 'completed' && 'text-green-600',
        status === 'processing' && 'text-blue-600',
        status === 'pending' && 'text-muted-foreground'
      )}>
        {label}
      </span>
    </div>
  );
}
```

---

### 2.7 Tailwind Configuration

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "pulse-slow": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.5 },
        },
      },
      animation: {
        "pulse-slow": "pulse-slow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## Phase 3: Advanced Features

### 3.1 PDF Support
- [ ] Add PyMuPDF for PDF parsing
- [ ] Extract text and images from PDF slides
- [ ] Unified parser interface for PPT and PDF

### 3.2 Actual Slide Image Extraction
- [ ] Use `python-pptx` to render actual slides as images
- [ ] Or use LibreOffice headless mode for conversion
- [ ] Fall back to text rendering if extraction fails

### 3.3 Speaker Notes Parsing
- [ ] Extract speaker notes from PPTX
- [ ] Include notes in narration context
- [ ] Option to use notes as narration base

### 3.4 Custom Difficulty Levels
- [ ] Add difficulty parameter to API
- [ ] Modify QA prompt for difficulty control
- [ ] Generate mixed difficulty sets

### 3.5 Multiple LLM Provider Support
- [ ] Abstract LLM layer
- [ ] Add OpenAI support
- [ ] Add Anthropic support
- [ ] Add Azure OpenAI support
- [ ] Configuration-based provider selection

### 3.6 Quiz Mode
- [ ] Interactive quiz component in frontend
- [ ] Score tracking
- [ ] Timed quiz option
- [ ] Results summary with correct answers

---

## Phase 4: Production Readiness

### 4.1 Docker Containerization

```dockerfile
# Dockerfile (Backend)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  ollama_data:
```

### 4.2 Database Integration
- [ ] Add PostgreSQL for job persistence
- [ ] Store processing history
- [ ] User accounts and authentication
- [ ] Usage analytics

### 4.3 Monitoring & Observability
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Health check endpoints
- [ ] Distributed tracing with OpenTelemetry

### 4.4 CI/CD Pipeline
- [ ] GitHub Actions workflow
- [ ] Automated testing
- [ ] Docker image builds
- [ ] Deployment to cloud (AWS/GCP/Azure)

---

## Technical Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Upload    │  │  Progress   │  │   Results   │  │    Quiz     │        │
│  │    Page     │  │    Page     │  │    Page     │  │    Mode     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────────────┘        │
│         │                │                │                                 │
│         │    REST API    │   WebSocket    │    REST API                    │
└─────────┼────────────────┼────────────────┼─────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           API Layer                                  │   │
│  │  POST /process-ppt  │  GET /jobs/{id}  │  WS /ws/jobs/{id}         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐   │
│  │                         Job Manager                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │  Queue   │  │ Worker   │  │  Status  │  │  Cache   │            │   │
│  │  │ (Redis)  │  │  Pool    │  │ Tracker  │  │ (Redis)  │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐   │
│  │                        Processing Pipeline                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │   PPT    │  │Narration │  │    QA    │  │  Video   │            │   │
│  │  │  Parser  │──▶│  Chain   │──▶│  Chain   │──▶│ Assembly │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐      │
│  │   Ollama    │           │  Edge-TTS   │           │   FFmpeg    │      │
│  │  (LLM API)  │           │   (Audio)   │           │   (Video)   │      │
│  └─────────────┘           └─────────────┘           └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Timeline & Milestones

### Sprint 1 (Week 1-2): Backend Foundation
- [x] Fix existing bugs
- [ ] Implement async processing
- [ ] Add logging system
- [ ] Add configuration management
- [ ] Add error handling

### Sprint 2 (Week 3-4): Background Processing
- [ ] Implement job queue
- [ ] Add job status endpoints
- [ ] Add WebSocket progress
- [ ] Add file cleanup

### Sprint 3 (Week 5-6): Frontend Setup
- [ ] Create Next.js project
- [ ] Setup Tailwind + shadcn/ui
- [ ] Build upload page
- [ ] Build processing page

### Sprint 4 (Week 7-8): Frontend Complete
- [ ] Build results page
- [ ] Add video player
- [ ] Add quiz mode
- [ ] API integration

### Sprint 5 (Week 9-10): Polish & Deploy
- [ ] Docker setup
- [ ] CI/CD pipeline
- [ ] Documentation
- [ ] Performance optimization

---

## Quick Start Commands

### Backend
```bash
cd Presentation-Understanding-Engine
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up --build
```

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [LangChain](https://python.langchain.com/)
- [Ollama](https://ollama.ai/)
