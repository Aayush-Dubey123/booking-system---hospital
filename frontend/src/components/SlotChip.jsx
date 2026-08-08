export default function SlotChip({ slot, selected, taken, onClick }) {
  if (taken) {
    return (
      <div className="px-4 py-2 rounded-xl text-sm font-medium bg-slate-50 text-slate-400 border border-slate-100 line-through cursor-not-allowed select-none">
        {slot}
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-4 py-2 rounded-xl text-sm font-semibold border transition-all duration-300 select-none hover:scale-[1.02] active:scale-95
        ${selected
          ? 'bg-blue-600 text-white border-blue-600 shadow-lg shadow-blue-500/30 ring-2 ring-blue-500 ring-offset-2'
          : 'bg-white text-slate-600 border-slate-200 hover:border-blue-400 hover:text-blue-600 hover:shadow-sm'
        }`}
    >
      {slot}
    </button>
  )
}
