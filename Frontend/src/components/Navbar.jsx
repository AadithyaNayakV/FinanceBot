import React from 'react';
import { Sun, Moon, Trash2 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function Navbar({ onClearChat, messageCount }) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 w-full glass-panel border-b transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="relative w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-500 p-[2px] shadow-lg shadow-emerald-500/20">
            <div className="w-full h-full rounded-[14px] bg-[#090d16] flex items-center justify-center relative overflow-hidden">
              <span className="text-xl font-black bg-gradient-to-r from-emerald-400 to-cyan-300 bg-clip-text text-transparent">
                $
              </span>
            </div>
          </div>

          <div>
            <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 dark:from-emerald-400 dark:via-teal-300 dark:to-cyan-400 bg-clip-text text-transparent">
              FinanceBot
            </span>
          </div>
        </div>

        {/* Right Actions: Clear Chat & Theme Switcher */}
        <div className="flex items-center gap-3">
          {messageCount > 1 && (
            <button
              onClick={onClearChat}
              title="Clear Conversation"
              className="p-2 px-3 rounded-xl text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 hover:bg-red-500/10 transition-colors flex items-center gap-1.5 text-xs font-medium"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear</span>
            </button>
          )}

          {/* 3D Theme Switcher */}
          <button
            onClick={toggleTheme}
            aria-label="Toggle Theme"
            className="p-2.5 rounded-2xl glass-card border hover:border-emerald-500/40 text-gray-700 dark:text-gray-200 transition-all duration-300 hover:scale-105 active:scale-95 shadow-sm"
          >
            {isDark ? (
              <Sun className="w-5 h-5 text-amber-400 transition-transform duration-300 hover:rotate-45" />
            ) : (
              <Moon className="w-5 h-5 text-indigo-600 transition-transform duration-300 hover:-rotate-12" />
            )}
          </button>
        </div>

      </div>
    </header>
  );
}
