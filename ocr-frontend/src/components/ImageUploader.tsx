"use client"

import type React from "react"
import { useState, useRef } from "react"
import { useAuth } from "../contexts/AuthContext"

interface UploadResponse {
  image_id: string
  status: string
}

const ImageUploader: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)
  const [workload, setWorkload] = useState<"on_premise" | "cloud">("cloud")
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { fetchWithAuth } = useAuth()

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()

    const files = fileInputRef.current?.files
    if (!files || files.length === 0) {
      setUploadStatus("Please select at least one image to upload.")
      return
    }

    if (files.length > 2) {
      setUploadStatus("You can upload a maximum of 2 images at once.")
      return
    }

    setIsUploading(true)
    setUploadStatus("Uploading images...")

    try {
      const formData = new FormData()
      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i])
      }

      const uploadUrl = `/upload-images?workload=${workload}`
      const response = await fetchWithAuth(uploadUrl, {
        method: "POST",
        body: formData,
      }).catch((err) => {
        console.error("Network error during upload:", err)
        throw new Error(`Network error: ${err.message || "Failed to connect to the server"}`)
      })

      if (!response.ok) {
        const errorResponse = await response.json().catch(() => ({ details: "Unknown error" }))
        throw new Error(errorResponse.detail)
      }

      const data: UploadResponse[] = await response.json()
      setUploadStatus(`Successfully uploaded ${data.length} image(s).`)

      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }

      window.dispatchEvent(new CustomEvent("refreshImageList"))
    } catch (error: any) {
      console.error("Upload error:", error)
      setUploadStatus(`Upload failed: ${error.message}`)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Upload Images</h2>
      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select images (up to 2)
          </label>
          <input
            type="file"
            ref={fileInputRef}
            accept="image/*"
            multiple
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Processing:</label>
          <select
            value={workload}
            onChange={(e) => setWorkload(e.target.value as "on_premise" | "cloud")}
            className="border border-gray-300 rounded px-3 py-1 text-sm"
          >
            <option value="cloud">Cloud</option>
            <option value="on_premise">On Premise</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={isUploading}
          className={`w-full py-2 px-4 rounded-md text-white font-medium ${
            isUploading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {isUploading ? "Uploading..." : "Upload Images"}
        </button>

        {uploadStatus && (
          <p className={`text-sm ${uploadStatus.includes("failed") ? "text-red-600" : "text-green-600"}`}>
            {uploadStatus}
          </p>
        )}
      </form>
    </div>
  )
}

export default ImageUploader
