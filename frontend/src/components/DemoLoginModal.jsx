import { useEffect, useState } from 'react'
import { Loader2, Server, CheckCircle2, AlertCircle, X, RefreshCw, Clock } from 'lucide-react'

/**
 * DemoLoginModal
 * Displays a clean, professional overlay informing visitors that the demo backend
 * is hosted on Render Free and may require a short cold-start warm-up period.
 */
export default function DemoLoginModal({
  isOpen,
  roleTitle = 'Demo User',
  status = 'connecting', // 'connecting' | 'waking' | 'success' | 'error'
  errorMessage = null,
  onRetry,
  onClose,
}) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0)

  // Manage elapsed timer while modal is open and in connecting/waking state
  useEffect(() => {
    if (!isOpen) {
      setElapsedSeconds(0)
      return
    }

    if (status === 'success' || status === 'error') {
      return
    }

    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [isOpen, status])

  if (!isOpen) return null

  const isColdStart = elapsedSeconds >= 3

  return (
    <div
      className="fixed inset-0 z-[9990] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md transition-opacity duration-300"
      role="dialog"
      aria-modal="true"
      aria-labelledby="demo-modal-title"
    >
      <div className="relative w-full max-w-md bg-[#0a0f1e] border border-slate-800 rounded-2xl p-6 shadow-2xl overflow-hidden text-left">
        {/* Background glow accents */}
        <div className="absolute -top-20 -right-20 w-44 h-44 bg-[#cca75a]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -left-20 w-44 h-44 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Close / Cancel Button */}
        {(status === 'error' || elapsedSeconds >= 2) && (
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-slate-500 hover:text-slate-300 transition-colors p-1.5 rounded-lg hover:bg-slate-800/60 cursor-pointer"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <div className="flex flex-col items-center text-center">
          {/* Header Icon Badge */}
          <div className="relative mb-4">
            {status === 'success' ? (
              <div className="w-14 h-14 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-7 h-7" />
              </div>
            ) : status === 'error' ? (
              <div className="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
                <AlertCircle className="w-7 h-7" />
              </div>
            ) : (
              <div className="relative w-14 h-14 rounded-full bg-[#cca75a]/10 border border-[#cca75a]/30 flex items-center justify-center text-[#cca75a]">
                <Server className="w-7 h-7" />
                <div className="absolute inset-0 rounded-full border-2 border-[#cca75a]/50 border-t-transparent animate-spin" />
              </div>
            )}
          </div>

          {/* Heading */}
          <h3 id="demo-modal-title" className="text-xl font-bold text-white mb-1 tracking-tight">
            Thank you for visiting!
          </h3>

          {/* Role badge */}
          {roleTitle && (
            <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-semibold bg-[#cca75a]/15 text-[#cca75a] border border-[#cca75a]/30 mb-3">
              Role: {roleTitle}
            </span>
          )}

          {/* Explanation Message */}
          <div className="text-sm text-slate-300 leading-relaxed mb-5 space-y-2">
            <p>
              Our demo backend may be waking up from its free-tier sleep state. You’ll be redirected shortly. Please be patient while the server starts.
            </p>
            <p className="text-xs text-slate-400">
              (Initial startup on Render Free may take a short while if the server was idle.)
            </p>
          </div>

          {/* Progress / Loading Indicator (active during connect / waking / success) */}
          {status !== 'error' && (
            <div className="w-full bg-[#060b15] border border-slate-800/80 rounded-xl p-4 mb-2 text-left">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-medium">
                  {status === 'success' ? (
                    <span className="text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Server Ready & Authenticated
                    </span>
                  ) : isColdStart ? (
                    <span className="text-[#cca75a] flex items-center gap-1.5">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" /> Server is waking up (Render Free)...
                    </span>
                  ) : (
                    <span className="text-slate-300 flex items-center gap-1.5">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" /> Connecting to backend...
                    </span>
                  )}
                </span>

                <span className="flex items-center gap-1 text-[11px] text-slate-500 font-mono">
                  <Clock className="w-3 h-3" />
                  {elapsedSeconds}s
                </span>
              </div>

              {/* Dynamic progress bar */}
              <div className="w-full h-1.5 bg-slate-800/80 rounded-full overflow-hidden">
                {status === 'success' ? (
                  <div className="h-full bg-emerald-500 w-full transition-all duration-300" />
                ) : (
                  <div
                    className="h-full bg-gradient-to-r from-[#cca75a] to-[#ddb96a] transition-all duration-500 rounded-full"
                    style={{
                      width: `${Math.min(95, Math.max(12, elapsedSeconds * 4 + 10))}%`
                    }}
                  />
                )}
              </div>

              <p className="text-[11px] text-slate-500 mt-2 text-center italic">
                {status === 'success'
                  ? 'Redirecting shortly...'
                  : isColdStart
                  ? 'Warming up Render service. Please wait…'
                  : 'Please wait…'}
              </p>
            </div>
          )}

          {/* Genuine Error Handling View */}
          {status === 'error' && (
            <div className="w-full bg-red-950/30 border border-red-950/60 rounded-xl p-4 mb-3 text-left">
              <p className="text-xs font-semibold text-red-400 mb-1">Backend Connection Error</p>
              <p className="text-xs text-red-300/90 mb-3 leading-relaxed">
                {errorMessage || 'Unable to communicate with the authentication server.'}
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={onRetry}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-200 text-xs font-semibold transition-colors cursor-pointer"
                >
                  <RefreshCw className="w-3.5 h-3.5" /> Try Again
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="py-2 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
