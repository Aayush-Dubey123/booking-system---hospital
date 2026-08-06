import { Inbox } from 'lucide-react'

export default function EmptyState({ title = 'Nothing here yet', description = '' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
      <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center">
        <Inbox className="w-7 h-7 text-blue-300" />
      </div>
      <p className="font-semibold text-slate-500 text-base">{title}</p>
      {description && <p className="text-sm text-slate-400">{description}</p>}
    </div>
  )
}
