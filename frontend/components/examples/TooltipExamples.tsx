// frontend/components/examples/TooltipExamples.tsx
"use client"

import { Button } from "@/components/ui/button"
import { SimpleTooltip } from "@/components/ui/simple-tooltip"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Info, Settings, Download, Share2, Heart, Star } from "lucide-react"

export function TooltipExamples() {
  return (
    <div className="p-8 space-y-8">
      <h2 className="text-2xl font-bold mb-6">Tooltip Examples</h2>
      
      {/* Simple Tooltip Examples */}
      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Simple Tooltips</h3>
        <div className="flex flex-wrap gap-4">
          
          <SimpleTooltip content="This is a helpful tooltip">
            <Button variant="outline">
              <Info className="h-4 w-4 mr-2" />
              Hover me
            </Button>
          </SimpleTooltip>

          <SimpleTooltip content="Generate new AI content" side="bottom">
            <Button className="bg-gradient-to-r from-purple-500 to-pink-500">
              Generate Content
            </Button>
          </SimpleTooltip>

          <SimpleTooltip content="Open settings panel" side="left">
            <Button variant="ghost" size="icon">
              <Settings className="h-4 w-4" />
            </Button>
          </SimpleTooltip>

          <SimpleTooltip content="Download your content" side="right">
            <Button variant="outline" size="icon">
              <Download className="h-4 w-4" />
            </Button>
          </SimpleTooltip>

        </div>
      </section>

      {/* Advanced Tooltip Examples */}
      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Advanced Tooltips</h3>
        <TooltipProvider delayDuration={300}>
          <div className="flex flex-wrap gap-4">
            
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share Content
                </Button>
              </TooltipTrigger>
              <TooltipContent side="top">
                <div className="text-center">
                  <p className="font-medium">Share your content</p>
                  <p className="text-xs opacity-75">Copy link or export file</p>
                </div>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-600">
                  <Heart className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom" className="bg-red-600">
                <p>Add to favorites</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <div className="inline-flex items-center space-x-1 cursor-pointer">
                  <Star className="h-4 w-4 text-yellow-400" />
                  <span className="text-sm">4.9</span>
                </div>
              </TooltipTrigger>
              <TooltipContent side="top">
                <div className="text-center">
                  <p className="font-medium">Content Rating</p>
                  <p className="text-xs opacity-75">Based on 1,247 reviews</p>
                </div>
              </TooltipContent>
            </Tooltip>

          </div>
        </TooltipProvider>
      </section>

      {/* Long Content Tooltip */}
      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Rich Content Tooltips</h3>
        
        <SimpleTooltip
          content={
            <div className="max-w-xs">
              <p className="font-semibold mb-1">AI Content Generation</p>
              <p className="text-xs opacity-90 mb-2">
                Our advanced AI can generate high-quality content in multiple formats including:
              </p>
              <ul className="text-xs space-y-1">
                <li>• Blog posts and articles</li>
                <li>• Social media content</li>
                <li>• Technical documentation</li>
                <li>• Creative writing</li>
              </ul>
            </div>
          }
          side="right"
          className="max-w-none"
        >
          <Button variant="outline">
            <Info className="h-4 w-4 mr-2" />
            What can AI generate?
          </Button>
        </SimpleTooltip>
      </section>

      {/* Disabled Tooltip */}
      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Conditional Tooltips</h3>
        
        <SimpleTooltip
          content="This feature is coming soon!"
          disabled={false}
        >
          <Button variant="outline" disabled>
            Premium Feature
          </Button>
        </SimpleTooltip>
        
        <SimpleTooltip
          content="You don't have permission"
          disabled={true}
        >
          <Button variant="outline">
            No Tooltip When Disabled
          </Button>
        </SimpleTooltip>
      </section>

      {/* Interactive Tooltip Demo */}
      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Interactive Elements</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          
          {[
            { icon: Download, label: "Download", tooltip: "Download as PDF, DOCX, or MD" },
            { icon: Share2, label: "Share", tooltip: "Share via link or social media" },
            { icon: Settings, label: "Settings", tooltip: "Customize your preferences" },
            { icon: Info, label: "Help", tooltip: "Get help and documentation" },
          ].map(({ icon: Icon, label, tooltip }) => (
            <SimpleTooltip key={label} content={tooltip} side="top">
              <div className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors">
                <Icon className="h-6 w-6 mx-auto mb-2 text-purple-500" />
                <p className="text-center text-sm font-medium">{label}</p>
              </div>
            </SimpleTooltip>
          ))}
          
        </div>
      </section>
    </div>
  )
}