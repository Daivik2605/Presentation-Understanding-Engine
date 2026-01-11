'use client';

import { cn } from '@/lib/utils';

interface LanguageSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const languages = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'fr', label: 'French', flag: '🇫🇷' },
  { code: 'hi', label: 'Hindi', flag: '🇮🇳' },
];

export function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  return (
    <div className="grid grid-cols-3 gap-3">
      {languages.map((lang) => (
        <button
          key={lang.code}
          type="button"
          onClick={() => onChange(lang.code)}
          className={cn(
            'flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-colors',
            value === lang.code
              ? 'border-primary bg-primary/5'
              : 'border-muted hover:border-primary/50'
          )}
        >
          <span className="text-2xl">{lang.flag}</span>
          <span className="text-sm font-medium">{lang.label}</span>
        </button>
      ))}
    </div>
  );
}
