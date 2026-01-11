'use client';

import { Download, FileVideo, FileAudio, FileText, FileJson } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { downloadFile, JobResult } from '@/lib/api';

interface DownloadPanelProps {
  result: JobResult;
}

interface DownloadItem {
  type: string;
  label: string;
  description: string;
  icon: React.ElementType;
  available: boolean;
}

export function DownloadPanel({ result }: DownloadPanelProps) {
  const hasVideo = !!result.final_video_path;
  const hasAudio = result.slides.some((s) => s.audio_path);
  const hasMcqs = result.slides.some((s) => s.mcqs && s.mcqs.length > 0);

  const downloadItems: DownloadItem[] = [
    {
      type: 'video',
      label: 'Final Video',
      description: 'Complete video lecture with narration',
      icon: FileVideo,
      available: hasVideo,
    },
    {
      type: 'audio_zip',
      label: 'All Audio Files',
      description: 'ZIP archive of individual narration audio',
      icon: FileAudio,
      available: hasAudio,
    },
    {
      type: 'narrations',
      label: 'Narration Scripts',
      description: 'All slide narrations as text file',
      icon: FileText,
      available: true,
    },
    {
      type: 'mcqs_json',
      label: 'Quiz Questions (JSON)',
      description: 'MCQ questions in JSON format',
      icon: FileJson,
      available: hasMcqs,
    },
    {
      type: 'summary',
      label: 'Processing Summary',
      description: 'Complete processing results as JSON',
      icon: FileJson,
      available: true,
    },
  ];

  const handleDownload = async (fileType: string, filename: string) => {
    try {
      const blob = await downloadFile(result.job_id, fileType);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Download className="h-5 w-5" />
          Export & Download
        </CardTitle>
        <CardDescription>
          Download generated content in various formats
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2">
          {downloadItems.map((item) => (
            <div
              key={item.type}
              className={`flex items-start gap-4 p-4 rounded-lg border ${
                item.available ? '' : 'opacity-50'
              }`}
            >
              <div className="p-2 bg-primary/10 rounded-lg">
                <item.icon className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-medium">{item.label}</h4>
                <p className="text-sm text-muted-foreground">
                  {item.description}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  disabled={!item.available}
                  onClick={() =>
                    handleDownload(item.type, `${result.filename}_${item.type}`)
                  }
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
