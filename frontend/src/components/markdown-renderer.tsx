/**
 * Markdown Renderer Component
 * Renders markdown content with proper formatting and cyberpunk styling
 */
import React from "react";
import { cn } from "../lib/utils";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  if (!content) return null;

  // Enhanced markdown parser
  const parseMarkdown = (text: string): string => {
    if (!text) return "";
    
    let html = text;

    // 1. Code blocks first (preserve them)
    const codeBlockPlaceholders: string[] = [];
    html = html.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
      const id = `CODEBLOCK_${codeBlockPlaceholders.length}`;
      codeBlockPlaceholders.push(`<pre class="bg-black/80 p-4 rounded border border-gray-700 my-4 overflow-x-auto"><code class="text-[#00ff41] text-sm font-mono whitespace-pre">${code.trim()}</code></pre>`);
      return id;
    });

    // 2. Inline code
    const inlineCodePlaceholders: string[] = [];
    html = html.replace(/`([^`\n]+)`/g, (match, code) => {
      const id = `INLINECODE_${inlineCodePlaceholders.length}`;
      inlineCodePlaceholders.push(`<code class="bg-black/60 px-1.5 py-0.5 rounded text-[#00ff41] text-sm font-mono">${code}</code>`);
      return id;
    });

    // 3. Headers
    html = html.replace(/^#### (.*)$/gm, '<h4 class="text-base font-bold text-[#00ff41] mt-5 mb-2 font-mono">$1</h4>');
    html = html.replace(/^### (.*)$/gm, '<h3 class="text-lg font-bold text-[#00ff41] mt-6 mb-3 font-mono">$1</h3>');
    html = html.replace(/^## (.*)$/gm, '<h2 class="text-xl font-bold text-[#00ff41] mt-8 mb-4 font-mono">$1</h2>');
    html = html.replace(/^# (.*)$/gm, '<h1 class="text-2xl font-bold text-[#00ff41] mt-10 mb-5 font-mono">$1</h1>');

    // 4. Bold (**text**)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-white font-bold">$1</strong>');

    // 5. Italic (*text*)
    html = html.replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g, '<em class="text-gray-300 italic">$1</em>');

    // 6. Lists - process line by line
    const lines = html.split('\n');
    const processedLines: string[] = [];
    let currentList: string[] = [];
    let isOrderedList = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const unorderedMatch = line.match(/^[\*\-\+] (.+)$/);
      const orderedMatch = line.match(/^(\d+)\. (.+)$/);

      if (unorderedMatch || orderedMatch) {
        const isOrdered = !!orderedMatch;
        if (currentList.length === 0) {
          isOrderedList = isOrdered;
          currentList.push(unorderedMatch ? unorderedMatch[1] : orderedMatch![2]);
        } else if (isOrderedList === isOrdered) {
          currentList.push(unorderedMatch ? unorderedMatch[1] : orderedMatch![2]);
        } else {
          // Different list type, close current and start new
          const listTag = isOrderedList ? 'ol' : 'ul';
          processedLines.push(`<${listTag} class="my-3 ml-6 space-y-2 ${isOrderedList ? 'list-decimal' : 'list-disc'}">${currentList.map(item => `<li class="text-gray-300">${item}</li>`).join('')}</${listTag}>`);
          currentList = [unorderedMatch ? unorderedMatch[1] : orderedMatch![2]];
          isOrderedList = isOrdered;
        }
      } else {
        if (currentList.length > 0) {
          const listTag = isOrderedList ? 'ol' : 'ul';
          processedLines.push(`<${listTag} class="my-3 ml-6 space-y-2 ${isOrderedList ? 'list-decimal' : 'list-disc'}">${currentList.map(item => `<li class="text-gray-300">${item}</li>`).join('')}</${listTag}>`);
          currentList = [];
        }
        processedLines.push(line);
      }
    }

    // Close any remaining list
    if (currentList.length > 0) {
      const listTag = isOrderedList ? 'ol' : 'ul';
      processedLines.push(`<${listTag} class="my-3 ml-6 space-y-2 ${isOrderedList ? 'list-decimal' : 'list-disc'}">${currentList.map(item => `<li class="text-gray-300">${item}</li>`).join('')}</${listTag}>`);
    }

    html = processedLines.join('\n');

    // 7. Horizontal rules
    html = html.replace(/^---$/gm, '<hr class="my-6 border-gray-700" />');

    // 8. Links
    html = html.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" class="text-[#00ff41] hover:underline" target="_blank" rel="noopener noreferrer">$1</a>');

    // 9. Restore inline code
    inlineCodePlaceholders.forEach((code, idx) => {
      html = html.replace(`INLINECODE_${idx}`, code);
    });

    // 10. Restore code blocks
    codeBlockPlaceholders.forEach((block, idx) => {
      html = html.replace(`CODEBLOCK_${idx}`, block);
    });

    // 11. Paragraphs - wrap non-HTML lines
    const paragraphs = html.split(/\n\n+/);
    html = paragraphs
      .map((p) => {
        p = p.trim();
        if (!p) return "";
        // Skip if already HTML tag
        if (p.match(/^<[^>]+>/)) return p;
        return `<p class="text-gray-300 mb-3 leading-relaxed">${p.replace(/\n/g, "<br />")}</p>`;
      })
      .join("");

    return html;
  };

  return (
    <div
      className={cn("text-sm leading-relaxed", className)}
      dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }}
    />
  );
}
