import { createContext, useContext, useState, useCallback } from 'react'
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

export const useToast = () => {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

const ICONS = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
}

const STYLES = {
  success: 'bg-[#0a1e16] border-emerald-950 text-emerald-300',
  error: 'bg-[#1e1014] border-red-950/40 text-red-300',
  info: 'bg-[#080f1e] border-[#cca75a]/15 text-slate-200',
}

const ICON_STYLES = {
  success: 'text-emerald-400',
  error: 'text-red-400',
  info: 'text-[#cca75a]',
}

let toastId = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback(({ type = 'info', title, message, duration = 4000 }) => {
    const id = ++toastId
    setToasts((prev) => [...prev, { id, type, title, message }])
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
    return id
  }, [removeToast])

  const success = useCallback((message, title = 'Success') =>
    toast({ type: 'success', title, message }), [toast])

  const error = useCallback((message, title = 'Error') =>
    toast({ type: 'error', title, message }), [toast])

  const info = useCallback((message, title = 'Info') =>
    toast({ type: 'info', title, message }), [toast])

  return (
    <ToastContext.Provider value={{ toast, success, error, info }}>
      {children}

      {/* Toast container */}
      <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-3 pointer-events-none max-w-sm w-full">
        {toasts.map((t) => {
          const Icon = ICONS[t.type] || Info
          return (
            <div
              key={t.id}
              className={`pointer-events-auto flex items-start gap-3 border rounded-xl px-4 py-3 shadow-lg animate-slide-in ${STYLES[t.type]}`}
            >
              <Icon className={`w-5 h-5 mt-0.5 shrink-0 ${ICON_STYLES[t.type]}`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold">{t.title}</p>
                {t.message && <p className="text-xs mt-0.5 opacity-80">{t.message}</p>}
              </div>
              <button
                onClick={() => removeToast(t.id)}
                className="shrink-0 opacity-50 hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}
