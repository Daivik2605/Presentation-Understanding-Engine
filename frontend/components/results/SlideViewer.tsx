'use client';

import { useState } from 'react';
import { ChevronLeft, ChevronRight, PlayCircle, Volume2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getFileUrl, SlideResult } from '@/lib/api';

interface SlideViewerProps {
  slides: SlideResult[];
}

export function SlideViewer({ slides }: SlideViewerProps) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slide = slides[currentSlide];

  const goToPrevious = () => {
    setCurrentSlide((prev) => Math.max(0, prev - 1));
  };

  const goToNext = () => {
    setCurrentSlide((prev) => Math.min(slides.length - 1, prev + 1));
  };

  const playNarration = () => {
    if (slide.audio_path) {
      const audio = new Audio(getFileUrl(slide.audio_path));
      audio.play();
    }
  };

  return (
    <div className="space-y-4">
      {/* Slide Display */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">
              Slide {currentSlide + 1}: {slide.title || 'Untitled'}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={goToPrevious}
                disabled={currentSlide === 0}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm text-muted-foreground">
                {currentSlide + 1} / {slides.length}
              </span>
              <Button
                variant="outline"
                size="icon"
                onClick={goToNext}
                disabled={currentSlide === slides.length - 1}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Slide Image */}
          {slide.image_path && (
            <div className="aspect-video bg-muted rounded-lg overflow-hidden">
              <img
                src={getFileUrl(slide.image_path)}
                alt={`Slide ${currentSlide + 1}`}
                className="w-full h-full object-contain"
              />
            </div>
          )}

          {/* Content */}
          <div className="space-y-2">
            <h4 className="font-medium">Content</h4>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {slide.text || 'No text content'}
            </p>
          </div>

          {/* Narration */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Narration</h4>
              {slide.audio_path && (
                <Button variant="ghost" size="sm" onClick={playNarration}>
                  <Volume2 className="h-4 w-4 mr-2" />
                  Play Audio
                </Button>
              )}
            </div>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {slide.narration || 'No narration generated'}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Slide Thumbnails */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {slides.map((s, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`flex-shrink-0 w-20 h-14 rounded border-2 overflow-hidden ${
              index === currentSlide
                ? 'border-primary'
                : 'border-transparent opacity-60 hover:opacity-100'
            }`}
          >
            {s.image_path ? (
              <img
                src={getFileUrl(s.image_path)}
                alt={`Thumbnail ${index + 1}`}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-muted flex items-center justify-center text-xs">
                {index + 1}
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
