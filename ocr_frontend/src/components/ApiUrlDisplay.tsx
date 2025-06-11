"use client"

import type React from "react"
import { useState } from "react"
import { useAuth } from "../contexts/AuthContext"

const ApiUrlDisplay: React.FC = () => {
  const { apiBaseUrl } = useAuth()
  const [copied, setCopied] = useState(false)
  const apiUrl = `${apiBaseUrl}`

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(apiUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy text: ", err)
    }
  }

  return (
    <div className="w-120 p-4 bg-white rounded-lg shadow-md">
      <div className="flex items-center justify-between">
        <div className="flex-1 mr-4">
          <p className="text-sm text-gray-500 mb-1">API URL</p>
          <div className="flex items-center">
            <code className="text-sm bg-gray-100 p-2 rounded flex-1 overflow-x-auto">
              {apiUrl}
            </code>
          </div>
        </div>
        <button
          onClick={handleCopy}
          className="h-10 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
    </div>
  )
}

export default ApiUrlDisplay 