// frontend/components/GenerationPreview.tsx
"use client";

import { useState, useEffect, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// Update these import paths to the correct relative paths if needed
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Loader2, 
  Brain, 
  FileText, 
  CheckCircle, 
  XCircle,
  Eye,
  Download,
  Copy
} from "lucide-react";

interface GenerationStep {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  duration?: number;
}

interface GenerationPreviewProps {
  isGenerating: boolean;
  generatedContent?: string;
  onCancel?: () => void;
  onSave?: () => void;
  templateName?: string;
  styleProfile?: string;
}

export function GenerationPreview(props: GenerationPreviewProps) {
  const {
    isGenerating,
    generatedContent,
    onCancel,
    onSave,
    templateName = "Unknown Template",
    styleProfile = "Default Style"
  } = props;

  const [progress, setProgress] = useState(0);
  const [streamedContent, setStreamedContent] = useState("");

  const generationSteps: GenerationStep[] = useMemo(() => [
    { id: "planning", name: "Planning Content Structure", status: 'pending' },
    { id: "research", name: "Gathering Information", status: 'pending' },
    { id: "writing", name: "Generating Content", status: 'pending' },
    { id: "formatting", name: "Applying Style & Format", status: 'pending' },
    { id: "review", name: "Quality Review", status: 'pending' },
  ], []);

  const [steps, setSteps] = useState<GenerationStep[]>(generationSteps);

  // Simulate generation progress
    useEffect(() => {
      if (!isGenerating) {
        setProgress(0);
        setStreamedContent("");
        setSteps(generationSteps);
        return;
      }
  
      const interval = setInterval(() => {
        setProgress(prev => {
          const newProgress = Math.min(prev + Math.random() * 15, 100);
  
          // Update steps based on progress
          const stepIndex = Math.floor((newProgress / 100) * steps.length);
          setSteps(prevSteps =>
            prevSteps.map((step, index) => ({
              ...step,
              status: index < stepIndex ? 'completed' :
                     index === stepIndex ? 'active' : 'pending'
            }))
          );
  
          return newProgress;
        });
      }, 800);
  
      return () => clearInterval(interval);
    }, [isGenerating, generationSteps, steps.length]);

  // Simulate streaming content
  useEffect(() => {
    if (generatedContent && !isGenerating) {
      setStreamedContent("");
      let index = 0;
      const streamInterval = setInterval(() => {
        if (index < generatedContent.length) {
          setStreamedContent(prev => prev + generatedContent[index]);
          index++;
        } else {
          clearInterval(streamInterval);
        }
      }, 30);
      
      return () => clearInterval(streamInterval);
    }
  }, [generatedContent, isGenerating]);

  const copyToClipboard = async () => {
    if (streamedContent) {
      await navigator.clipboard.writeText(streamedContent);
    }
  };

  if (!isGenerating && !generatedContent) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Generation Status Card */}
      <Card className="border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {isGenerating ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin text-purple-600" />
                  Generating Content
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Generation Complete
                </>
              )}
            </CardTitle>
            <div className="flex gap-2">
              <Badge variant="secondary">{templateName}</Badge>
              <Badge variant="outline">{styleProfile}</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Generation Steps */}
          <div className="space-y-2">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center gap-3 p-2 rounded-lg transition-all">
                <div className={`
                  w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium
                  ${step.status === 'completed' ? 'bg-green-100 text-green-700' :
                    step.status === 'active' ? 'bg-purple-100 text-purple-700' :
                    step.status === 'error' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-500'}
                `}>
                  {step.status === 'completed' ? (
                    <CheckCircle className="h-3 w-3" />
                  ) : step.status === 'active' ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : step.status === 'error' ? (
                    <XCircle className="h-3 w-3" />
                  ) : (
                    index + 1
                  )}
                </div>
                <span className={`text-sm ${
                  step.status === 'active' ? 'font-medium text-purple-700' : 
                  step.status === 'completed' ? 'text-green-700' :
                  'text-gray-600'
                }`}>
                  {step.name}
                </span>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          {isGenerating && (
            <div className="flex gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={onCancel}>
                Cancel Generation
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Content Preview */}
      {(streamedContent || isGenerating) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Generated Content Preview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Content Display */}
              <div className="min-h-[300px] max-h-[600px] overflow-y-auto p-4 bg-gray-50 rounded-lg border">
                <div className="prose prose-sm max-w-none">
                  {streamedContent ? (
                    <pre className="whitespace-pre-wrap font-sans text-gray-800">
                      {streamedContent}
                      {isGenerating && (
                        <span className="animate-pulse">▊</span>
                      )}
                    </pre>
                  ) : (
                    <div className="flex items-center justify-center h-32 text-gray-400">
                      <div className="text-center">
                        <Brain className="h-8 w-8 mx-auto mb-2 animate-pulse" />
                        <p>AI is thinking...</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              {streamedContent && !isGenerating && (
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" size="sm" onClick={copyToClipboard}>
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-2" />
                    Full Preview
                  </Button>
                  <Button onClick={onSave}>
                    Save Content
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}