"use client"

import { AuthProvider } from "../../src/contexts/AuthContext"
import MainPage from "../../src/pages/MainPage"

export default function Page() {
  return (
    <AuthProvider>
      <MainPage />
    </AuthProvider>
  )
}
