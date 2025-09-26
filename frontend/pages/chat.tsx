import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import axios from 'axios'
import { Send, LogOut, User } from 'lucide-react'

interface Message {
  id: string
  text: string
  sender: 'user' | 'assistant'
  timestamp: Date
}

export default function Chat({ user, setUser }: any) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }

    // Welcome message
    setMessages([{
      id: '1',
      text: `Olá ${user.username}! Sou o Cloudinho, seu assistente FinOps. Como posso ajudar você hoje com análises de custos AWS?`,
      sender: 'assistant',
      timestamp: new Date()
    }])
  }, [user, router])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      const response = await axios.post('/api/chat', {
        message: inputMessage,
        userId: user.id
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        sender: 'assistant',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        sender: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setUser(null)
    router.push('/login')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!user) {
    return <div>Redirecionando...</div>
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">C</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Cloudinho FinOps</h1>
            <p className="text-sm text-gray-500">Assistente de Custos AWS</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <User size={16} />
            <span>{user.username}</span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-1 text-gray-600 hover:text-gray-900"
          >
            <LogOut size={16} />
            <span>Sair</span>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`message-bubble px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-primary text-white'
                  : 'bg-white text-gray-900 shadow-sm border'
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
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-900 shadow-sm border px-4 py-2 rounded-lg">
              <div className="loading-dots">Cloudinho está pensando...</div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua pergunta sobre custos AWS..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            rows={2}
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !inputMessage.trim()}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}
