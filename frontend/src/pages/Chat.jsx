import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Home as HomeIcon } from 'lucide-react';
import Chatbot from '../components/Chatbot';

const Chat = () => {
  const navigate = useNavigate();

  return (
    <div className="relative">
      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        className="fixed top-4 left-4 z-50 bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200"
        aria-label="Back to Home"
      >
        <ArrowLeft className="w-5 h-5 text-gray-700" />
      </button>
      
      {/* Optional: Home button */}
      <button
        onClick={() => navigate('/')}
        className="fixed top-4 left-20 z-50 bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200"
        aria-label="Home"
      >
        <HomeIcon className="w-5 h-5 text-gray-700" />
      </button>

      {/* Chatbot Component */}
      <Chatbot />
    </div>
  );
};

export default Chat;