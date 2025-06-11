"use client"

import type React from "react"
import Link from "next/link"
import { useAuth } from "../contexts/AuthContext"
import { useRouter } from "next/navigation"
import { ApiKeyDialog } from "./ApiKeyDialog"

const Header: React.FC = () => {
  const { currentUser, logout } = useAuth()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              {/* Placeholder logo */}
              <div className="h-8 w-8 bg-indigo-600 rounded-full"></div>
            </div>
            <div className="ml-6 flex items-center">
              <Link href="/app" className="px-3 py-2 rounded-md text-sm font-medium text-gray-900 hover:bg-gray-100">
                Home
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <ApiKeyDialog />
            <div className="flex-shrink-0">
              <span className="text-sm font-medium text-gray-700 mr-4">{currentUser}</span>
              <button
                onClick={handleLogout}
                className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
