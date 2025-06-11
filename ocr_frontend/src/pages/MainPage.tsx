"use client"

import type React from "react"
import Header from "../components/Header"
import ImageUploader from "../components/ImageUploader"
import ImageList from "../components/ImageList"
import ApiUrlDisplay from "../components/ApiUrlDisplay"
import TokenGenerator from "../components/TokenGenerator"
import FloatingDocButton from "../components/FloatingDocButton"

const MainPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex flex-col items-center">
            <div className="flex w-full max-w-4xl justify-between items-start gap-8">
              <ImageUploader />
              <div className="space-y-4">
                <ApiUrlDisplay />
                <TokenGenerator />
              </div>
              <FloatingDocButton />
            </div>
            <ImageList />
          </div>
        </div>
      </main>
    </div>
  )
}

export default MainPage
