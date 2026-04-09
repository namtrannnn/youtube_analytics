import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2 } from 'lucide-react';
import { api } from '../api';
import ReactMarkdown from 'react-markdown';

export default function ChatWindow({ taskId, initialChat = [] }) {
  
  // Khởi tạo State: Nếu có lịch sử cũ thì dùng nó, nếu không thì dùng câu chào mặc định
  const [messages, setMessages] = useState(() => {
    if (initialChat && initialChat.length > 0) {
      return initialChat;
    }
    return [
      { role: 'bot', content: 'Chào bạn! Tôi đã học xong dữ liệu của video này. Bạn muốn hỏi gì?' }
    ];
  });

  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef(null);

  // const scrollToBottom = () => {
  //   messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  // };

  // useEffect(scrollToBottom, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsThinking(true);

    try {
      const botAnswer = await api.chatWithData(taskId, userMsg);
      
      setMessages(prev => [...prev, { role: 'bot', content: botAnswer }]);
    } catch (error) {
      console.error("Lỗi Chatbot:", error);
      setMessages(prev => [...prev, { role: 'bot', content: 'Xin lỗi, tôi gặp lỗi khi kết nối server.' }]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
      <div className="bg-slate-50 p-4 border-b border-slate-200 flex items-center gap-2">
        <Bot className="w-5 h-5 text-blue-600" />
        <span className="font-semibold text-slate-700">Trợ lý AI (Hỏi đáp trên dữ liệu thu nhập)</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-3 ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-slate-100 text-slate-800 rounded-bl-none'
            }`}>
              {msg.role === 'bot' ? (
                 <ReactMarkdown className="prose prose-sm">{msg.content}</ReactMarkdown>
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}
        {isThinking && (
          <div className="flex justify-start">
             <div className="bg-slate-100 p-3 rounded-lg rounded-bl-none flex items-center gap-2 text-slate-500 text-sm">
                <Loader2 className="w-4 h-4 animate-spin" /> Đang suy nghĩ...
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-4 border-t border-slate-200 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ví dụ: Mọi người chê gì về âm thanh?"
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        />
        <button 
          type="submit" 
          disabled={isThinking}
          className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg disabled:opacity-50"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
}