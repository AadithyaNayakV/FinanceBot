import { useState, useRef, useEffect } from "react";
import { 
  Paperclip, 
  Send, 
  Loader2, 
  UploadCloud,
  ArrowDown
} from "lucide-react";
import { ThemeProvider } from "./context/ThemeContext";
import Navbar from "./components/Navbar";
import ChatMessage from "./components/ChatMessage";
import FileUploadPreview from "./components/FileUploadPreview";
import ThreeDBackground from "./components/ThreeDBackground";

const INITIAL_MESSAGE = {
  type: "bot",
  text: "Hi I am FinanceBot, how can I help you today?",
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
};

const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");

function MainChat() {
  const [query, setQuery] = useState("");
  const [files, setFiles] = useState([]);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = (behavior = "smooth") => {
    chatEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isUp = scrollHeight - scrollTop - clientHeight > 150;
    setShowScrollBottom(isUp);
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files)]);
    }
  };

  const handleRemoveFile = (indexToRemove) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles((prev) => [...prev, ...Array.from(e.dataTransfer.files)]);
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim() && files.length === 0) return;

    const textToSend = query.trim();
    const currentFiles = [...files];
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        text: textToSend,
        files: currentFiles,
        timestamp
      }
    ]);

    setQuery("");
    setFiles([]);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("query", textToSend);
    currentFiles.forEach((file) => formData.append("files", file));

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      const botTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: data.answer || "No response received.",
          source: data.source,
          timestamp: botTimestamp
        }
      ]);
    } catch (err) {
      console.error("Chat error:", err);
      const botTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Some error has occurred ⚠️",
          timestamp: botTimestamp
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleClearChat = () => {
    setMessages([INITIAL_MESSAGE]);
    setFiles([]);
    setQuery("");
  };

  return (
    <div 
      className="relative flex flex-col h-screen overflow-hidden"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* 3D Interactive Background */}
      <ThreeDBackground />

      {/* Drag & Drop Overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-50 bg-emerald-950/70 backdrop-blur-sm flex flex-col items-center justify-center p-6 border-2 border-dashed border-emerald-400 rounded-2xl m-4">
          <UploadCloud className="w-12 h-12 text-emerald-300 mb-2 animate-bounce" />
          <h2 className="text-xl font-bold text-white">Drop files here to attach</h2>
        </div>
      )}

      {/* Top Navbar */}
      <Navbar 
        onClearChat={handleClearChat}
        messageCount={messages.length}
      />

      {/* Main Chat Container */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full overflow-hidden relative z-10 px-3 sm:px-6">
        
        {/* Messages List */}
        <div 
          ref={scrollContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto py-4 flex flex-col justify-start"
        >
          <div className="flex flex-col gap-2">
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-medium text-sm py-2 px-3">
                <Loader2 className="w-4 h-4 animate-spin text-emerald-600 dark:text-emerald-400" />
                <span>Thinking...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Scroll to bottom floating button */}
        {showScrollBottom && (
          <button
            onClick={() => scrollToBottom()}
            className="absolute bottom-24 right-8 p-2.5 rounded-full bg-white dark:bg-slate-800 text-emerald-600 dark:text-emerald-400 shadow-xl border border-slate-300 dark:border-slate-700 hover:scale-110 transition-all z-20"
            title="Scroll to bottom"
          >
            <ArrowDown className="w-4 h-4" />
          </button>
        )}

        {/* 3D Floating Input Bar */}
        <div className="py-3 sm:py-4">
          <form
            onSubmit={handleSubmit}
            className="bg-white dark:bg-slate-900 rounded-2xl border-2 border-slate-300 dark:border-slate-700 shadow-xl transition-all focus-within:border-emerald-500 dark:focus-within:border-emerald-500"
          >
            <input
              type="file"
              multiple
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
            />

            {/* Attached Files Preview */}
            <FileUploadPreview 
              files={files} 
              onRemoveFile={handleRemoveFile} 
            />

            <div className="flex items-end gap-2 p-2 sm:p-2.5">
              {/* Paperclip Button */}
              <button
                type="button"
                onClick={handleUploadClick}
                className="p-2 rounded-xl text-slate-700 dark:text-slate-300 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all shrink-0"
                title="Attach files"
              >
                <Paperclip className="w-5 h-5" />
              </button>

              {/* Text Input - Explicit black text in light mode, crisp white in dark mode */}
              <textarea
                ref={textareaRef}
                rows={1}
                value={query}
                onChange={handleQueryChange}
                onKeyDown={handleKeyDown}
                placeholder="Type your question..."
                className="flex-1 bg-transparent border-none outline-none resize-none text-sm text-slate-950 dark:text-white placeholder:text-slate-500 dark:placeholder:text-slate-400 font-medium py-1.5 px-1 max-h-32 min-h-[36px] leading-relaxed"
              />

              {/* Send Button */}
              <button
                type="submit"
                disabled={loading || (!query.trim() && files.length === 0)}
                className={`p-2.5 px-4 rounded-xl font-bold flex items-center justify-center shrink-0 transition-all ${
                  loading || (!query.trim() && files.length === 0)
                    ? 'bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 cursor-not-allowed opacity-60'
                    : 'bg-emerald-600 hover:bg-emerald-700 text-white btn-3d shadow-md'
                }`}
                title="Send"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
          </form>
        </div>

      </main>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <MainChat />
    </ThemeProvider>
  );
}
