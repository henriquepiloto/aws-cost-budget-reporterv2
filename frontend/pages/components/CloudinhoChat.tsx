import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, Send, X, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  type: 'user' | 'cloudinho';
  content: string;
  timestamp: Date;
}

interface CloudinhoChatProps {
  cliente?: string;
  branding?: {
    primary_color: string;
    secondary_color: string;
    accent_color: string;
    cloudinho_avatar?: string;
  };
}

export default function CloudinhoChat({ cliente, branding }: CloudinhoChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const colors = {
    primary: branding?.primary_color || '#1f2937',
    secondary: branding?.secondary_color || '#3b82f6',
    accent: branding?.accent_color || '#10b981'
  };

  // Initial greeting when chat opens
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const greeting: Message = {
        id: 'greeting',
        type: 'cloudinho',
        content: `Olá! Eu sou o Cloudinho 👋 

Sou seu assistente especialista em custos AWS aqui na Select Soluções! 

Como posso ajudar você hoje? Posso:
- 📊 Analisar seus custos atuais
- 📈 Mostrar tendências e previsões  
- 💰 Identificar oportunidades de economia
- 🚨 Explicar alertas importantes
- 🎯 Sugerir otimizações personalizadas

${cliente ? `Vejo que você está consultando dados do **${cliente}**. ` : ''}O que gostaria de saber?`,
        timestamp: new Date()
      };
      setMessages([greeting]);
    }
  }, [isOpen, cliente]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue,
          cliente: cliente || ''
        })
      });

      const data = await response.json();

      const cloudinhoMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'cloudinho',
        content: data.response || 'Desculpe, tive um problema para processar sua pergunta. Pode tentar novamente?',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, cloudinhoMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'cloudinho',
        content: 'Ops! 😅 Tive um problema de conexão. Pode tentar novamente em alguns segundos?',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <motion.button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 w-16 h-16 rounded-full shadow-lg flex items-center justify-center text-white z-50 ${
          isOpen ? 'hidden' : 'block'
        }`}
        style={{ backgroundColor: colors.secondary }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
      >
        <MessageCircle size={24} />
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
          <Bot size={12} className="text-white" />
        </div>
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.3 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.3 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden border"
          >
            {/* Header */}
            <div 
              className="p-4 text-white flex items-center justify-between"
              style={{ backgroundColor: colors.primary }}
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                  {branding?.cloudinho_avatar ? (
                    <img 
                      src={branding.cloudinho_avatar} 
                      alt="Cloudinho" 
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <Bot size={20} />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold">Cloudinho</h3>
                  <p className="text-xs opacity-90">Assistente AWS</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-white/20 rounded-full transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[80%] ${
                    message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}>
                    {/* Avatar */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user' 
                        ? 'bg-gray-200' 
                        : 'text-white'
                    }`}
                    style={message.type === 'cloudinho' ? { backgroundColor: colors.accent } : {}}
                    >
                      {message.type === 'user' ? (
                        <User size={16} className="text-gray-600" />
                      ) : branding?.cloudinho_avatar ? (
                        <img 
                          src={branding.cloudinho_avatar} 
                          alt="Cloudinho" 
                          className="w-6 h-6 rounded-full"
                        />
                      ) : (
                        <Bot size={16} />
                      )}
                    </div>

                    {/* Message Bubble */}
                    <div className={`rounded-2xl px-4 py-2 ${
                      message.type === 'user'
                        ? 'text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                    style={message.type === 'user' ? { backgroundColor: colors.secondary } : {}}
                    >
                      {message.type === 'cloudinho' ? (
                        <ReactMarkdown 
                          className="prose prose-sm max-w-none"
                          components={{
                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                            strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                            ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                            li: ({ children }) => <li className="mb-1">{children}</li>
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      ) : (
                        <p className="text-sm">{message.content}</p>
                      )}
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-white/70' : 'text-gray-500'
                      }`}>
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white"
                      style={{ backgroundColor: colors.accent }}
                    >
                      <Bot size={16} />
                    </div>
                    <div className="bg-gray-100 rounded-2xl px-4 py-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t bg-gray-50">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Digite sua pergunta..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  style={{ backgroundColor: colors.secondary }}
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
