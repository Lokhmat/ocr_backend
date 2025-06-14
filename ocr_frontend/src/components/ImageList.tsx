"use client"

import type React from "react"
import { useState, useEffect, useRef, useCallback } from "react"
import { useAuth } from "../contexts/AuthContext"
import ReviewModal from "./ReviewModal"

interface Image {
  image_id: string
  s3_key: string
  status: string
  result_json: string
  created_at: string
}

interface ImagesResponse {
  images: Image[]
  next_cursor: string | null
}

const formatJson = (jsonString: string) => {
  try {
    // Replace single quotes with double quotes, but be careful not to replace escaped single quotes
    const sanitizedJson = jsonString.replace(/(?<!\\)'/g, '"')
    console.log("Sanitized JSON string:", sanitizedJson);
    const parsed = JSON.parse(sanitizedJson);
    const formatted = JSON.stringify(parsed, null, 4);
    console.log("Formatted JSON:", formatted);
    return formatted;
  } catch (error) {
    console.error("Error formatting JSON:", error);
    return jsonString;
  }
};

const ImageList: React.FC = () => {
  const [images, setImages] = useState<Image[]>([])
  const [nextCursor, setNextCursor] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedImage, setSelectedImage] = useState<Image | null>(null)
  const { fetchWithAuth, apiBaseUrl } = useAuth()
  const observer = useRef<IntersectionObserver | null>(null)
  const lastImageElementRef = useCallback((node: HTMLDivElement | null) => {
    if (isLoading) return
    if (observer.current) observer.current.disconnect()
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && nextCursor) {
        fetchImages(nextCursor)
      }
    })
    if (node) observer.current.observe(node)
  }, [isLoading, nextCursor])

  // Update the fetchImages function with better error handling
  const fetchImages = async (cursor?: string) => {
    if (isLoading) return // Prevent multiple simultaneous requests

    setIsLoading(true)
    setError(null)

    try {
      const url = cursor 
        ? `/images/list?cursor=${encodeURIComponent(cursor)}&limit=25` 
        : "/images/list?limit=25"

      console.log("Fetching images with authentication...")
      const response = await fetchWithAuth(url).catch((err) => {
        console.error("Network error fetching images:", err)
        throw new Error(`Network error: ${err.message || "Failed to connect to the server"}`)
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unknown error")
        throw new Error(`Failed to fetch images: ${response.status} - ${errorText}`)
      }

      const data: ImagesResponse = await response.json()
      console.log("Images fetched:", data.images.length)

      if (cursor) {
        // Append to existing images
        setImages(prev => [...prev, ...data.images])
      } else {
        // Replace existing images
        setImages(data.images)
      }

      setNextCursor(data.next_cursor)
    } catch (err: any) {
      console.error("Error fetching images:", err)
      setError(`Failed to load images: ${err.message}. Please check your connection and try again.`)
    } finally {
      setIsLoading(false)
    }
  }

  // Extract filename from s3_key
  const getFilename = (s3Key: string) => {
    return s3Key.split("/").pop() || s3Key
  }

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  // Handle image click
  const handleImageClick = async (imageId: string) => {
    try {
      const imageUrl = `${apiBaseUrl}/get-image?image_id=${encodeURIComponent(imageId)}`
      window.open(imageUrl, '_blank')
    } catch (error) {
      console.error("Error opening image:", error)
    }
  }

  // Handle review button click
  const handleReviewClick = (image: Image) => {
    setSelectedImage(image);
  };

  // Handle modal close
  const handleModalClose = () => {
    setSelectedImage(null);
  };

  // Handle successful save
  const handleSaveSuccess = () => {
    fetchImages(); // Refresh the image list
  };

  // Fetch images on mount and when refresh event is triggered
  useEffect(() => {
    fetchImages()

    const handleRefresh = () => {
      fetchImages()
    }

    window.addEventListener("refreshImageList", handleRefresh)
    return () => {
      window.removeEventListener("refreshImageList", handleRefresh)
      if (observer.current) observer.current.disconnect()
    }
  }, [])

  if (error) {
    return (
      <div className="w-[65%] mx-auto p-4 bg-red-50 text-red-700 rounded-md">
        {error}
      </div>
    )
  }

  if (isLoading && images.length === 0) {
    return (
      <div className="w-[65%] mx-auto p-4 text-center">
        <p className="text-gray-600">Loading images...</p>
      </div>
    )
  }

  if (images.length === 0) {
    return (
      <div className="w-[65%] mx-auto p-4 text-center">
        <p className="text-gray-600">No images uploaded yet.</p>
      </div>
    )
  }

  return (
    <div className="w-[65%] mx-auto mt-8">
      <div className="grid grid-cols-1 gap-4">
        {images.map((image, index) => (
          <div 
            key={image.image_id} 
            ref={index === images.length - 1 ? lastImageElementRef : null}
            className="bg-white p-4 rounded-lg shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 
                  className="text-lg font-medium text-gray-900 cursor-pointer hover:text-blue-600"
                  onClick={() => handleImageClick(image.image_id)}
                >
                  {getFilename(image.s3_key)}
                </h3>
                <p className="text-sm text-gray-500">
                  Uploaded: {formatDate(image.created_at)}
                </p>
                <p className="text-sm text-gray-500">
                  Status: {image.status}
                </p>
              </div>
              {image.result_json && (
                <button
                  onClick={() => handleReviewClick(image)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Edit result
                </button>
              )}
            </div>
            {image.result_json && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700">Results:</h4>
                <div className="mt-2 p-4 bg-gray-50 rounded-lg overflow-x-auto">
                  <pre className="whitespace-pre-wrap break-words">
                    {formatJson(image.result_json)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      {isLoading && images.length > 0 && (
        <div className="w-full text-center py-4">
          <p className="text-gray-600">Loading more images...</p>
        </div>
      )}

      {selectedImage && (
        <ReviewModal
          isOpen={true}
          onClose={handleModalClose}
          imageId={selectedImage.image_id}
          imageUrl={`${apiBaseUrl}/get-image?image_id=${encodeURIComponent(selectedImage.image_id)}`}
          initialJson={selectedImage.result_json}
          onSave={handleSaveSuccess}
        />
      )}
    </div>
  )
}

export default ImageList
