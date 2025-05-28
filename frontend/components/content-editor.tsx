// frontend/components/content-editor.tsx
"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useEffect } from "react";

interface ContentEditorProps {
  content: string; // HTML string to display
  editable?: boolean; // Whether the editor should be editable
  onUpdate?: (html: string) => void; // Callback for when content changes (if editable)
}

export default function ContentEditor({ content, editable = false, onUpdate }: ContentEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit, // Basic extensions like bold, italic, lists, etc.
    ],
    content: content,
    editable: editable,
    onUpdate: ({ editor }) => {
      if (onUpdate) {
        onUpdate(editor.getHTML());
      }
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-xl focus:outline-none p-4 border border-gray-300 rounded-md bg-white',
      },
    },
  });

  // Update editor content when the 'content' prop changes
  useEffect(() => {
    if (editor && editor.getHTML() !== content) {
      editor.commands.setContent(content, false); // false to not emit update event
    }
  }, [content, editor]);

  if (!editor) {
    return null; // Editor is not ready yet
  }

  return (
    <div>
      {editable && (
        <div className="mb-2 p-2 bg-gray-100 rounded-md border border-gray-200 flex flex-wrap gap-2">
          {/* Basic Editor Controls (can be expanded) */}
          <button
            onClick={() => editor.chain().focus().toggleBold().run()}
            disabled={!editor.can().chain().focus().toggleBold().run()}
            className="px-2 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
          >
            Bold
          </button>
          <button
            onClick={() => editor.chain().focus().toggleItalic().run()}
            disabled={!editor.can().chain().focus().toggleItalic().run()}
            className="px-2 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
          >
            Italic
          </button>
          <button
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            disabled={!editor.can().chain().focus().toggleBulletList().run()}
            className="px-2 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
          >
            Bullet List
          </button>
          <button
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            disabled={!editor.can().chain().focus().toggleOrderedList().run()}
            className="px-2 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
          >
            Ordered List
          </button>
          {/* Add more controls as needed */}
        </div>
      )}
      <EditorContent editor={editor} />
    </div>
  );
}
