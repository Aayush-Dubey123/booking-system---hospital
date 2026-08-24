import { Loader2 } from 'lucide-react'

export default function LoadingSpinner({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-slate-400">
      <Loader2 className="w-8 h-8 animate-spin text-[#cca75a]" />
      <span className="text-sm font-medium text-slate-500">{text}</span>
    </div>
  )
}
