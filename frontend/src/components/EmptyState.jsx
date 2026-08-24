import { Inbox } from 'lucide-react'

export default function EmptyState({ title = 'Nothing here yet', description = '' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
      <div className="w-14 h-14 bg-[#0a0f1e] border border-[#cca75a]/15 rounded-2xl flex items-center justify-center">
        <Inbox className="w-7 h-7 text-[#cca75a]" />
      </div>
      <p className="font-semibold text-slate-200 text-base">{title}</p>
      {description && <p className="text-sm text-slate-500 text-center max-w-xs">{description}</p>}
    </div>
  )
}
