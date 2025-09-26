import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { useEffect, useState } from 'react'
import { verifyToken } from '@/lib/auth'

export default function App({ Component, pageProps }: AppProps) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      const userData = verifyToken(token)
      if (userData) {
        setUser(userData)
      } else {
        localStorage.removeItem('token')
      }
    }
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return <Component {...pageProps} user={user} setUser={setUser} />
}
