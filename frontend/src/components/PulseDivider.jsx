/**
 * PulseDivider — CityCare signature EKG/pulse trace divider.
 * Place after every page <h1> header.
 * Uses a unique key to re-trigger the CSS draw animation.
 */
export default function PulseDivider({ animKey }) {
  return (
    <div className="pulse-divider">
      <svg key={animKey} viewBox="0 0 1000 22" preserveAspectRatio="none">
        <path d="M0,11 L400,11 L415,3 L430,19 L445,3 L460,11 L1000,11" />
      </svg>
    </div>
  )
}
