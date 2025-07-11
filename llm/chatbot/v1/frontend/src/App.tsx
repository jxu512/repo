// frontend/src/App.tsx
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const App = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("llama3");
const [isLoading, setIsLoading] = useState(false);
const [useRAG, setUseRAG] = useState(false);
const messageEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage: Message = {
      id: Date.now(),
      text: input.trim(),
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    
    try {
      const res = await axios.post("http://localhost:8000/chat", {
        prompt: input.trim(),
        model,
        use_rag: useRAG,
      }, {
        timeout: 600000 // 60 second timeout
      });
      
      const botMessage: Message = {
        id: Date.now() + 1,
        text: res.data.response || "No response received",
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: `Error: ${error.response?.data?.detail || error.message || 'Failed to communicate with server'}`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const indexContent = async () => {
    if (!input.trim() || isLoading) return;
    setIsLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/index", {
        texts: [input.trim()]
      }, {
        timeout: 600000
      });
      const indexMessage: Message = {
        id: Date.now(),
        text: `Indexing: ${res.data.status}`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, indexMessage]);
      setInput("");
    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now(),
        text: `Indexing Error: ${error.response?.data?.detail || error.message || 'Failed'}`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="h-screen w-screen flex justify-center bg-gray-50">
      <div className="h-full w-full max-w-4xl flex flex-col">
        <header className="bg-white shadow-sm border-b">
          <h1 className="text-2xl font-bold p-4 text-gray-800">Chatbot powered by Ollama</h1>
        </header>

        <div className="flex flex-col flex-1 p-4 overflow-hidden">
          {/* Messages Panel - Always visible */}
          <div className="flex-1 border border-gray-200 rounded-lg bg-white shadow-sm overflow-hidden flex flex-col">
            <div className="flex-1 p-4 overflow-y-auto space-y-3">
              {messages.length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  <p className="text-lg">Welcome to the Ollama Chatbot!</p>
                  <p className="text-sm mt-2">Start a conversation by typing a message below.</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] p-3 rounded-lg ${
                        message.sender === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.text}</p>
                      <p className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                      <span>Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messageEndRef} />
            </div>
          </div>

          {/* Input Panel */}
          <div className="mt-4 bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <textarea
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  placeholder="Type your message here..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  disabled={isLoading}
                />
              </div>
              <div className="flex gap-4">
                <div className="flex flex-col gap-2">
                  <button
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      isLoading || !input.trim()
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-blue-500 text-white hover:bg-blue-600'
                    }`}
                    onClick={sendMessage}
                    disabled={isLoading || !input.trim()}
                  >
                    {isLoading ? 'Sending...' : 'Send'}
                  </button>
                  <button
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      isLoading || !input.trim()
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-green-500 text-white hover:bg-green-600'
                    }`}
                    onClick={indexContent}
                    disabled={isLoading || !input.trim()}
                  >
                    {isLoading ? 'Indexing...' : 'Index'}
                  </button>
                </div>
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="useRAG"
                      checked={useRAG}
                      onChange={(e) => setUseRAG(e.target.checked)}
                      disabled={isLoading}
                    />
                    <label htmlFor="useRAG" className="text-sm text-gray-700">
                      Use RAG
                    </label>
                  </div>
                  <select
                    className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    disabled={isLoading}
                  >
                    <option value="llama3">llama3</option>
                    <option value="mistral-small">mistral-small</option>
                    <option value="deepseek-r1">deepseek-r1</option>
                    <option value="llama2">llama2</option>
                    <option value="codellama">codellama</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
