import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Home({ user }: any) {
  const router = useRouter()

  useEffect(() => {
    if (user) {
      router.push('/chat')
    } else {
      router.push('/login')
    }
  }, [user, router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
    </div>
  )
}
