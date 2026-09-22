import React from 'react';
import { FileText, FileSpreadsheet, FileCode, File, X } from 'lucide-react';

function getFileIcon(fileName) {
  const ext = fileName.split('.').pop().toLowerCase();
  if (['csv', 'xlsx', 'xls'].includes(ext)) {
    return <FileSpreadsheet className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />;
  }
  if (['json', 'py', 'js', 'html', 'sql'].includes(ext)) {
    return <FileCode className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />;
  }
  if (['pdf', 'doc', 'docx', 'txt', 'md'].includes(ext)) {
    return <FileText className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />;
  }
  return <File className="w-4 h-4 text-amber-600 dark:text-amber-400" />;
}

function formatBytes(bytes, decimals = 1) {
  if (!+bytes) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

export default function FileUploadPreview({ files, onRemoveFile }) {
  if (!files || files.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-3 py-2 bg-slate-100/90 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 rounded-t-2xl">
      {files.map((file, index) => (
        <div
          key={index}
          className="flex items-center gap-2 pl-2.5 pr-1.5 py-1 rounded-xl bg-white dark:bg-slate-800 text-xs border border-slate-200 dark:border-slate-700/60 shadow-sm"
        >
          {getFileIcon(file.name)}
          <div className="flex flex-col min-w-0">
            <span className="font-semibold text-slate-900 dark:text-slate-100 truncate max-w-[140px]">
              {file.name}
            </span>
            <span className="text-[10px] text-slate-600 dark:text-slate-400 font-mono">
              {formatBytes(file.size)}
            </span>
          </div>
          <button
            type="button"
            onClick={() => onRemoveFile(index)}
            className="p-1 rounded-lg text-slate-500 hover:text-red-500 hover:bg-red-500/10 transition-colors ml-1"
            title="Remove attachment"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
}
