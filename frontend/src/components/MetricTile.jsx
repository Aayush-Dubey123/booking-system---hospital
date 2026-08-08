/**
 * MetricTile — CityCare solid-color metric tile.
 * Props:
 *   label    {string}  — display label
 *   value    {number|null} — numeric value (null shows skeleton while loading)
 *   icon     {Component} — lucide-react icon
 *   variant  {'teal'|'pulse'|'amber'} — tile color
 */
export default function MetricTile({ label, value, icon: Icon, variant = 'teal' }) {
  const variantClass = {
    teal:  't-teal',
    pulse: 't-pulse',
    amber: 't-amber',
  }[variant] ?? 't-teal'

  return (
    <div className={`tile ${variantClass}`}>
      <div className="ic">
        {Icon && <Icon size={17} color="#fff" strokeWidth={2} />}
      </div>
      <div>
        {value == null ? (
          <div className="skeleton-num" />
        ) : (
          <div className="num">{String(value).padStart(2, '0')}</div>
        )}
        <div className="lbl">{label}</div>
      </div>
    </div>
  )
}
