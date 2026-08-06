import { AlertCircle, X } from 'lucide-react'
import { useState } from 'react'

export default function ErrorBanner({ message, onRetry }) {
  const [dismissed, setDismissed] = useState(false)
  if (!message || dismissed) return null

  return (
    <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
      <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
      <span className="flex-1">{message}</span>
      <div className="flex items-center gap-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-red-600 font-semibold hover:underline text-xs"
          >
            Retry
          </button>
        )}
        <button onClick={() => setDismissed(true)} className="text-red-400 hover:text-red-600">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
