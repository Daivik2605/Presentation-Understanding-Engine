import Link from 'next/link';
import { ArrowRight, FileText, Video, Brain, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5" />
        
        <div className="container mx-auto relative">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              Transform Presentations into{' '}
              <span className="text-primary">Learning Experiences</span>
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8">
              AI-powered engine that converts PowerPoint files into narrated videos 
              and interactive quizzes. Perfect for EdTech, training, and education.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/upload">
                <Button size="lg" className="gap-2">
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/docs">
                <Button size="lg" variant="outline">
                  View Documentation
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Powerful Features
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              icon={<FileText className="h-8 w-8" />}
              title="Smart Parsing"
              description="Extracts and understands slide content with semantic analysis"
            />
            <FeatureCard
              icon={<Brain className="h-8 w-8" />}
              title="AI Narration"
              description="Generates teacher-style explanations using advanced LLMs"
            />
            <FeatureCard
              icon={<Video className="h-8 w-8" />}
              title="Video Generation"
              description="Creates complete video lectures with TTS audio"
            />
            <FeatureCard
              icon={<Globe className="h-8 w-8" />}
              title="Multilingual"
              description="Supports English, French, and Hindi outputs"
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            How It Works
          </h2>
          
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <StepCard
                number={1}
                title="Upload"
                description="Upload your .pptx file and select language preferences"
              />
              <StepCard
                number={2}
                title="Process"
                description="AI analyzes slides and generates narration & questions"
              />
              <StepCard
                number={3}
                title="Download"
                description="Get your video lecture and interactive MCQ quiz"
              />
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-primary text-primary-foreground">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Transform Your Presentations?
          </h2>
          <p className="text-lg mb-8 opacity-90">
            Start creating engaging educational content in minutes.
          </p>
          <Link href="/upload">
            <Button size="lg" variant="secondary" className="gap-2">
              Upload Your First Presentation
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="p-6 rounded-lg border bg-card">
      <div className="text-primary mb-4">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}

function StepCard({
  number,
  title,
  description,
}: {
  number: number;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}
