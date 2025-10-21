import { useState, useRef, useEffect } from "react";
import { PaperClipIcon } from "@heroicons/react/24/solid";

function App() {
  const [query, setQuery] = useState("");
  const [files, setFiles] = useState([]);
  const [messages, setMessages] = useState([{type:btoa,text:"Hi Iam ANMate How Can I Help You Today?"}]);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);
  const [loading,setloading]=useState(false)

  
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

   const handleSubmit = async (e) => {
    setloading(true)
    e.preventDefault();
    if (!query) return;

    const formData = new FormData();
    formData.append('query', query);
    files.forEach((file) => formData.append('files', file));

    try {
       setQuery('');
             setMessages((prev) => [...prev, { type: 'user', text: query }]);

      const res = await fetch('http://localhost:8000/chat/', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
//    const data = await new Promise((resolve) => {
//   setTimeout(() => {
//     const result = { answer: "as" };
//     resolve(result);
//   }, 2000);
// });
      setMessages((prev) => [...prev,  { type: 'bot', text: data.answer }]);
      setQuery('');
      setFiles([]);
      setloading(false)
    } catch (err) {
      setloading(true)
           setMessages((prev) => [...prev,{ type: 'bot', text: "Some Error has been Occured ⚠️" }]);

    }
    finally {
      setloading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`inline-block px-4 py-2 rounded-lg break-words ${
              msg.type === "user"
                ? "bg-gray-500 text-white self-end"
                : "bg-gray-300 text-black self-start"
            }`}
            style={{ maxWidth: "70%" }} 
          >
            {msg.text}
          </div>
        ))}
         {loading && (
            <div className="text-gray-500 text-3xl italic">…</div>
          )}
        <div ref={chatEndRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex items-center p-4 bg-white border-t border-gray-300 gap-2"
      >
        <input
          type="file"
          multiple
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />

        
        <button
          type="button"
          onClick={handleUploadClick}
          className="p-2 hover:bg-gray-200 rounded-full"
        >
          <PaperClipIcon className="h-6 w-6 text-gray-600" />
        </button>

        
        {files.length > 0 && (
          <div className="flex gap-2 overflow-x-auto max-w-xs">
            {files.map((f, idx) => (
              <span
                key={idx}
                className="bg-gray-300 px-2 py-1 rounded text-sm whitespace-nowrap"
              >
                {f.name}
              </span>
            ))}
          </div>
        )}

    
        <input
          type="text"
          placeholder="Type your question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        />

       
        <button
          type="submit"
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
