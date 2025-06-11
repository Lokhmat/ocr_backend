"use client"

import type React from "react"
import { useState } from "react"

interface TokenModalProps {
  token: string
  expiresAt: string | null
  onClose: () => void
}

const TokenModal: React.FC<TokenModalProps> = ({ token, expiresAt, onClose }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(token)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy token: ", err)
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never"
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-semibold mb-4">Your API Token</h2>
        
        <div className="mb-4">
          <p className="text-sm text-gray-500 mb-2">Token</p>
          <div className="flex items-center">
            <code className="text-sm bg-gray-100 p-2 rounded flex-1 overflow-x-auto">
              {token}
            </code>
            <button
              onClick={handleCopy}
              className="ml-2 h-10 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-500">Expires at:</p>
          <p className="text-sm font-medium">{formatDate(expiresAt)}</p>
        </div>

        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <p className="text-sm text-yellow-700">
            ⚠️ This is the only time you will see this token. Please make sure to save it securely.
          </p>
        </div>

        <button
          onClick={onClose}
          className="w-full h-10 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  )
}

export default TokenModal 