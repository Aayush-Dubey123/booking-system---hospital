export default function SlotChip({ slot, selected, taken, onClick }) {
  if (taken) {
    return (
      <div className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-400 line-through cursor-not-allowed select-none">
        {slot}
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-150 select-none
        ${selected
          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
          : 'bg-white text-slate-600 border-slate-200 hover:border-blue-400 hover:text-blue-600'
        }`}
    >
      {slot}
    </button>
  )
}
