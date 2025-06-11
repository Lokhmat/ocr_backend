"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "../contexts/AuthContext"

export function ApiKeyDialog() {
  const [open, setOpen] = React.useState(false)
  const [apiKey, setApiKey] = React.useState("")
  const [error, setError] = React.useState<string | null>(null)
  const { fetchWithAuth } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const response = await fetchWithAuth("/user/cloud-key", {
        method: "PUT",
        body: JSON.stringify({ cloud_key: apiKey }),
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unknown error")
        throw new Error(`Failed to update API key: ${response.status} - ${errorText}`)
      }

      setOpen(false)
      setApiKey("")
    } catch (error: any) {
      console.error("Error updating API key:", error)
      setError(error.message || "Failed to update API key")
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">Specify API Key</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>OpenRouter API Key</DialogTitle>
          <div className="text-sm text-muted-foreground">
            <p className="mb-2">To use cloud processing, you need to provide your OpenRouter API key. You can get one by:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Visit <a href="https://openrouter.ai" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">openrouter.ai</a></li>
              <li>Sign up or log in to your account</li>
              <li>Go to your dashboard and copy your API key</li>
              <li>Paste it below</li>
            </ol>
          </div>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="apiKey" className="text-right">
                API Key
              </Label>
              <Input
                id="apiKey"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="col-span-3"
                placeholder="sk-or-..."
              />
            </div>
            {error && (
              <div className="text-red-500 text-sm mt-2">
                {error}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button type="submit">Save changes</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
} 