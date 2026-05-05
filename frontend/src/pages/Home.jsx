import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Scale, MessageCircle, BookOpen, Shield, Users, Zap, ArrowRight, CheckCircle, Globe, Sparkles } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: '35,472+ Legal Chunks',
      description: 'Comprehensive coverage of Bangladeshi acts and legal documents'
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: 'Bilingual Support',
      description: 'Get answers in both English and Bengali languages'
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Ultra-Fast Responses',
      description: 'Powered by Groq LLaMA-3-70B for lightning-fast answers'
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Cited Sources',
      description: 'Every answer comes with legal references and citations'
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: 'Hybrid Search',
      description: 'Combines semantic + keyword search for accuracy'
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'AI-Powered',
      description: 'Advanced RAG architecture for precise legal answers'
    }
  ];

  const stats = [
    { value: '35K+', label: 'Legal Chunks' },
    { value: '2', label: 'Languages' },
    { value: '<2s', label: 'Response Time' },
    { value: 'FREE', label: 'To Use' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-grid-gray-900/[0.02] bg-[size:20px_20px]" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-28">
          {/* Badge */}
          <div className="flex justify-center mb-6">
            <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium">
              <Scale className="w-4 h-4" />
              <span>LegalEase BD - AI Legal Assistant</span>
            </div>
          </div>

          {/* Main Title */}
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-6">
              Your AI-Powered Legal
              <br />
              Assistant for Bangladesh
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Get instant, accurate answers to your legal questions about Bangladeshi law.
              Powered by LLaMA-3-70B and comprehensive legal databases.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/chat')}
                className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <MessageCircle className="w-5 h-5" />
                Start Chatting Now
                <ArrowRight className="w-5 h-5" />
              </button>
              <button
                onClick={() => {
                  const element = document.getElementById('features');
                  element?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="inline-flex items-center gap-2 bg-white text-gray-700 px-8 py-4 rounded-xl text-lg font-semibold border border-gray-300 hover:border-blue-500 hover:shadow-lg transition-all duration-200"
              >
                Learn More
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 mt-16 pt-8 border-t border-gray-200">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                  <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need in a Legal Assistant
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              LegalEase BD combines cutting-edge AI with comprehensive legal databases
              to provide you with accurate, reliable legal information.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-300"
              >
                <div className="bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg w-12 h-12 flex items-center justify-center text-blue-600 group-hover:scale-110 transition-transform duration-300 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How LegalEase BD Works
            </h2>
            <p className="text-xl text-gray-600">
              Advanced RAG architecture for precise legal answers
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center text-2xl font-bold text-blue-600 mx-auto mb-4 shadow-md">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Ask Your Question</h3>
              <p className="text-gray-600">
                Type your legal question in English or Bengali
              </p>
            </div>

            <div className="text-center">
              <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center text-2xl font-bold text-blue-600 mx-auto mb-4 shadow-md">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Searches Laws</h3>
              <p className="text-gray-600">
                Hybrid search scans 35,000+ legal chunks for relevant information
              </p>
            </div>

            <div className="text-center">
              <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center text-2xl font-bold text-blue-600 mx-auto mb-4 shadow-md">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Get Cited Answers</h3>
              <p className="text-gray-600">
                Receive structured responses with legal references
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Get Legal Answers?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Start chatting with LegalEase BD now - It's free!
          </p>
          <button
            onClick={() => navigate('/chat')}
            className="inline-flex items-center gap-2 bg-white text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-xl transition-all duration-200"
          >
            <MessageCircle className="w-5 h-5" />
            Start Your First Conversation
            <ArrowRight className="w-5 h-5" />
          </button>
          
          <div className="mt-8 flex items-center justify-center gap-4 text-sm text-blue-100">
            <div className="flex items-center gap-1">
              <CheckCircle className="w-4 h-4" />
              <span>Free to use</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle className="w-4 h-4" />
              <span>No registration</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle className="w-4 h-4" />
              <span>Instant answers</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex justify-center mb-4">
            <Scale className="w-8 h-8 text-blue-400" />
          </div>
          <p className="text-sm">
            LegalEase BD - AI Legal Assistant for Bangladeshi Law
          </p>
          <p className="text-xs mt-2">
            This is an AI-powered legal information tool. For specific legal advice, please consult a qualified lawyer.
          </p>
          <p className="text-xs mt-4">
            © 2026 LegalEase BD. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;