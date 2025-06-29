// frontend/components/content-editor.tsx
"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useEffect, useState } from "react";
import { 
  Bold, 
  Italic, 
  List, 
  ListOrdered, 
  Heading1, 
  Heading2, 
  Quote, 
  Code,
  Undo,
  Redo,
  Eye,
  Edit3,
  Save,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "sonner";

interface ContentEditorProps {
  content: string;
  editable?: boolean;
  onUpdate?: (html: string) => void;
  onSave?: (html: string) => void;
  onCancel?: () => void;
  placeholder?: string;
  className?: string;
}

export default function ContentEditor({ 
  content, 
  editable = false, 
  onUpdate, 
  onSave,
  onCancel,
  placeholder = "Start writing...",
  className = ""
}: ContentEditorProps) {
  const [isPreviewMode, setIsPreviewMode] = useState(!editable);
  const [hasChanges, setHasChanges] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  const editor = useEditor({
    extensions: [StarterKit],
    content,
    editable: editable && !isPreviewMode,
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const text = editor.getText();
      const words = text.trim() ? text.trim().split(/\s+/).length : 0;
      
      setWordCount(words);
      setHasChanges(true);
      onUpdate?.(html);
    },
    editorProps: {
      attributes: {
        class: `prose prose-sm max-w-none focus:outline-none p-4 min-h-[200px] ${
          editable && !isPreviewMode 
            ? 'border border-gray-200 rounded-md bg-white' 
            : 'bg-gray-50'
        }`,
        'data-placeholder': placeholder,
      },
    },
  });

  useEffect(() => {
    if (editor && editor.getHTML() !== content) {
      editor.commands.setContent(content, false);
      setHasChanges(false);
      
      // Calculate initial word count
      const text = editor.getText();
      const words = text.trim() ? text.trim().split(/\s+/).length : 0;
      setWordCount(words);
    }
  }, [content, editor]);

  const handleSave = () => {
    if (editor && onSave) {
      onSave(editor.getHTML());
      setHasChanges(false);
      toast.success("Content saved successfully!");
    }
  };

  const handleCancel = () => {
    if (editor) {
      editor.commands.setContent(content, false);
      setHasChanges(false);
      onCancel?.();
    }
  };

  const togglePreview = () => {
    if (editable) {
      setIsPreviewMode(!isPreviewMode);
      if (editor) {
        editor.setEditable(!isPreviewMode);
      }
    }
  };

  if (!editor) {
    return (
      <Card className={className}>
        <CardContent className="p-4">
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const ToolbarButton = ({ 
    onClick, 
    disabled, 
    active, 
    icon: Icon, 
    label 
  }: {
    onClick: () => void;
    disabled?: boolean;
    active?: boolean;
    icon: React.ElementType;
    label: string;
  }) => (
    <Button
      variant={active ? "default" : "ghost"}
      size="sm"
      onClick={onClick}
      disabled={disabled}
      title={label}
      className="h-8 w-8 p-0"
    >
      <Icon className="h-4 w-4" />
    </Button>
  );

  return (
    <Card className={className}>
      {editable && (
        <div className="border-b border-gray-200 p-3">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-xs">
                {wordCount} words
              </Badge>
              {hasChanges && (
                <Badge variant="secondary" className="text-xs">
                  Unsaved changes
                </Badge>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={togglePreview}
                className="flex items-center gap-2"
              >
                {isPreviewMode ? (
                  <>
                    <Edit3 className="h-4 w-4" />
                    Edit
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4" />
                    Preview
                  </>
                )}
              </Button>
              
              {hasChanges && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancel}
                    className="flex items-center gap-2"
                  >
                    <X className="h-4 w-4" />
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    className="flex items-center gap-2"
                  >
                    <Save className="h-4 w-4" />
                    Save
                  </Button>
                </>
              )}
            </div>
          </div>

          {!isPreviewMode && (
            <div className="flex flex-wrap items-center gap-1 p-2 bg-gray-50 rounded-md">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBold().run()}
                disabled={!editor.can().chain().focus().toggleBold().run()}
                active={editor.isActive('bold')}
                icon={Bold}
                label="Bold"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleItalic().run()}
                disabled={!editor.can().chain().focus().toggleItalic().run()}
                active={editor.isActive('italic')}
                icon={Italic}
                label="Italic"
              />
              
              <Separator orientation="vertical" className="h-6 mx-1" />
              
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                active={editor.isActive('heading', { level: 1 })}
                icon={Heading1}
                label="Heading 1"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                active={editor.isActive('heading', { level: 2 })}
                icon={Heading2}
                label="Heading 2"
              />
              
              <Separator orientation="vertical" className="h-6 mx-1" />
              
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBulletList().run()}
                active={editor.isActive('bulletList')}
                icon={List}
                label="Bullet List"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                active={editor.isActive('orderedList')}
                icon={ListOrdered}
                label="Ordered List"
              />
              
              <Separator orientation="vertical" className="h-6 mx-1" />
              
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBlockquote().run()}
                active={editor.isActive('blockquote')}
                icon={Quote}
                label="Quote"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleCode().run()}
                active={editor.isActive('code')}
                icon={Code}
                label="Inline Code"
              />
              
              <Separator orientation="vertical" className="h-6 mx-1" />
              
              <ToolbarButton
                onClick={() => editor.chain().focus().undo().run()}
                disabled={!editor.can().chain().focus().undo().run()}
                icon={Undo}
                label="Undo"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().redo().run()}
                disabled={!editor.can().chain().focus().redo().run()}
                icon={Redo}
                label="Redo"
              />
            </div>
          )}
        </div>
      )}
      
      <CardContent className="p-0 relative">
        {editable && !isPreviewMode && !editor.getText().trim() && (
          <div className="absolute top-4 left-4 text-gray-400 pointer-events-none">
            {placeholder}
          </div>
        )}
        <EditorContent editor={editor} />
      </CardContent>
    </Card>
  );
}