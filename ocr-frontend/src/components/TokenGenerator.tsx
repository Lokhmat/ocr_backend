"use client"

import type React from "react"
import { useState } from "react"
import { useAuth } from "../contexts/AuthContext"
import TokenModal from "./TokenModal"

interface TokenResponse {
  token: string
  expires_at: string | null
}

const TokenGenerator: React.FC = () => {
  const { fetchWithAuth } = useAuth()
  const [daysValid, setDaysValid] = useState<number | null>(30)
  const [isGenerating, setIsGenerating] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [tokenData, setTokenData] = useState<TokenResponse | null>(null)

  const handleGenerateToken = async () => {
    setIsGenerating(true)
    try {
      const response = await fetchWithAuth("/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          days_valid: daysValid,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to generate token")
      }

      const data: TokenResponse = await response.json()
      setTokenData(data)
      setShowModal(true)
    } catch (error) {
      console.error("Error generating token:", error)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="w-120 p-4 bg-white rounded-lg shadow-md">
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-500 mb-2">Token Validity</p>
          <div className="flex items-center justify-between space-x-1">
            <button
              onClick={() => setDaysValid(30)}
              className={`px-1 py-3 rounded-md text-sm ${
                daysValid === 30
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              30 days
            </button>
            <button
              onClick={() => setDaysValid(60)}
              className={`px-1 py-3 rounded-md text-sm ${
                daysValid === 60
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              60 days
            </button>
            <button
              onClick={() => setDaysValid(90)}
              className={`px-1 py-3 rounded-md text-sm ${
                daysValid === 90
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              90 days
            </button>
            <button
              onClick={() => setDaysValid(120)}
              className={`px-1 py-3 rounded-md text-sm ${
                daysValid === 120
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              120 days
            </button>
            <button
              onClick={() => setDaysValid(null)}
              className={`px-1 py-3 rounded-md text-sm ${
                daysValid === null
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Infinite
            </button>
          </div>
        </div>
        <button
          onClick={handleGenerateToken}
          disabled={isGenerating}
          className="w-full h-10 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isGenerating ? "Generating..." : "Create Token"}
        </button>
      </div>

      {showModal && tokenData && (
        <TokenModal
          token={tokenData.token}
          expiresAt={tokenData.expires_at}
          onClose={() => {
            setShowModal(false)
            setTokenData(null)
          }}
        />
      )}
    </div>
  )
}

export default TokenGenerator 