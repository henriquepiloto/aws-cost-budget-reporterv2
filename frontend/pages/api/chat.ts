import type { NextApiRequest, NextApiResponse } from 'next'
import { verifyToken } from '@/lib/auth'
import { query } from '@/lib/db'
import axios from 'axios'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  // Verify authentication
  const token = req.headers.authorization?.replace('Bearer ', '')
  if (!token) {
    return res.status(401).json({ message: 'No token provided' })
  }

  const user = verifyToken(token)
  if (!user) {
    return res.status(401).json({ message: 'Invalid token' })
  }

  const { message, userId } = req.body

  if (!message) {
    return res.status(400).json({ message: 'Message is required' })
  }

  try {
    // Log user message
    await query(
      'INSERT INTO chat_logs (user_id, message, sender, created_at) VALUES (?, ?, ?, NOW())',
      [userId, message, 'user']
    )

    // Get cost context from API
    const apiUrl = process.env.API_URL || 'https://costs.selectsolucoes.com'
    let costContext = ''
    
    try {
      const costResponse = await axios.get(`${apiUrl}/costs/overview`, {
        timeout: 5000
      })
      costContext = `Contexto de custos AWS atual: ${JSON.stringify(costResponse.data)}`
    } catch (error) {
      console.log('Could not fetch cost context:', error)
      costContext = 'Contexto de custos não disponível no momento.'
    }

    // Call Bedrock via cost-reporter API
    const bedrockResponse = await axios.post(`${apiUrl}/chat`, {
      message: message,
      context: costContext,
      user_id: userId
    }, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    const assistantResponse = bedrockResponse.data.response || 'Desculpe, não consegui processar sua solicitação.'

    // Log assistant response
    await query(
      'INSERT INTO chat_logs (user_id, message, sender, created_at) VALUES (?, ?, ?, NOW())',
      [userId, assistantResponse, 'assistant']
    )

    res.status(200).json({ response: assistantResponse })
  } catch (error) {
    console.error('Chat error:', error)
    
    // Log error
    await query(
      'INSERT INTO chat_logs (user_id, message, sender, created_at) VALUES (?, ?, ?, NOW())',
      [userId, 'Erro interno do sistema', 'system']
    )

    res.status(500).json({ 
      response: 'Desculpe, ocorreu um erro interno. Nossa equipe foi notificada e está trabalhando para resolver o problema.' 
    })
  }
}
