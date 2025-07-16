import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Loader2, Zap, Brain, FileText, Sparkles, X } from "lucide-react";

interface GeneratingDialogProps {
  open: boolean;
  onOpenChange?: (open: boolean) => void;
  currentAgent?: string;
  progress?: number;
  templateName?: string;
  styleProfile?: string;
  requestId?: string;
  onCancel?: () => void;
}

// Agent information for enhanced UX
const agentInfo = {
  planner: {
    name: "Planning",
    icon: Brain,
    description: "Analyzing requirements and creating content strategy",
    color: "text-blue-500"
  },
  researcher: {
    name: "Research", 
    icon: FileText,
    description: "Gathering relevant information and insights",
    color: "text-green-500"
  },
  writer: {
    name: "Writing",
    icon: Sparkles,
    description: "Crafting your content with AI creativity",
    color: "text-purple-500"
  },
  editor: {
    name: "Editing",
    icon: FileText,
    description: "Refining and polishing the content",
    color: "text-orange-500"
  },
  seo_optimizer: {
    name: "SEO Optimization",
    icon: Zap,
    description: "Optimizing for search engines and readability",
    color: "text-pink-500"
  },
  formatter: {
    name: "Formatting",
    icon: FileText,
    description: "Applying final formatting and structure",
    color: "text-indigo-500"
  }
};

export default function GeneratingDialog({ 
  open, 
  onOpenChange,
  currentAgent = "planner",
  progress = 0,
  templateName,
  styleProfile,
  requestId,
  onCancel
}: GeneratingDialogProps) {
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [dots, setDots] = useState("");

  // Timer for elapsed time
  useEffect(() => {
    if (!open) {
      setTimeElapsed(0);
      return;
    }

    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [open]);

  // Animated dots for loading effect
  useEffect(() => {
    if (!open) {
      setDots("");
      return;
    }

    const dotsTimer = setInterval(() => {
      setDots(prev => {
        if (prev === "...") return "";
        return prev + ".";
      });
    }, 500);

    return () => clearInterval(dotsTimer);
  }, [open]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const currentAgentInfo = agentInfo[currentAgent as keyof typeof agentInfo] || agentInfo.planner;
  const AgentIcon = currentAgentInfo.icon;

  // Calculate progress if not provided
  const calculatedProgress = progress > 0 ? progress : Math.min((timeElapsed / 30) * 100, 95);

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    if (onOpenChange) {
      onOpenChange(false);
    }
  };

  // Handle dialog state changes - only allow closing if there's a cancel handler
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && onCancel) {
      // Only allow closing if cancel is available
      onCancel();
    }
    // Don't automatically close during generation unless explicitly cancelled
    if (onOpenChange && (!newOpen && onCancel)) {
      onOpenChange(newOpen);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent 
        aria-describedby="generation-description"
        className="max-w-md mx-auto"
        // Prevent closing by clicking outside during generation unless cancel is available
        onPointerDownOutside={(e) => {
          if (!onCancel) {
            e.preventDefault();
          }
        }}
        onEscapeKeyDown={(e) => {
          if (!onCancel) {
            e.preventDefault();
          }
        }}
      >
        <DialogHeader className="text-center space-y-4">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Generating Content{dots}
            </DialogTitle>
            {onCancel && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCancel}
                className="h-8 w-8 p-0 hover:bg-red-100 hover:text-red-600"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          
          <DialogDescription id="generation-description" className="text-muted-foreground text-sm text-center">
            <span className="block mb-2">Our AI agents are working together to create your content.</span>
            {templateName && styleProfile && (
              <span className="flex justify-center gap-2 flex-wrap">
                <Badge variant="outline" className="text-xs">
                  {templateName}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {styleProfile}
                </Badge>
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        {/* Progress Section */}
        <div className="space-y-6 py-4">
          {/* Current Agent Status */}
          <div className="flex items-center justify-center space-x-3">
            <div className={`p-3 rounded-full bg-gray-100 dark:bg-gray-800 ${currentAgentInfo.color}`}>
              <AgentIcon className="h-6 w-6 animate-pulse" />
            </div>
            <div className="text-center">
              <div className="font-medium">{currentAgentInfo.name} Agent</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {currentAgentInfo.description}
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium">Progress</span>
              <span className="text-gray-600 dark:text-gray-400">
                {Math.round(calculatedProgress)}%
              </span>
            </div>
            <Progress 
              value={calculatedProgress} 
              className="h-2"
            />
          </div>

          {/* Agent Pipeline Visualization */}
          <div className="grid grid-cols-3 gap-2">
            {Object.entries(agentInfo).slice(0, 6).map(([agentKey, agent]) => {
              const isActive = agentKey === currentAgent;
              const isCompleted = Object.keys(agentInfo).indexOf(agentKey) < Object.keys(agentInfo).indexOf(currentAgent);
              const AgentIconComponent = agent.icon;
              
              return (
                <div 
                  key={agentKey}
                  className={`p-2 rounded-lg text-center transition-all duration-300 ${
                    isActive 
                      ? 'bg-blue-100 dark:bg-blue-900 border-2 border-blue-300 dark:border-blue-700' 
                      : isCompleted
                      ? 'bg-green-100 dark:bg-green-900 border border-green-300 dark:border-green-700'
                      : 'bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                  }`}
                >
                  <AgentIconComponent 
                    className={`h-4 w-4 mx-auto mb-1 ${
                      isActive ? 'animate-pulse text-blue-600' : 
                      isCompleted ? 'text-green-600' : 
                      'text-gray-400'
                    }`} 
                  />
                  <div className={`text-xs font-medium ${
                    isActive ? 'text-blue-700 dark:text-blue-300' : 
                    isCompleted ? 'text-green-700 dark:text-green-300' : 
                    'text-gray-500'
                  }`}>
                    {agent.name}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Loading Animation */}
          <div className="flex justify-center items-center py-4">
            <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          </div>

          {/* Status Information */}
          <div className="text-center space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex justify-center items-center gap-4">
              <span>Time: {formatTime(timeElapsed)}</span>
              {requestId && (
                <span className="font-mono text-xs">ID: {requestId.slice(-8)}</span>
              )}
            </div>
            <p className="text-xs">
              This usually takes 30-60 seconds. Please don&apos;t close this window.
            </p>
          </div>

          {/* Cancel Button */}
          {onCancel && (
            <div className="flex justify-center pt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancel}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
              >
                Cancel Generation
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}