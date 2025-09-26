import type { AppProps } from 'next/app'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import '../styles/globals.css'

// Import components
import Chat from './chat'
import Login from './login'
import Admin from './admin'

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter()
  const [currentPath, setCurrentPath] = useState('/')

  useEffect(() => {
    setCurrentPath(router.asPath)
  }, [router.asPath])

  // SPA routing
  if (currentPath === '/' || currentPath === '/chat') {
    return <Chat />
  }
  
  if (currentPath === '/login') {
    return <Login />
  }
  
  if (currentPath === '/admin') {
    return <Admin />
  }

  return <Component {...pageProps} />
}
