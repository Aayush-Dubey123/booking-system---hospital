import { useNavigate } from 'react-router-dom'

/* Shared flat doctor illustration — matches citycare-redesign-v2.html */
function DoctorArt() {
  return (
    <svg viewBox="0 0 220 230" style={{ width: '100%', height: 'auto' }}>
      <ellipse cx="110" cy="205" rx="90" ry="14" fill="#cca75a" opacity=".2" />
      <rect x="30" y="70" width="60" height="60" rx="10" fill="#0b1329" />
      <path d="M40 70 h40 v-6 a20 20 0 0 0 -40 0 z" fill="#F1D9C6" />
      <circle cx="60" cy="55" r="20" fill="#F1D9C6" />
      <path d="M42 50 a18 14 0 0 1 36 0" fill="#2A2018" />
      <rect x="80" y="88" width="112" height="90" rx="14" fill="#cca75a" />
      <circle cx="136" cy="70" r="22" fill="#F1D9C6" />
      <path d="M116 66 a20 15 0 0 1 40 0" fill="#2A2018" />
      <rect x="105" y="90" width="62" height="88" rx="12" fill="#080f1e" stroke="rgba(204, 167, 90, 0.25)" strokeWidth="1" />
      <rect x="118" y="108" width="36" height="6" rx="3" fill="#0b1329" />
      <rect x="118" y="120" width="36" height="6" rx="3" fill="#0b1329" />
      <rect x="118" y="132" width="22" height="6" rx="3" fill="#cca75a" />
      <circle cx="70" cy="115" r="7" fill="none" stroke="#cca75a" strokeWidth="3" />
      <path d="M70 122 v14 a10 10 0 0 0 10 10 h6" fill="none" stroke="#cca75a" strokeWidth="3" strokeLinecap="round" />
      <circle cx="90" cy="147" r="5" fill="#cca75a" />
    </svg>
  )
}

/* EKG trace SVG backdrop for the art side panel */
function AuthTrace() {
  return (
    <div className="auth-trace">
      <svg viewBox="0 0 400 700" preserveAspectRatio="none">
        <path d="M0,340 L120,340 L135,300 L150,380 L165,280 L180,340 L400,340" />
      </svg>
    </div>
  )
}

/**
 * AuthShell — split-screen auth layout.
 * Props:
 *   activeTab  {'signin'|'signup'}
 *   title      {string}  — form heading
 *   subtitle   {string}  — form sub-copy
 *   children   {ReactNode} — form fields + submit button
 *   footerText {string}  — text before the link
 *   footerLinkLabel {string}
 *   footerLinkTab   {'signin'|'signup'} — which tab the link switches to
 */
export default function AuthShell({
  activeTab,
  title,
  subtitle,
  children,
  footerText,
  footerLinkLabel,
  footerLinkTab,
}) {
  const navigate = useNavigate()

  const handleTabSwitch = (tab) => {
    navigate(tab === 'signin' ? '/login' : '/signup')
  }

  return (
    <div className="auth-wrap">
      <div className="auth-shell">
        {/* Left — form panel */}
        <div className="auth-form-side">
          {/* Logo */}
          <div className="logo-row">
            <div className="logo-mark">
              <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 12h4l2 -6 4 12 2 -6h8" />
              </svg>
            </div>
            <span className="logo-word">City<em>Care</em></span>
          </div>

          {/* Tab toggle */}
          <div className="auth-tabs">
            <button
              type="button"
              className={activeTab === 'signin' ? 'active' : ''}
              onClick={() => handleTabSwitch('signin')}
            >
              Sign in
            </button>
            <button
              type="button"
              className={activeTab === 'signup' ? 'active' : ''}
              onClick={() => handleTabSwitch('signup')}
            >
              Create account
            </button>
          </div>

          {/* Form content */}
          <h1 className="auth-title">{title}</h1>
          <p className="auth-sub">{subtitle}</p>

          {children}

          {/* Footer link */}
          <div className="auth-foot">
            {footerText}{' '}
            <a onClick={() => handleTabSwitch(footerLinkTab)}>
              {footerLinkLabel}
            </a>
          </div>
        </div>

        {/* Right — art panel */}
        <div className="auth-art-side">
          <AuthTrace />
          <div className="art">
            <DoctorArt />
          </div>
          <div className="auth-quote">
            <p>"Care that keeps pace with you."</p>
            <span>CityCare Clinic — since 2014</span>
          </div>
        </div>
      </div>
    </div>
  )
}
