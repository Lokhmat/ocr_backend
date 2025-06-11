"use client"

import type React from "react"
import { createContext, useContext, useState, type ReactNode, useEffect } from "react"
import { useRouter } from "next/navigation"

// Define the base URL for API calls - ensure this matches your backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:80"

// Debug helper for authentication actions
const logAuthAction = (action: string, details?: any) => {
  console.log(`Auth: ${action}`, details || "")
}

interface AuthContextType {
  currentUser: string | null
  accessToken: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>
  isLoading: boolean
  apiBaseUrl: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const router = useRouter()
  const [currentUser, setCurrentUser] = useState<string | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [refreshPromise, setRefreshPromise] = useState<Promise<string> | null>(null)

  // Load tokens from localStorage on initial mount
  useEffect(() => {
    const storedAccessToken = localStorage.getItem("access_token")
    const storedRefreshToken = localStorage.getItem("refresh_token")
    const storedUser = localStorage.getItem("current_user")

    if (storedAccessToken && storedRefreshToken && storedUser) {
      setAccessToken(storedAccessToken)
      setRefreshToken(storedRefreshToken)
      setCurrentUser(storedUser)
    } else {
      // If no tokens are available, redirect to login
      router.push("/login")
    }
  }, [router])

  // Function to refresh the token
  const refreshTokenFn = async (): Promise<string> => {
    if (refreshPromise) return refreshPromise

    const newPromise = new Promise<string>(async (resolve, reject) => {
      try {
        setIsRefreshing(true)
        console.log("Attempting token refresh...")

        const currentRefreshToken = localStorage.getItem("refresh_token")
        if (!currentRefreshToken) {
          throw new Error("No refresh token available")
        }

        const response = await fetch(`${API_BASE_URL}/refresh`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: currentRefreshToken }),
        })

        if (!response.ok) {
          const errorText = await response.text().catch(() => "Unknown error")
          throw new Error(`Failed to refresh token: ${response.status} - ${errorText}`)
        }

        const data = await response.json()
        console.log("Token refreshed successfully")
        
        // Update both tokens
        setAccessToken(data.access_token)
        setRefreshToken(data.refresh_token)
        
        // Store tokens in localStorage
        localStorage.setItem("access_token", data.access_token)
        localStorage.setItem("refresh_token", data.refresh_token)
        
        setIsRefreshing(false)
        resolve(data.access_token)
      } catch (error) {
        console.error("Token refresh error:", error)
        setIsRefreshing(false)
        setCurrentUser(null)
        setAccessToken(null)
        setRefreshToken(null)
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        localStorage.removeItem("current_user")
        router.push("/login")
        reject(error)
      }
    })

    setRefreshPromise(newPromise)

    // Clear the promise after it resolves or rejects
    newPromise
      .then(() => setRefreshPromise(null))
      .catch(() => setRefreshPromise(null))

    return newPromise
  }

  // Custom fetch function with authentication
  const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
    setIsLoading(true)

    // Check if we have an access token
    const currentAccessToken = localStorage.getItem("access_token")
    if (!currentAccessToken) {
      router.push("/login")
      throw new Error("No access token available")
    }

    // Prepare headers with auth token if available
    const headers = new Headers(options.headers || {})
    
    // Only set Content-Type if it's not a FormData request
    if (!(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json")
    }
    
    headers.set("Authorization", `Bearer ${currentAccessToken}`)

    // Prepare the request
    const requestOptions: RequestInit = {
      ...options,
      headers,
    }

    const fullUrl = url.startsWith("http") ? url : `${API_BASE_URL}${url}`
    console.log(`Fetching: ${fullUrl}`, { headers: Object.fromEntries(headers.entries()) })

    try {
      // Make the request
      const response = await fetch(fullUrl, requestOptions)
      console.log(`Response status: ${response.status} for ${url}`)
      console.log(`Response headers:`, Object.fromEntries(response.headers.entries()))

      // If unauthorized, try to refresh the token
      if (response.status === 401) {
        console.log("Received 401, attempting token refresh")
        try {
          // Get a fresh token
          const newToken = await refreshTokenFn()
          console.log("Got new token, retrying original request")

          // Update the Authorization header with the new token
          headers.set("Authorization", `Bearer ${newToken}`)

          // Retry the original request with the new token
          const retryResponse = await fetch(fullUrl, {
            ...requestOptions,
            headers,
          })

          console.log(`Retry response status: ${retryResponse.status}`)

          // If still unauthorized, logout
          if (retryResponse.status === 401) {
            console.log("Still unauthorized after token refresh, logging out")
            logout()
          }

          setIsLoading(false)
          return retryResponse
        } catch (error) {
          // If refresh fails, logout
          console.error("Token refresh failed during request retry:", error)
          logout()
          setIsLoading(false)
          throw error
        }
      }

      setIsLoading(false)
      return response
    } catch (error) {
      setIsLoading(false)
      console.error(`Fetch error for ${url}:`, error)
      throw error
    }
  }

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      console.log(`Attempting login for ${email} to ${API_BASE_URL}/login`)
      
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      console.log(`Login response status: ${response.status}`)
      console.log(`Login response headers:`, Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unknown error")
        throw new Error(`Login failed: ${response.status} - ${errorText}`)
      }

      const data = await response.json()
      console.log("Login successful, tokens received:", data)
      
      // Store both tokens
      setAccessToken(data.access_token)
      setRefreshToken(data.refresh_token)
      setCurrentUser(email)
      
      // Store tokens in localStorage
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      localStorage.setItem("current_user", email)

      // Redirect to home page after successful login
      router.push("/")
    } catch (error) {
      console.error("Login error:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unknown error")
        throw new Error(`Registration failed: ${response.status} - ${errorText}`)
      }

      const data = await response.json()
      
      // Store both tokens
      setAccessToken(data.access_token)
      setRefreshToken(data.refresh_token)
      setCurrentUser(email)
      
      // Store tokens in localStorage
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      localStorage.setItem("current_user", email)

      // Redirect to home page after successful registration
      router.push("/")
    } catch (error) {
      console.error("Registration error:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setAccessToken(null)
    setRefreshToken(null)
    setCurrentUser(null)
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("current_user")
    router.push("/login")
  }

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        accessToken,
        login,
        register,
        logout,
        fetchWithAuth,
        isLoading,
        apiBaseUrl: API_BASE_URL,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
