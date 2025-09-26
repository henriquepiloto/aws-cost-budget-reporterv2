import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface ChatConfig {
  primaryColor: string;
  secondaryColor: string;
  botName: string;
  welcomeMessage: string;
  theme: 'light' | 'dark';
}

export default function Chat() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatConfig, setChatConfig] = useState<ChatConfig>({
    primaryColor: '#3b82f6',
    secondaryColor: '#1e40af',
    botName: 'Cloudinho',
    welcomeMessage: 'Olá! Sou o Cloudinho, seu assistente de análise de custos AWS. Como posso ajudar você hoje?',
    theme: 'light'
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChatConfig();
    addWelcomeMessage();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatConfig = async () => {
    try {
      const response = await fetch('https://ewapsbyof8.execute-api.us-east-1.amazonaws.com/prod/chat/config');
      if (response.ok) {
        const data = await response.json();
        if (data.config) {
          setChatConfig(data.config);
        }
      }
    } catch (error) {
      console.error('Error loading chat config:', error);
    }
  };

  const addWelcomeMessage = () => {
    const welcomeMessage: Message = {
      id: 'welcome',
      content: chatConfig.welcomeMessage,
      sender: 'bot',
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('https://ewapsbyof8.execute-api.us-east-1.amazonaws.com/prod/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      });

      const data = await response.json();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || 'Desculpe, não consegui processar sua mensagem.',
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Desculpe, ocorreu um erro. Tente novamente.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={`min-h-screen ${chatConfig.theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <div 
        className="border-b shadow-sm"
        style={{ 
          backgroundColor: chatConfig.theme === 'dark' ? '#1f2937' : 'white',
          borderBottomColor: chatConfig.primaryColor 
        }}
      >
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
              style={{ backgroundColor: chatConfig.primaryColor }}
            >
              {chatConfig.botName.charAt(0)}
            </div>
            <div>
              <h1 className={`text-xl font-bold ${chatConfig.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {chatConfig.botName}
              </h1>
              <p className={`text-sm ${chatConfig.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
                Assistente de Análise de Custos AWS
              </p>
            </div>
          </div>
          <button
            onClick={() => router.push('/login')}
            className="px-4 py-2 border rounded-md text-sm hover:bg-gray-50"
          >
            Admin
          </button>
        </div>
      </div>

      {/* Chat Container */}
      <div className="container mx-auto max-w-4xl h-[calc(100vh-120px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start gap-3 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white"
                  style={{ 
                    backgroundColor: message.sender === 'user' ? chatConfig.secondaryColor : chatConfig.primaryColor 
                  }}
                >
                  {message.sender === 'user' ? 'U' : 'B'}
                </div>
                <div className={`rounded-lg shadow-sm border p-3 ${chatConfig.theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white'}`}>
                  <p className={`text-sm ${chatConfig.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    {message.content}
                  </p>
                  <p className={`text-xs mt-2 ${chatConfig.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    {message.timestamp.toLocaleTimeString('pt-BR', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-start gap-3 max-w-[80%]">
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white"
                  style={{ backgroundColor: chatConfig.primaryColor }}
                >
                  B
                </div>
                <div className={`rounded-lg shadow-sm border p-3 ${chatConfig.theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white'}`}>
                  <div className="flex items-center gap-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className={`text-sm ${chatConfig.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
                      {chatConfig.botName} está digitando...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t" style={{ borderTopColor: chatConfig.theme === 'dark' ? '#374151' : '#e5e7eb' }}>
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Digite sua pergunta sobre custos AWS..."
              disabled={isLoading}
              className={`flex-1 px-3 py-2 border rounded-md ${chatConfig.theme === 'dark' ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              style={{ backgroundColor: chatConfig.primaryColor }}
              className="px-4 py-2 text-white rounded-md hover:opacity-90 disabled:opacity-50"
            >
              Enviar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
