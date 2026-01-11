'use client';

import { Slider } from '@/components/ui/slider';

interface SlideSliderProps {
  value: number;
  onChange: (value: number) => void;
}

export function SlideSlider({ value, onChange }: SlideSliderProps) {
  return (
    <div className="space-y-2">
      <Slider
        value={[value]}
        onValueChange={(values) => onChange(values[0])}
        min={1}
        max={20}
        step={1}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>1</span>
        <span>20</span>
      </div>
    </div>
  );
}
