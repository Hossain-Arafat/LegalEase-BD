import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, AlertCircle, Scale } from 'lucide-react';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'আসসালামু আলাইকুম! আমি আপনার বাংলাদেশি আইনি সহায়ক। আমি কীভাবে আপনাকে সাহায্য করতে পারি? (Hello! I am your Bangladeshi legal assistant. How can I help you?)'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const API_URL = import.meta.env.VITE_LLM_API_URL;
      
      if (!API_URL) {
        throw new Error('API URL not configured. Please check your .env file.');
      }

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      
      // Just use the response text directly
      let formattedResponse = data.response;
      
      // Add citations if available (keeping legal references)
      if (data.citations && data.citations.length > 0) {
        formattedResponse += '\n\n📚 **Legal References:**\n';
        data.citations.forEach(citation => {
          if (citation.act) {
            formattedResponse += `• ${citation.act}`;
            if (citation.section) formattedResponse += `, Section ${citation.section}`;
            if (citation.act_no) formattedResponse += ` (Act No. ${citation.act_no})`;
            formattedResponse += '\n';
          }
        });
      }

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: formattedResponse
      };

      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message || 'সংযোগ সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।');
      
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'দুঃখিত, সার্ভারে সমস্যা হয়েছে। অনুগ্রহ করে কিছুক্ষণ পরে আবার চেষ্টা করুন। (Sorry, there was a server issue. Please try again later.)'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full p-2">
              <Scale className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Legalease AI</h1>
              <p className="text-sm text-gray-500">স্মার্ট আইনি সহায়তা, আপনার হাতের মুঠোয়</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 animate-fade-in ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
                  <Scale className="w-4 h-4 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-800 shadow-md border border-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap break-words font-sans leading-relaxed">
                  {message.content}
                </div>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
                <Scale className="w-4 h-4 text-white animate-pulse" />
              </div>
              <div className="bg-white rounded-lg px-4 py-3 shadow-md border border-gray-200">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  <span className="text-gray-600">আইনি বিশ্লেষণ করা হচ্ছে...</span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="flex justify-center">
              <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 flex items-center gap-2 text-red-700">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="আপনার আইনি প্রশ্ন লিখুন... (Type your legal question...)"
              rows="1"
              className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-sans"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg px-6 py-2 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">প্রেরণ</span>
            </button>
          </div>
          
          {/* Disclaimer */}
          <div className="flex items-center justify-center gap-2 mt-3 text-xs text-gray-500">
            <AlertCircle className="w-3 h-3" />
            <span>
              এই চ্যাটবট আইনি পরামর্শের জন্য নয়, শুধুমাত্র তথ্যগত উদ্দেশ্যে। গুরুত্বপূর্ণ আইনি বিষয়ে পেশাদার আইনজীবীর সাথে পরামর্শ করুন।
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;