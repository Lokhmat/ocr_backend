"use client"

import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from "@/components/ui/dialog"

export default function FloatingDocButton() {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Dialog>
        <DialogTrigger asChild>
          <button className="h-12 w-12 rounded-full bg-primary text-white text-xl shadow-lg hover:bg-primary/90 transition-colors">
            ?
          </button>
        </DialogTrigger>
        <DialogContent>
          <>
            <DialogHeader>
              <DialogTitle>API Documentation</DialogTitle>
              <DialogDescription>
                Learn how to access and use the image processing API.
              </DialogDescription>
            </DialogHeader>

            <div className="text-sm text-muted-foreground space-y-4 max-h-[70vh] overflow-y-auto pr-2">
              <section>
                <h3 className="font-semibold">🔐 Authentication</h3>
                <p>
                  Before calling any API endpoints, you must first generate a token.
                </p>
                <ol className="list-decimal list-inside pl-4">
                  <li>Click the "Generate Token" button in the UI.</li>
                  <li>Copy the token shown.</li>
                  <li>
                    Include this token in your requests using the{" "}
                    <code className="px-1 bg-accent text-accent-foreground rounded">
                      Authorization: Bearer &lt;your_token&gt;
                    </code>{" "}
                    header.
                  </li>
                </ol>
              </section>

              <section>
                <h3 className="font-semibold">🌐 Base URL</h3>
                <p>
                  The base API endpoint is displayed in the UI (above the token generator).
                  Append paths like <code>/api/list</code> or <code>/api/image</code> to it.
                </p>
              </section>

              <section>
                <h3 className="font-semibold">📄 Endpoint: <code>/api/list</code></h3>
                <p>Retrieves a paginated list of your uploaded images.</p>
                <p><strong>Method:</strong> <code>POST</code></p>
                <p><strong>Request Headers:</strong></p>
                <pre><code>Authorization: Bearer &lt;your_token&gt;</code></pre>
                <p><strong>Request Body (JSON):</strong> <em>optional</em></p>
                <pre><code>{`{
  "cursor": "abc123", // optional
  "limit": 10         // optional, between 1 and 100
}`}</code></pre>

                <p><strong>Response Example:</strong></p>
                <pre><code>{`{
  "images": [
    {
      "image_id": "abc123",
      "s3_key": "images/user1/photo.jpg",
      "status": "processed",
      "result_json": "...",
      "created_at": "2025-05-05T12:00:00Z"
    }
  ],
  "next_cursor": "def456"
}`}</code></pre>

                <p>
                  Use <code>next_cursor</code> in the next request to fetch more results.
                  Stop when <code>next_cursor</code> is <code>null</code>.
                </p>
              </section>

              <section>
                <h3 className="font-semibold">🖼 Endpoint: <code>{`/api/image?image_id={image_id}`}</code></h3>
                <p>Get details and extracted JSON for a single image by its ID.</p>
                <p><strong>Method:</strong> <code>GET</code></p>
                <p><strong>Request Headers:</strong></p>
                <pre><code>Authorization: Bearer &lt;your_token&gt;</code></pre>

                <p><strong>Response:</strong> same <code>ImageStatus</code> object as in the list.</p>
              </section>
            </div>
          </>
        </DialogContent>
      </Dialog>
    </div>
  )
}
