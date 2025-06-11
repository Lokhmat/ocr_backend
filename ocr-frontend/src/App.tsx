"use client"

import React from "react"
import { useAuth } from "./contexts/AuthContext"
import { useRouter } from "next/navigation"

// Protected route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentUser } = useAuth()
  const router = useRouter()

  React.useEffect(() => {
    if (!currentUser) {
      router.push("/login")
    }
  }, [currentUser, router])

  if (!currentUser) {
    return null
  }

  return <>{children}</>
}

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <ProtectedRoute>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-8">
            <h1 className="text-3xl font-bold text-gray-900">Image Processing App</h1>
            <p className="text-gray-600">Welcome to the image processing application.</p>
          </div>
        </div>
      </ProtectedRoute>
    </div>
  )
}

export default App
