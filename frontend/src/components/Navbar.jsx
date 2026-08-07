import { HeartPulse } from 'lucide-react'

export default function Navbar() {
  return (
    <header className="h-14 bg-white/80 backdrop-blur-md border-b border-slate-100 flex items-center px-6 gap-3 shadow-xs sticky top-0 z-30">
      <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center">
        <HeartPulse className="w-4 h-4 text-white" />
      </div>
      <span className="font-bold text-slate-800 text-sm">CityCare Clinic</span>
    </header>
  )
}
