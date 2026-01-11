'use client';

import { useState } from 'react';
import { CheckCircle, XCircle, ChevronLeft, ChevronRight, Trophy } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { SlideResult, MCQ } from '@/lib/api';

interface QuizModeProps {
  slides: SlideResult[];
}

interface Answer {
  questionIndex: number;
  selectedOption: string;
  isCorrect: boolean;
}

export function QuizMode({ slides }: QuizModeProps) {
  // Flatten MCQs from all slides (qa has easy/medium/hard categories)
  const allMcqs: { slideNumber: number; mcq: MCQ; difficulty: string }[] = slides.flatMap((slide) => {
    if (!slide.qa) return [];
    const mcqs: { slideNumber: number; mcq: MCQ; difficulty: string }[] = [];
    
    if (slide.qa.easy) {
      mcqs.push(...slide.qa.easy.map((mcq) => ({ slideNumber: slide.slide_number, mcq, difficulty: 'easy' })));
    }
    if (slide.qa.medium) {
      mcqs.push(...slide.qa.medium.map((mcq) => ({ slideNumber: slide.slide_number, mcq, difficulty: 'medium' })));
    }
    if (slide.qa.hard) {
      mcqs.push(...slide.qa.hard.map((mcq) => ({ slideNumber: slide.slide_number, mcq, difficulty: 'hard' })));
    }
    
    return mcqs;
  });

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);

  if (allMcqs.length === 0) {
    return (
      <Card>
        <CardContent className="py-10 text-center">
          <p className="text-muted-foreground">
            No quiz questions were generated for this presentation.
          </p>
        </CardContent>
      </Card>
    );
  }

  const current = allMcqs[currentQuestion];
  const isLastQuestion = currentQuestion === allMcqs.length - 1;
  const correctCount = answers.filter((a) => a.isCorrect).length;

  const handleOptionSelect = (option: string) => {
    if (showResult) return;
    setSelectedOption(option);
  };

  const handleSubmit = () => {
    if (!selectedOption) return;

    const isCorrect = selectedOption === current.mcq.answer;  // Backend uses 'answer'
    setAnswers([
      ...answers,
      { questionIndex: currentQuestion, selectedOption, isCorrect },
    ]);
    setShowResult(true);
  };

  const handleNext = () => {
    if (isLastQuestion) {
      setQuizCompleted(true);
    } else {
      setCurrentQuestion((prev) => prev + 1);
      setSelectedOption(null);
      setShowResult(false);
    }
  };

  const handleRestart = () => {
    setCurrentQuestion(0);
    setAnswers([]);
    setSelectedOption(null);
    setShowResult(false);
    setQuizCompleted(false);
  };

  if (quizCompleted) {
    const score = (correctCount / allMcqs.length) * 100;

    return (
      <Card>
        <CardContent className="py-10 text-center space-y-4">
          <Trophy
            className={cn(
              'h-16 w-16 mx-auto',
              score >= 80
                ? 'text-yellow-500'
                : score >= 50
                ? 'text-gray-400'
                : 'text-orange-400'
            )}
          />
          <h2 className="text-2xl font-bold">Quiz Complete!</h2>
          <p className="text-lg">
            You scored{' '}
            <span className="font-bold text-primary">
              {correctCount}/{allMcqs.length}
            </span>{' '}
            ({Math.round(score)}%)
          </p>
          <Progress value={score} className="w-64 mx-auto h-3" />
          <Button onClick={handleRestart} className="mt-4">
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">
              Question {currentQuestion + 1} of {allMcqs.length}
            </CardTitle>
            <CardDescription>
              From Slide {current.slideNumber} • {current.difficulty.charAt(0).toUpperCase() + current.difficulty.slice(1)}
            </CardDescription>
          </div>
          <div className="text-sm text-muted-foreground">
            Score: {correctCount}/{answers.length}
          </div>
        </div>
        <Progress
          value={((currentQuestion + 1) / allMcqs.length) * 100}
          className="h-2"
        />
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Question */}
        <p className="text-lg font-medium">{current.mcq.question}</p>

        {/* Options */}
        <div className="space-y-2">
          {current.mcq.options.map((option, index) => {
            const isSelected = selectedOption === option;
            const isCorrect = option === current.mcq.answer;  // Backend uses 'answer'
            const showCorrect = showResult && isCorrect;
            const showWrong = showResult && isSelected && !isCorrect;

            return (
              <button
                key={index}
                onClick={() => handleOptionSelect(option)}
                disabled={showResult}
                className={cn(
                  'w-full text-left p-4 rounded-lg border-2 transition-colors',
                  !showResult && isSelected && 'border-primary bg-primary/5',
                  !showResult && !isSelected && 'border-muted hover:border-primary/50',
                  showCorrect && 'border-green-500 bg-green-500/10',
                  showWrong && 'border-destructive bg-destructive/10'
                )}
              >
                <div className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full border flex items-center justify-center text-sm font-medium">
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span className="flex-1">{option}</span>
                  {showCorrect && <CheckCircle className="h-5 w-5 text-green-500" />}
                  {showWrong && <XCircle className="h-5 w-5 text-destructive" />}
                </div>
              </button>
            );
          })}
        </div>

        {/* Difficulty Badge */}
        {showResult && (
          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm">
              <span className="font-medium">Correct Answer: </span>
              {current.mcq.answer}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between pt-4">
          <Button
            variant="outline"
            onClick={() => {
              setCurrentQuestion((prev) => prev - 1);
              setSelectedOption(null);
              setShowResult(false);
            }}
            disabled={currentQuestion === 0}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>

          {showResult ? (
            <Button onClick={handleNext}>
              {isLastQuestion ? 'See Results' : 'Next Question'}
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={!selectedOption}>
              Submit Answer
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
