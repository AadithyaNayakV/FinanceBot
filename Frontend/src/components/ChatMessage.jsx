import React, { useState } from 'react';
import { Bot, User, Copy, Check, FileText } from 'lucide-react';

function formatMessageText(text) {
  if (!text) return null;
  const lines = text.split('\n');

  return lines.map((line, idx) => {
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      return (
        <li key={idx} className="ml-4 list-disc my-1 text-slate-900 dark:text-slate-100 font-normal">
          {renderFormattedInline(line.trim().substring(2))}
        </li>
      );
    }
    if (/^\d+\.\s/.test(line.trim())) {
      return (
        <li key={idx} className="ml-4 list-decimal my-1 text-slate-900 dark:text-slate-100 font-normal">
          {renderFormattedInline(line.trim().replace(/^\d+\.\s/, ''))}
        </li>
      );
    }
    if (!line.trim()) {
      return <div key={idx} className="h-2" />;
    }
    return (
      <p key={idx} className="my-1 leading-relaxed text-slate-900 dark:text-slate-100 font-normal">
        {renderFormattedInline(line)}
      </p>
    );
  });
}

function renderFormattedInline(str) {
  const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-slate-950 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="font-mono text-xs px-1.5 py-0.5 rounded bg-slate-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-slate-300 dark:border-emerald-700/50">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

export default function ChatMessage({ message }) {
  const isUser = message.type === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!message.text) return;
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const timeString = message.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div 
      className={`flex items-start gap-3 my-3 group transition-all duration-200 ${
        isUser ? 'flex-row-reverse self-end' : 'self-start'
      } max-w-full sm:max-w-[85%] lg:max-w-[80%]`}
    >
      {/* 3D Avatar */}
      <div className="shrink-0 mt-0.5">
        {isUser ? (
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 p-[2px] shadow-sm">
            <div className="w-full h-full rounded-[10px] bg-slate-900 flex items-center justify-center text-white">
              <User className="w-4 h-4 text-emerald-300" />
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-[2px] shadow-sm">
            <div className="w-full h-full rounded-[10px] bg-slate-900 flex items-center justify-center text-white">
              <Bot className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
        )}
      </div>

      {/* Message Bubble Container */}
      <div className="flex flex-col gap-1 min-w-0">
        
        {/* Author & Time - High contrast in both light and dark mode */}
        <div className={`flex items-center gap-2 px-1 text-xs text-slate-700 dark:text-slate-300 font-semibold ${
          isUser ? 'justify-end' : 'justify-start'
        }`}>
          <span className="text-slate-900 dark:text-slate-200">
            {isUser ? 'You' : 'FinanceBot'}
          </span>
          <span className="text-slate-400">•</span>
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-normal">{timeString}</span>
        </div>

        {/* Bubble Body */}
        <div
          className={`relative rounded-2xl p-3.5 sm:p-4 text-sm transition-all duration-200 ${
            isUser
              ? 'bg-gradient-to-br from-emerald-600 to-teal-600 text-white shadow-md rounded-tr-xs'
              : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-tl-xs border border-slate-300 dark:border-slate-700 shadow-md backdrop-blur-md'
          }`}
        >
          {/* User Attached Files */}
          {message.files && message.files.length > 0 && (
            <div className="mb-2.5 flex flex-wrap gap-1.5">
              {message.files.map((file, i) => (
                <div 
                  key={i} 
                  className="flex items-center gap-1.5 px-2 py-0.5 rounded-lg bg-white/20 text-xs backdrop-blur-sm text-white font-medium"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span className="truncate max-w-[140px]">{file.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* Main Text */}
          <div className="text-[13.5px] leading-relaxed text-slate-900 dark:text-slate-100">
            {formatMessageText(message.text)}
          </div>

          {/* Source Info if available */}
          {message.source && message.source !== 'None' && message.source !== 'undefined' && (
            <div className="mt-2.5 pt-2 border-t border-slate-200 dark:border-slate-700 text-xs text-emerald-700 dark:text-emerald-400 font-mono font-semibold">
              📎 Source: {typeof message.source === 'string' ? message.source : JSON.stringify(message.source)}
            </div>
          )}

          {/* Copy Button */}
          <div className="mt-1 flex items-center justify-end opacity-70 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="p-1 rounded text-slate-900 hover:text-slate-900 dark:text-gray-100 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-1 text-[11px] font-medium"
              title="Copy message"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                  <span className="text-emerald-600 dark:text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
