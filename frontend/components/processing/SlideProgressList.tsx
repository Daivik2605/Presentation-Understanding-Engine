'use client';

import { CheckCircle, Loader2, Clock, XCircle, FileText, HelpCircle, Video } from 'lucide-react';

import { cn } from '@/lib/utils';
import { SlideProgress } from '@/lib/api';

interface SlideProgressListProps {
  slides: SlideProgress[];
}

export function SlideProgressList({ slides }: SlideProgressListProps) {
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium">Slide Progress</h4>
      <div className="space-y-2">
        {slides.map((slide) => (
          <SlideProgressItem key={slide.slide_number} slide={slide} />
        ))}
      </div>
    </div>
  );
}

function getStepIcon(state: string) {
  switch (state) {
    case 'completed':
      return <CheckCircle className="h-3 w-3 text-green-500" />;
    case 'processing':
      return <Loader2 className="h-3 w-3 animate-spin text-primary" />;
    case 'failed':
      return <XCircle className="h-3 w-3 text-destructive" />;
    default:
      return <Clock className="h-3 w-3 text-muted-foreground" />;
  }
}

function SlideProgressItem({ slide }: { slide: SlideProgress }) {
  // Determine overall slide status
  const getOverallStatus = () => {
    if (slide.error) return 'failed';
    if (slide.narration === 'failed' || slide.mcq === 'failed' || slide.video === 'failed') return 'failed';
    if (slide.video === 'completed') return 'completed';
    if (slide.narration === 'processing' || slide.mcq === 'processing' || slide.video === 'processing') return 'processing';
    if (slide.narration === 'completed' || slide.mcq === 'completed') return 'processing'; // Still working
    return 'pending';
  };

  const overallStatus = getOverallStatus();
  
  const getStatusIcon = () => {
    switch (overallStatus) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-destructive" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getCurrentStep = () => {
    if (slide.video === 'processing') return 'Creating video...';
    if (slide.video === 'completed') return 'Done';
    if (slide.mcq === 'processing') return 'Generating MCQs...';
    if (slide.narration === 'processing') return 'Generating narration...';
    if (slide.narration === 'completed' && slide.video === 'pending') return 'Creating audio...';
    return 'Waiting...';
  };

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg border',
        overallStatus === 'processing' && 'border-primary bg-primary/5',
        overallStatus === 'completed' && 'border-green-500/30 bg-green-500/5',
        overallStatus === 'failed' && 'border-destructive/30 bg-destructive/5'
      )}
    >
      {getStatusIcon()}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium">Slide {slide.slide_number}</p>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1" title="Narration">
              <FileText className="h-3 w-3" />
              {getStepIcon(slide.narration)}
            </span>
            <span className="flex items-center gap-1" title="MCQs">
              <HelpCircle className="h-3 w-3" />
              {getStepIcon(slide.mcq)}
            </span>
            <span className="flex items-center gap-1" title="Video">
              <Video className="h-3 w-3" />
              {getStepIcon(slide.video)}
            </span>
          </div>
        </div>
        <p className="text-xs text-muted-foreground truncate">
          {getCurrentStep()}
        </p>
        {slide.error && (
          <p className="text-xs text-destructive truncate">{slide.error}</p>
        )}
      </div>
    </div>
  );
}
