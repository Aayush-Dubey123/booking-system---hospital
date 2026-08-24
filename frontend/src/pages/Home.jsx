import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../components/Toast'
import {
  HeartPulse, Activity, Shield, ArrowRight, Lock, User,
  Stethoscope, Cpu, Layers, Send, CheckCircle, Sparkles,
  Calendar, Eye, EyeOff, Loader2, PhoneCall,
  FileText, CreditCard, Grid, Menu, X,
} from 'lucide-react'

/* ─────────────────────────────────────────────────────────────
   Smooth-scroll that compensates for the sticky header height
───────────────────────────────────────────────────────────── */
const HEADER_H = 72 // px — keep in sync with header height

function scrollTo(id) {
  const el = document.getElementById(id)
  if (!el) return
  const top = el.getBoundingClientRect().top + window.scrollY - HEADER_H
  window.scrollTo({ top, behavior: 'smooth' })
}

/* ─────────────────────────────────────────────────────────────
   Main component
───────────────────────────────────────────────────────────── */
export default function Home({ defaultTab = 'signin' }) {
  // ── Auth card state ────────────────────────────────────────
  const [activeTab, setActiveTab] = useState(defaultTab)

  useEffect(() => {
    setActiveTab(defaultTab)
  }, [defaultTab])

  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  // ── Product preview state ──────────────────────────────────
  const [previewTab, setPreviewTab] = useState('dashboard')
  const [chatMsg, setChatMsg] = useState('')
  const [chatLog, setChatLog] = useState([
    { from: 'bot', text: 'Hello John! I can help you check your medical records, review prescriptions, or look up appointment details. What would you like to know?' },
  ])

  // ── Mobile nav ────────────────────────────────────────────
  const [mobileOpen, setMobileOpen] = useState(false)

  // ── Forms (separate instances per tab to prevent bleed) ───
  const signinForm = useForm()
  const signupForm = useForm()

  const { login, signup, isAuthenticated } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  // ── Helpers ───────────────────────────────────────────────
  const getDashPath = (r) => {
    if (r === 'doctor') return '/doctor/dashboard'
    if (r === 'owner') return '/owner/dashboard'
    if (r === 'superadmin') return '/admin/dashboard'
    return '/dashboard'
  }

  const handleBook = () => {
    if (isAuthenticated) { navigate('/book'); return }
    scrollTo('hero')
    setActiveTab('signin')
    toast.info('Sign in or use a demo account to book an appointment.', 'Sign In Required')
  }

  const switchTab = (tab) => {
    setActiveTab(tab)
    signinForm.clearErrors()
    signupForm.clearErrors()
    setShowPassword(false)
  }

  // ── Login submit ──────────────────────────────────────────
  const onSignin = async (data) => {
    setLoading(true)
    try {
      const res = await login({ email: data.email, password: data.password })
      toast.success('Welcome back!', 'Login Successful')
      navigate(getDashPath(res.role))
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Login failed. Please check your credentials.')
    } finally { setLoading(false) }
  }

  // ── Signup submit ─────────────────────────────────────────
  const onSignup = async (data) => {
    setLoading(true)
    try {
      await signup({ first_name: data.first_name, last_name: data.last_name, email: data.email, password: data.password })
      const res = await login({ email: data.email, password: data.password })
      toast.success('Account created! Welcome to CityCare.', 'Welcome')
      navigate(getDashPath(res.role))
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Sign-up failed. Please try again.')
    } finally { setLoading(false) }
  }

  // ── Demo login ────────────────────────────────────────────
  const demoLogin = async (roleType) => {
    const creds = {
      patient: { email: 'patient1@example.com',      password: 'password123' },
      doctor:  { email: 'doctor1@example.com',        password: 'pass-ADAYUSH1' },
      admin:   { email: 'superadmin@citycare.com',    password: 'admin1234' },
    }[roleType]
    if (!creds) return
    setLoading(true)
    try {
      const res = await login(creds)
      toast.success(`Signed in as ${roleType}.`, 'Demo Access Granted')
      navigate(getDashPath(res.role))
    } catch (err) {
      toast.error(err.response?.data?.detail ?? `Could not sign in as ${roleType}.`)
    } finally { setLoading(false) }
  }

  // ── Preview chat ──────────────────────────────────────────
  const sendChat = (e) => {
    e.preventDefault()
    if (!chatMsg.trim()) return
    const userText = chatMsg.trim()
    setChatLog(p => [...p, { from: 'user', text: userText }])
    setChatMsg('')
    setTimeout(() => {
      let reply = "I'm a preview chatbot. Sign in to use the real AI Health Assistant!"
      const lc = userText.toLowerCase()
      if (lc.includes('prescription') || lc.includes('medication'))
        reply = 'Your active prescriptions: Amoxicillin 500mg (twice daily), Vitamin D3 1000 IU (daily).'
      else if (lc.includes('appointment') || lc.includes('doctor'))
        reply = 'Your next appointment: General Checkup with Dr. Sarah Johnson — today at 10:00 AM.'
      setChatLog(p => [...p, { from: 'bot', text: reply }])
    }, 700)
  }

  // ── Reusable style constants ──────────────────────────────
  const NAV_LINK = 'text-sm font-medium text-slate-400 hover:text-white transition-colors duration-200 hover:underline underline-offset-4 decoration-[#cca75a]/60'
  const INPUT_BASE = 'w-full bg-[#0a0f1e] border border-slate-800/80 focus:border-[#cca75a]/60 text-slate-200 placeholder:text-slate-600 rounded-xl outline-none transition-colors duration-200'
  const LABEL = 'block text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1.5'
  const DEMO_BTN = 'w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-[#0a0f1e] hover:bg-[#111827] border border-slate-800/60 hover:border-slate-700 transition-all duration-200 group cursor-pointer text-left'
  const GOLD_BTN = 'bg-gradient-to-r from-[#cca75a] to-[#ddb96a] hover:from-[#ddb96a] hover:to-[#cca75a] text-[#050811] font-bold transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed'
  const GHOST_BTN = 'bg-[#0d1527]/80 hover:bg-[#131f38] text-slate-300 hover:text-white border border-slate-800 hover:border-slate-700 font-semibold transition-all duration-200'

  const pwVal = signupForm.watch('password')

  return (
    <div className="min-h-screen bg-[#050811] text-slate-100 antialiased overflow-x-hidden" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>

      {/* ── 1. NAVBAR ─────────────────────────────────────── */}
      <header
        id="site-header"
        className="fixed top-0 inset-x-0 z-50 border-b border-white/5"
        style={{ height: `${HEADER_H}px`, background: 'rgba(5,8,17,0.92)', backdropFilter: 'blur(20px)' }}
      >
        <div className="max-w-[1320px] mx-auto h-full px-5 sm:px-8 flex items-center justify-between gap-6">

          {/* Logo */}
          <button onClick={() => scrollTo('hero')} className="flex items-center gap-2.5 shrink-0 focus:outline-none">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#cca75a] to-[#e8cc86] flex items-center justify-center">
              <HeartPulse className="w-4 h-4 text-[#050811]" />
            </div>
            <span className="text-[17px] font-semibold tracking-tight text-white">
              City<span className="text-[#cca75a]">Care</span>
            </span>
          </button>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-7">
            {[['Home','hero'],['Services','services'],['How It Works','how-it-works'],['About Us','about-us']].map(([label, id]) => (
              <button key={id} onClick={() => scrollTo(id)} className={NAV_LINK}>{label}</button>
            ))}
          </nav>

          {/* Desktop right actions */}
          <div className="hidden md:flex items-center gap-3 shrink-0">
            <button
              onClick={() => { scrollTo('hero'); switchTab('signin') }}
              className="text-sm font-semibold text-slate-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-white/5 transition-all duration-200"
            >
              Log in
            </button>
            <button
              onClick={() => { scrollTo('hero'); switchTab('signup') }}
              className="text-sm font-semibold text-slate-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-white/5 transition-all duration-200 border border-slate-700 hover:border-slate-600"
            >
              Sign up
            </button>
            <button
              id="nav-book-btn"
              onClick={handleBook}
              className={`${GOLD_BTN} text-xs font-bold px-4 py-2 rounded-xl shadow-md shadow-[#cca75a]/10`}
            >
              Book Appointment
            </button>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 text-slate-400 hover:text-white"
            onClick={() => setMobileOpen(o => !o)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile drawer */}
        {mobileOpen && (
          <div className="md:hidden absolute top-full inset-x-0 bg-[#080f1e] border-b border-slate-800 py-4 px-5 space-y-1">
            {[['Home','hero'],['Services','services'],['How It Works','how-it-works'],['About Us','about-us']].map(([label, id]) => (
              <button
                key={id}
                onClick={() => { scrollTo(id); setMobileOpen(false) }}
                className="w-full text-left py-2.5 text-sm text-slate-300 hover:text-white font-medium"
              >
                {label}
              </button>
            ))}
            <div className="pt-3 flex flex-col gap-2">
              <button onClick={() => { scrollTo('hero'); switchTab('signin'); setMobileOpen(false) }} className={`${GHOST_BTN} text-sm px-4 py-2.5 rounded-xl`}>Log in</button>
              <button onClick={handleBook} className={`${GOLD_BTN} text-sm px-4 py-2.5 rounded-xl`}>Book Appointment</button>
            </div>
          </div>
        )}
      </header>

      {/* ── 2. HERO ───────────────────────────────────────── */}
      <section
        id="hero"
        className="relative"
        style={{ paddingTop: HEADER_H }}
      >
        {/* Ambient glow — contained so it never causes overflow */}
        <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute top-0 left-0 w-[500px] h-[500px] rounded-full bg-[#cca75a]/4 blur-[140px] translate-x-[-30%] translate-y-[-20%]" />
          <div className="absolute bottom-0 right-0 w-[400px] h-[400px] rounded-full bg-blue-600/4 blur-[120px] translate-x-[20%] translate-y-[20%]" />
        </div>

        {/*
          Hero grid: 1440px max container, 100px top pad, 56px bottom pad.
          3-col proportions: 34% / 34% / 32%.
          items-stretch makes all 3 columns share the same height.
          The image column fills h-full; the auth card scrolls internally if needed.
        */}
        <div className="relative max-w-[1320px] mx-auto px-5 sm:px-8 pt-8 pb-10">
          <div
            className="hidden lg:grid gap-6"
            style={{ gridTemplateColumns: '34fr 34fr 32fr' }}
          >

            {/* ── Col 1 – Copy ────────────────────────────── */}
            <div className="flex flex-col justify-center">
              <span className="inline-block text-[#cca75a] text-[10px] font-bold tracking-[0.18em] uppercase mb-3">
                Trusted Healthcare, Always
              </span>
              <h1
                className="text-[2.6rem] font-bold leading-[1.1] tracking-tight text-white mb-4"
                style={{ fontFamily: "'Fraunces', serif" }}
              >
                Exceptional care.<br />
                <span className="bg-gradient-to-r from-[#cca75a] to-[#f4d193] bg-clip-text text-transparent">
                  Exclusively yours.
                </span>
              </h1>
              <p className="text-slate-400 text-[0.875rem] leading-relaxed mb-6 max-w-[340px]">
                CityCare Hospital System brings together expert doctors, advanced technology, and compassionate care — all in one place.
              </p>

              <div className="flex flex-wrap gap-3 mb-6">
                <button
                  id="hero-book-btn"
                  onClick={handleBook}
                  className={`${GOLD_BTN} flex items-center gap-2 text-sm px-5 py-2.5 rounded-xl`}
                >
                  Book Appointment <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => scrollTo('services')}
                  className={`${GHOST_BTN} text-sm px-5 py-2.5 rounded-xl`}
                >
                  Explore Services
                </button>
              </div>

              {/* Trust badges */}
              <div className="flex flex-wrap items-center gap-x-5 gap-y-2 pt-4 border-t border-slate-800/50">
                {[
                  [Shield, '24/7 Support'],
                  [Activity, 'Top Specialists'],
                  [Lock, 'Secure & Private'],
                ].map(([Icon, label]) => (
                  <span key={label} className="flex items-center gap-1.5 text-[11px] text-slate-500">
                    <Icon className="w-3.5 h-3.5 text-[#cca75a]/70" /> {label}
                  </span>
                ))}
              </div>
            </div>

            {/* ── Col 2 – Lobby image (fills col height) ─── */}
            <div
              className="relative rounded-2xl overflow-hidden border border-[#cca75a]/10 shadow-2xl group"
              style={{ minHeight: 520 }}
            >
              <img
                src="/citycare_lobby_premium.jpg"
                alt="CityCare premium hospital reception lobby"
                className="absolute inset-0 w-full h-full object-cover brightness-[0.72] saturate-90 group-hover:scale-[1.03] transition-transform duration-700"
              />
              {/* gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-[#050811]/90 via-transparent to-[#050811]/10" />

              {/* Bottom label — always inside the image boundary */}
              <div className="absolute bottom-3.5 left-3.5 right-3.5 flex items-center justify-between bg-[#080f1e]/88 backdrop-blur-md rounded-xl border border-slate-800/70 px-4 py-2.5">
                <div>
                  <span className="block text-[8px] text-[#cca75a] font-bold tracking-[0.15em] uppercase mb-0.5">Premium Facility</span>
                  <span className="text-white text-[11px] font-semibold">CityCare Hospital Reception</span>
                </div>
                <span className="relative flex h-2 w-2 shrink-0">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
              </div>

              {/* Floating metric cards — contained inside image column */}
              <div className="absolute top-3.5 right-3.5 flex flex-col gap-2 w-[136px]">
                {[
                  { label: 'Patients Served',    value: '12,500+', sub: 'Trusted by thousands' },
                  { label: 'Appointments Today', value: '320',     sub: 'All departments' },
                  { label: 'Satisfaction Rate',  value: '98%',     sub: 'Happy patients' },
                ].map(m => (
                  <div key={m.label} className="bg-[#080f1e]/90 backdrop-blur-md border border-[#cca75a]/15 rounded-xl px-3 py-2 shadow-xl">
                    <p className="text-[8px] font-bold text-slate-400 tracking-wide uppercase leading-none mb-1">{m.label}</p>
                    <p className="text-white text-[15px] font-bold leading-none">{m.value}</p>
                    <p className="text-[8px] text-[#cca75a]/80 mt-1">{m.sub}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* ── Col 3 – Auth / Demo card ────────────────── */}
            <div
              className="bg-[#080f1e] border border-[#cca75a]/12 rounded-2xl shadow-2xl flex flex-col"
              style={{ maxHeight: 620 }}
            >
              {/* Tab bar — always visible at top */}
              <div className="flex border-b border-slate-900 shrink-0">
                {[['signin','Sign In'],['signup','Create Account']].map(([t, label]) => (
                  <button
                    key={t}
                    onClick={() => switchTab(t)}
                    className={`flex-1 py-2.5 text-[11px] font-bold tracking-wide transition-all duration-200 ${
                      activeTab === t
                        ? 'bg-gradient-to-r from-[#cca75a] to-[#ddb96a] text-[#050811]'
                        : 'text-slate-400 hover:text-slate-200 bg-transparent'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>

              {/* Scrollable form region */}
              <div className="flex-1 overflow-y-auto px-5 pt-4 pb-4" style={{ scrollbarWidth: 'thin', scrollbarColor: '#1e293b transparent' }}>

                {/* Relative container with transition layout */}
                <div className="relative h-[375px] w-full">
                  {/* Sign-in form */}
                  <div
                    className="absolute inset-0 transition-all duration-300 ease-in-out"
                    style={{
                      opacity: activeTab === 'signin' ? 1 : 0,
                      transform: activeTab === 'signin' ? 'translateY(0)' : 'translateY(-10px)',
                      pointerEvents: activeTab === 'signin' ? 'auto' : 'none',
                    }}
                  >
                    <div className="mb-4">
                      <h2 className="text-white text-[15px] font-bold">Welcome back</h2>
                      <p className="text-slate-500 text-[11px] mt-0.5">Sign in to your CityCare account</p>
                    </div>
                    <form onSubmit={signinForm.handleSubmit(onSignin)} className="space-y-3" noValidate>
                      <div>
                        <label className={LABEL}>Email</label>
                        <div className="relative">
                          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" />
                          <input
                            type="email"
                            placeholder="name@email.com"
                            className={`${INPUT_BASE} text-[12px] py-2.5 pl-9 pr-3`}
                            {...signinForm.register('email', { required: 'Email is required' })}
                          />
                        </div>
                        {signinForm.formState.errors.email && (
                          <span className="text-red-400 text-[9px] mt-0.5 block">{signinForm.formState.errors.email.message}</span>
                        )}
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <label className={`${LABEL} mb-0`}>Password</label>
                          <button
                            type="button"
                            onClick={() => toast.info('Password reset is handled by your clinic administrator.', 'Contact Support')}
                            className="text-[10px] text-[#cca75a]/80 hover:text-[#cca75a] transition-colors"
                          >
                            Forgot?
                          </button>
                        </div>
                        <div className="relative">
                          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" />
                          <input
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Your password"
                            className={`${INPUT_BASE} text-[12px] py-2.5 pl-9 pr-10`}
                            {...signinForm.register('password', { required: 'Password is required' })}
                          />
                          <button
                            type="button"
                            onClick={() => setShowPassword(s => !s)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition-colors"
                          >
                            {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                        {signinForm.formState.errors.password && (
                          <span className="text-red-400 text-[9px] mt-0.5 block">{signinForm.formState.errors.password.message}</span>
                        )}
                      </div>

                      <label className="flex items-center gap-2 cursor-pointer select-none">
                        <input type="checkbox" id="remember" className="rounded accent-[#cca75a]" />
                        <span className="text-slate-400 text-[11px]">Remember me</span>
                      </label>

                      <button
                        type="submit"
                        disabled={loading}
                        className={`${GOLD_BTN} w-full flex items-center justify-center gap-2 text-[13px] py-2.5 rounded-xl`}
                      >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><span>Sign In</span><ArrowRight className="w-4 h-4" /></>}
                      </button>
                    </form>
                  </div>

                  {/* Sign-up form */}
                  <div
                    className="absolute inset-0 transition-all duration-300 ease-in-out"
                    style={{
                      opacity: activeTab === 'signup' ? 1 : 0,
                      transform: activeTab === 'signup' ? 'translateY(0)' : 'translateY(10px)',
                      pointerEvents: activeTab === 'signup' ? 'auto' : 'none',
                    }}
                  >
                    <div className="mb-3">
                      <h2 className="text-white text-[15px] font-bold">Create your account</h2>
                      <p className="text-slate-500 text-[11px] mt-0.5">Takes less than a minute</p>
                    </div>
                    <form onSubmit={signupForm.handleSubmit(onSignup)} className="space-y-2.5" noValidate>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className={LABEL}>First Name</label>
                          <input
                            placeholder="John"
                            className={`${INPUT_BASE} text-[12px] py-2 px-3`}
                            {...signupForm.register('first_name', { required: 'Required' })}
                          />
                          {signupForm.formState.errors.first_name && (
                            <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.first_name.message}</span>
                          )}
                        </div>
                        <div>
                          <label className={LABEL}>Last Name</label>
                          <input
                            placeholder="Doe"
                            className={`${INPUT_BASE} text-[12px] py-2 px-3`}
                            {...signupForm.register('last_name', { required: 'Required' })}
                          />
                          {signupForm.formState.errors.last_name && (
                            <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.last_name.message}</span>
                          )}
                        </div>
                      </div>

                      <div>
                        <label className={LABEL}>Email</label>
                        <input
                          type="email"
                          placeholder="name@email.com"
                          className={`${INPUT_BASE} text-[12px] py-2 px-3`}
                          {...signupForm.register('email', { required: 'Email is required' })}
                        />
                        {signupForm.formState.errors.email && (
                          <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.email.message}</span>
                        )}
                      </div>

                      <div>
                        <label className={LABEL}>Password</label>
                        <input
                          type="password"
                          placeholder="Min 8 characters"
                          className={`${INPUT_BASE} text-[12px] py-2 px-3`}
                          {...signupForm.register('password', { required: 'Password is required', minLength: { value: 8, message: 'Min 8 characters' } })}
                        />
                        {signupForm.formState.errors.password && (
                          <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.password.message}</span>
                        )}
                      </div>

                      <div>
                        <label className={LABEL}>Confirm Password</label>
                        <input
                          type="password"
                          placeholder="Repeat password"
                          className={`${INPUT_BASE} text-[12px] py-2 px-3`}
                          {...signupForm.register('confirm_password', {
                            required: 'Please confirm your password',
                            validate: v => v === pwVal || 'Passwords do not match',
                          })}
                        />
                        {signupForm.formState.errors.confirm_password && (
                          <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.confirm_password.message}</span>
                        )}
                      </div>

                      <button
                        type="submit"
                        disabled={loading}
                        className={`${GOLD_BTN} w-full flex items-center justify-center gap-2 text-[13px] py-2.5 rounded-xl`}
                      >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><span>Create Account</span><ArrowRight className="w-4 h-4" /></>}
                      </button>
                    </form>
                  </div>
                </div>

                {/* OR Divider */}
                <div className="relative my-3 flex items-center">
                  <div className="flex-1 border-t border-slate-800" />
                  <span className="mx-3 text-[9px] font-bold text-slate-600 uppercase tracking-widest">or</span>
                  <div className="flex-1 border-t border-slate-800" />
                </div>

                {/* Demo access — horizontal 3-tile grid matching the reference */}
                <div>
                  <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">Explore CityCare Demo</p>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { key: 'patient', title: 'Patient',  icon: User },
                      { key: 'doctor',  title: 'Doctor',   icon: Stethoscope },
                      { key: 'admin',   title: 'Admin',    icon: Shield },
                    ].map(d => (
                      <button
                        key={d.key}
                        disabled={loading}
                        onClick={() => demoLogin(d.key)}
                        className="flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl bg-[#0a0f1e] hover:bg-[#111827] border border-slate-800/60 hover:border-[#cca75a]/20 transition-all duration-200 group cursor-pointer"
                        aria-label={`Try demo as ${d.title}`}
                      >
                        <div className="w-8 h-8 rounded-lg bg-[#cca75a]/8 group-hover:bg-[#cca75a]/15 flex items-center justify-center transition-colors">
                          <d.icon className="w-4 h-4 text-[#cca75a]" />
                        </div>
                        <span className="text-white text-[11px] font-semibold">{d.title}</span>
                        <span className="text-[#cca75a] text-[9px] font-bold">Try Demo</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Mobile layout — single column stacked (375px / 768px) */}
          <div className="lg:hidden flex flex-col gap-6">
            {/* Mobile Col 1 – Copy */}
            <div className="flex flex-col">
              <span className="inline-block text-[#cca75a] text-[10px] font-bold tracking-[0.18em] uppercase mb-3">
                Trusted Healthcare, Always
              </span>
              <h1
                className="text-[2.2rem] sm:text-[2.6rem] font-bold leading-[1.1] tracking-tight text-white mb-4"
                style={{ fontFamily: "'Fraunces', serif" }}
              >
                Exceptional care.<br />
                <span className="bg-gradient-to-r from-[#cca75a] to-[#f4d193] bg-clip-text text-transparent">
                  Exclusively yours.
                </span>
              </h1>
              <p className="text-slate-400 text-sm leading-relaxed mb-5">
                CityCare Hospital System brings together expert doctors, advanced technology, and compassionate care — all in one place.
              </p>
              <div className="flex flex-wrap gap-3 mb-5">
                <button onClick={handleBook} className={`${GOLD_BTN} flex items-center gap-2 text-sm px-5 py-2.5 rounded-xl`}>
                  Book Appointment <ArrowRight className="w-4 h-4" />
                </button>
                <button onClick={() => scrollTo('services')} className={`${GHOST_BTN} text-sm px-5 py-2.5 rounded-xl`}>
                  Explore Services
                </button>
              </div>
              <div className="flex flex-wrap items-center gap-x-5 gap-y-2 pt-4 border-t border-slate-800/50">
                {[
                  [Shield, '24/7 Support'],
                  [Activity, 'Top Specialists'],
                  [Lock, 'Secure & Private'],
                ].map(([Icon, label]) => (
                  <span key={label} className="flex items-center gap-1.5 text-[11px] text-slate-500">
                    <Icon className="w-3.5 h-3.5 text-[#cca75a]/70" /> {label}
                  </span>
                ))}
              </div>
            </div>

            {/* Mobile Col 2 – Image */}
            <div className="relative h-[300px] sm:h-[380px] rounded-2xl overflow-hidden border border-[#cca75a]/10 shadow-2xl group">
              <img
                src="/citycare_lobby_premium.jpg"
                alt="CityCare premium hospital reception lobby"
                className="absolute inset-0 w-full h-full object-cover brightness-[0.72] group-hover:scale-[1.03] transition-transform duration-700"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#050811]/90 via-transparent to-[#050811]/10" />
              <div className="absolute bottom-3.5 left-3.5 right-3.5 flex items-center justify-between bg-[#080f1e]/88 backdrop-blur-md rounded-xl border border-slate-800/70 px-4 py-2.5">
                <div>
                  <span className="block text-[8px] text-[#cca75a] font-bold tracking-[0.15em] uppercase mb-0.5">Premium Facility</span>
                  <span className="text-white text-[11px] font-semibold">CityCare Hospital Reception</span>
                </div>
<span className="relative flex h-2 w-2 shrink-0">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
              </div>
              <div className="absolute top-3.5 right-3.5 flex flex-col gap-2 w-[130px]">
                {[
                  { label: 'Patients', value: '12,500+' },
                  { label: 'Today',    value: '320 Appts' },
                  { label: 'Rating',   value: '98%' },
                ].map(m => (
                  <div key={m.label} className="bg-[#080f1e]/90 backdrop-blur-md border border-[#cca75a]/15 rounded-xl px-3 py-2 shadow-xl">
                    <p className="text-[8px] font-bold text-slate-400 uppercase leading-none mb-1">{m.label}</p>
                    <p className="text-white text-[14px] font-bold leading-none">{m.value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Mobile Col 3 – Auth */}
            <div className="bg-[#080f1e] border border-[#cca75a]/12 rounded-2xl shadow-2xl">
              <div className="flex border-b border-slate-900">
                {[['signin','Sign In'],['signup','Create Account']].map(([t, label]) => (
                  <button
                    key={t}
                    onClick={() => switchTab(t)}
                    className={`flex-1 py-2.5 text-[11px] font-bold tracking-wide transition-all duration-200 ${
                      activeTab === t
                        ? 'bg-gradient-to-r from-[#cca75a] to-[#ddb96a] text-[#050811]'
                        : 'text-slate-400 hover:text-slate-200 bg-transparent'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <div className="px-5 pt-4 pb-4">
                {/* Relative container with transition layout */}
                <div className="relative h-[375px] w-full">
                  {/* Sign-in form */}
                  <div
                    className="absolute inset-0 transition-all duration-300 ease-in-out"
                    style={{
                      opacity: activeTab === 'signin' ? 1 : 0,
                      transform: activeTab === 'signin' ? 'translateY(0)' : 'translateY(-10px)',
                      pointerEvents: activeTab === 'signin' ? 'auto' : 'none',
                    }}
                  >
                    <div className="mb-3">
                      <h2 className="text-white text-[15px] font-bold">Welcome back</h2>
                      <p className="text-slate-500 text-[11px] mt-0.5">Sign in to your CityCare account</p>
                    </div>
                    <form onSubmit={signinForm.handleSubmit(onSignin)} className="space-y-3" noValidate>
                      <div>
                        <label className={LABEL}>Email</label>
                        <div className="relative">
                          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" />
                          <input type="email" placeholder="name@email.com" className={`${INPUT_BASE} text-[12px] py-2.5 pl-9 pr-3`} {...signinForm.register('email', { required: 'Email is required' })} />
                        </div>
                        {signinForm.formState.errors.email && <span className="text-red-400 text-[9px] mt-0.5 block">{signinForm.formState.errors.email.message}</span>}
                      </div>
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <label className={`${LABEL} mb-0`}>Password</label>
                          <button type="button" onClick={() => toast.info('Contact your clinic admin to reset.', 'Contact Support')} className="text-[10px] text-[#cca75a]/80 hover:text-[#cca75a] transition-colors">Forgot?</button>
                        </div>
                        <div className="relative">
                          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" />
                          <input type={showPassword ? 'text' : 'password'} placeholder="Your password" className={`${INPUT_BASE} text-[12px] py-2.5 pl-9 pr-10`} {...signinForm.register('password', { required: 'Password is required' })} />
                          <button type="button" onClick={() => setShowPassword(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition-colors">
                            {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                        {signinForm.formState.errors.password && <span className="text-red-400 text-[9px] mt-0.5 block">{signinForm.formState.errors.password.message}</span>}
                      </div>
                      <button type="submit" disabled={loading} className={`${GOLD_BTN} w-full flex items-center justify-center gap-2 text-[13px] py-2.5 rounded-xl`}>
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><span>Sign In</span><ArrowRight className="w-4 h-4" /></>}
                      </button>
                    </form>
                  </div>

                  {/* Sign-up form */}
                  <div
                    className="absolute inset-0 transition-all duration-300 ease-in-out"
                    style={{
                      opacity: activeTab === 'signup' ? 1 : 0,
                      transform: activeTab === 'signup' ? 'translateY(0)' : 'translateY(10px)',
                      pointerEvents: activeTab === 'signup' ? 'auto' : 'none',
                    }}
                  >
                    <div className="mb-3">
                      <h2 className="text-white text-[15px] font-bold">Create your account</h2>
                      <p className="text-slate-500 text-[11px] mt-0.5">Takes less than a minute</p>
                    </div>
                    <form onSubmit={signupForm.handleSubmit(onSignup)} className="space-y-2.5" noValidate>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className={LABEL}>First Name</label>
                          <input placeholder="John" className={`${INPUT_BASE} text-[12px] py-2 px-3`} {...signupForm.register('first_name', { required: 'Required' })} />
                          {signupForm.formState.errors.first_name && <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.first_name.message}</span>}
                        </div>
                        <div>
                          <label className={LABEL}>Last Name</label>
                          <input placeholder="Doe" className={`${INPUT_BASE} text-[12px] py-2 px-3`} {...signupForm.register('last_name', { required: 'Required' })} />
                          {signupForm.formState.errors.last_name && <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.last_name.message}</span>}
                        </div>
                      </div>
                      <div>
                        <label className={LABEL}>Email</label>
                        <input type="email" placeholder="name@email.com" className={`${INPUT_BASE} text-[12px] py-2 px-3`} {...signupForm.register('email', { required: 'Email is required' })} />
                        {signupForm.formState.errors.email && <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.email.message}</span>}
                      </div>
                      <div>
                        <label className={LABEL}>Password</label>
                        <input type="password" placeholder="Min 8 characters" className={`${INPUT_BASE} text-[12px] py-2 px-3`} {...signupForm.register('password', { required: 'Password is required', minLength: { value: 8, message: 'Min 8 characters' } })} />
                        {signupForm.formState.errors.password && <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.password.message}</span>}
                      </div>
                      <div>
                        <label className={LABEL}>Confirm Password</label>
                        <input type="password" placeholder="Repeat password" className={`${INPUT_BASE} text-[12px] py-2 px-3`} {...signupForm.register('confirm_password', { required: 'Confirm your password', validate: v => v === pwVal || 'Passwords do not match' })} />
                        {signupForm.formState.errors.confirm_password && <span className="text-red-400 text-[9px] mt-0.5 block">{signupForm.formState.errors.confirm_password.message}</span>}
                      </div>
                      <button type="submit" disabled={loading} className={`${GOLD_BTN} w-full flex items-center justify-center gap-2 text-[13px] py-2.5 rounded-xl`}>
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><span>Create Account</span><ArrowRight className="w-4 h-4" /></>}
                      </button>
                    </form>
                  </div>
                </div>

                <div className="relative my-3 flex items-center">
                  <div className="flex-1 border-t border-slate-800" />
                  <span className="mx-3 text-[9px] font-bold text-slate-600 uppercase tracking-widest">or</span>
                  <div className="flex-1 border-t border-slate-800" />
                </div>
                <div>
                  <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">Explore CityCare Demo</p>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { key: 'patient', title: 'Patient', icon: User },
                      { key: 'doctor',  title: 'Doctor',  icon: Stethoscope },
                      { key: 'admin',   title: 'Admin',   icon: Shield },
                    ].map(d => (
                      <button key={d.key} disabled={loading} onClick={() => demoLogin(d.key)} className="flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl bg-[#0a0f1e] hover:bg-[#111827] border border-slate-800/60 hover:border-[#cca75a]/20 transition-all duration-200 group" aria-label={`Try demo as ${d.title}`}>
                        <div className="w-7 h-7 rounded-lg bg-[#cca75a]/8 group-hover:bg-[#cca75a]/15 flex items-center justify-center transition-colors">
                          <d.icon className="w-3.5 h-3.5 text-[#cca75a]" />
                        </div>
                        <span className="text-white text-[10px] font-semibold">{d.title}</span>
                        <span className="text-[#cca75a] text-[9px] font-bold">Try Demo</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ── 3. SERVICES ──────────────────────────────────── */}
      <section id="services" className="border-y border-slate-900/60 bg-[#060b15]">
        <div className="max-w-[1320px] mx-auto px-5 sm:px-8 py-14 sm:py-16">
          <div className="text-center mb-14">
            <span className="text-[#cca75a] text-[10px] font-bold tracking-[0.18em] uppercase block mb-3">Our Expertise</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-white" style={{ fontFamily: "'Fraunces', serif" }}>
              Comprehensive Healthcare Services
            </h2>
            <p className="text-slate-400 text-sm mt-3 max-w-xl mx-auto">
              From routine checkups to complex treatments, our clinical departments deliver exceptional care.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { title: 'General Medicine',         desc: 'Primary health consultations, diagnostics, and routine screenings.',        icon: Stethoscope },
              { title: 'Cardiology Center',        desc: 'Cardiac diagnostics, stress tests, and comprehensive cardiovascular care.',  icon: Activity },
              { title: 'Orthopedics Clinic',       desc: 'Bone, joint, and ligament treatments with rehabilitation programs.',        icon: Layers },
              { title: 'AI Health Assistant',      desc: '24/7 AI-powered assistance for symptom queries and record summaries.',      icon: Sparkles },
            ].map((s, i) => (
              <div
                key={i}
                className="bg-[#080f1e] border border-slate-800/60 hover:border-[#cca75a]/20 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/30"
              >
                <div className="w-9 h-9 rounded-lg bg-[#cca75a]/8 flex items-center justify-center mb-5 text-[#cca75a]">
                  <s.icon className="w-4.5 h-4.5" style={{ width: 18, height: 18 }} />
                </div>
                <h3 className="text-white font-semibold text-sm mb-2">{s.title}</h3>
                <p className="text-slate-500 text-[12px] leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 4. HOW IT WORKS ──────────────────────────────── */}
      <section id="how-it-works" className="py-14 sm:py-16">
        <div className="max-w-[1320px] mx-auto px-5 sm:px-8">
          <div className="text-center mb-14">
            <span className="text-[#cca75a] text-[10px] font-bold tracking-[0.18em] uppercase block mb-3">Simple Process</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-white" style={{ fontFamily: "'Fraunces', serif" }}>
              How CityCare Works
            </h2>
            <p className="text-slate-400 text-sm mt-3 max-w-lg mx-auto">
              Book a specialist appointment in four simple digital steps.
            </p>
          </div>

          <div className="relative grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Connecting line (desktop only) */}
            <div
              aria-hidden
              className="hidden lg:block absolute top-[22px] left-[calc(12.5%+24px)] right-[calc(12.5%+24px)] h-px bg-gradient-to-r from-transparent via-[#cca75a]/25 to-transparent"
            />
            {[
              { n: '01', title: 'Find Doctors',      desc: 'Browse specialists across all clinical departments.' },
              { n: '02', title: 'Select Date & Slot', desc: 'Pick a date and a real-time available slot.' },
              { n: '03', title: 'Confirm & Book',    desc: 'Securely confirm your appointment instantly.' },
              { n: '04', title: 'Track Your Care',   desc: 'Review prescriptions and AI health insights.' },
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center text-center relative">
                <div className="w-11 h-11 rounded-full bg-[#cca75a] text-[#050811] text-sm font-bold flex items-center justify-center mb-5 shadow-lg shadow-[#cca75a]/15 border-[3px] border-[#050811] z-10">
                  {item.n}
                </div>
                <h3 className="text-white font-semibold text-sm mb-2">{item.title}</h3>
                <p className="text-slate-500 text-[12px] leading-relaxed max-w-[200px]">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 5. WHY CITYCARE ──────────────────────────────── */}
      <section id="why-citycare" className="border-t border-slate-900/60 bg-[#060b15] py-14 sm:py-16">
        <div className="max-w-[1320px] mx-auto px-5 sm:px-8">
          <div className="text-center mb-14">
            <span className="text-[#cca75a] text-[10px] font-bold tracking-[0.18em] uppercase block mb-3">Why CityCare</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-white" style={{ fontFamily: "'Fraunces', serif" }}>
              An Elevated Healthcare Standard
            </h2>
            <p className="text-slate-400 text-sm mt-3 max-w-lg mx-auto">
              We bring together first-class medical skills, advanced technology, and a seamless experience.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { title: 'Expert Doctors',      desc: 'Experienced and compassionate specialists across all fields.',     icon: Stethoscope },
              { title: 'Advanced Technology', desc: 'Modern diagnostic tools for accurate, timely diagnosis.',          icon: Cpu },
              { title: 'Personalized Care',   desc: 'Treatment plans designed around your unique health needs.',        icon: User },
              { title: 'Seamless Experience', desc: 'Everything you need — appointments, records, AI — in one place.',  icon: Layers },
            ].map((item, i) => (
              <div
                key={i}
                className="bg-[#080f1e] border border-slate-800/50 hover:border-[#cca75a]/20 rounded-2xl p-6 flex flex-col transition-all duration-300 hover:shadow-xl hover:shadow-black/20 group"
              >
                <div className="w-9 h-9 rounded-lg bg-[#cca75a]/6 group-hover:bg-[#cca75a]/12 flex items-center justify-center mb-5 text-[#cca75a] transition-colors">
                  <item.icon className="w-[18px] h-[18px]" />
                </div>
                <h3 className="text-white font-semibold text-sm mb-1.5">{item.title}</h3>
                <p className="text-slate-500 text-[12px] leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 6. PRODUCT PREVIEW ───────────────────────────── */}
      <section id="about-us" className="py-14 sm:py-16">
        <div className="max-w-[1320px] mx-auto px-5 sm:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] xl:grid-cols-[340px_1fr] gap-8 items-start">

            {/* Left sidebar description */}
            <div>
              <span className="text-[#cca75a] text-[10px] font-bold tracking-[0.18em] uppercase block mb-3">Inside CityCare</span>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4 leading-snug" style={{ fontFamily: "'Fraunces', serif" }}>
                Everything you get with CityCare
              </h2>
              <p className="text-slate-400 text-sm leading-relaxed mb-7">
                From appointments to prescriptions, our patient portal keeps your healthcare organised. Explore the interactive preview.
              </p>

              {/* Navigation tabs */}
              <div className="bg-[#080f1e] border border-slate-800/60 rounded-2xl p-2 space-y-0.5">
                {[
                  { key: 'dashboard',    label: 'Dashboard Overview',      icon: Grid },
                  { key: 'appointments', label: 'Appointments Tracker',     icon: Calendar },
                  { key: 'ai-assistant', label: 'AI Health Assistant',      icon: Sparkles },
                ].map(({ key, label, icon: Icon }) => (
                  <button
                    key={key}
                    onClick={() => setPreviewTab(key)}
                    className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-left text-[12px] font-semibold transition-all duration-200 ${
                      previewTab === key
                        ? 'bg-[#cca75a]/10 text-[#cca75a]'
                        : 'text-slate-500 hover:text-slate-200'
                    }`}
                  >
                    <Icon className="w-4 h-4 shrink-0" /> {label}
                  </button>
                ))}
                {[
                  { label: 'Medical Records', icon: FileText },
                  { label: 'Billing & Payments', icon: CreditCard },
                ].map(({ label, icon: Icon }) => (
                  <div key={label} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-[12px] font-semibold text-slate-700 select-none cursor-default">
                    <Icon className="w-4 h-4 shrink-0" /> {label}
                    <span className="ml-auto text-[8px] bg-slate-800 text-slate-600 px-1.5 py-0.5 rounded-md font-bold uppercase tracking-wide">Locked</span>
                  </div>
                ))}
              </div>

              <button
                onClick={handleBook}
                className="mt-6 text-[#cca75a] hover:text-[#ddb96a] text-xs font-bold flex items-center gap-1.5 transition-colors"
              >
                Get full dashboard access <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Right – mock product window */}
            <div className="bg-[#080f1e] border border-[#cca75a]/8 rounded-2xl overflow-hidden shadow-2xl">
              {/* Window chrome bar */}
              <div className="bg-[#050811] px-5 py-3 border-b border-slate-900 flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
                  <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/70" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
                </div>
                <span className="text-[10px] text-slate-600 font-mono tracking-widest select-none">patient_portal · CityCare</span>
                <div className="w-16" />
              </div>

              {/* Dashboard header bar */}
              <div className="px-6 py-4 border-b border-slate-900/50 flex items-center justify-between">
                <div>
                  <h3 className="text-white text-sm font-bold flex items-center gap-2">
                    Dashboard
                    <span className="text-[9px] bg-[#cca75a]/10 text-[#cca75a] px-2 py-0.5 rounded-full font-mono font-normal">Patient View</span>
                  </h3>
                  <p className="text-slate-500 text-[11px] mt-0.5">Good morning, John. Here's your health overview.</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="hidden sm:block text-slate-600 text-[11px]">{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                  <div className="w-7 h-7 rounded-full bg-[#cca75a] text-[#050811] text-[10px] font-bold flex items-center justify-center select-none">JD</div>
                </div>
              </div>

              {/* Tab content */}
              <div className="p-6">

                {/* DASHBOARD TAB */}
                {previewTab === 'dashboard' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {[
                        { label: 'Upcoming Appointment', badge: 'Active', value: 'General Checkup', sub: 'Dr. Sarah Johnson', meta: 'Today, 10:00 AM', color: 'text-[#cca75a]' },
                        { label: 'Medications', badge: '', value: '3 Active Prescriptions', sub: 'Refills available', meta: 'Updated 3 days ago', color: 'text-[#cca75a]' },
                        { label: 'Health Score', badge: '', value: '85 / 100', sub: 'Doing great!', meta: 'All metrics normal', color: 'text-emerald-500' },
                      ].map((card, ci) => (
                        <div key={ci} className="bg-[#050811] border border-slate-900/70 rounded-xl p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">{card.label}</span>
                            {card.badge && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
                          </div>
                          <p className="text-white text-xs font-semibold">{card.value}</p>
                          <p className={`text-[10px] mt-0.5 ${card.color}`}>{card.sub}</p>
                          <p className="text-[9px] text-slate-600 mt-1.5">{card.meta}</p>
                        </div>
                      ))}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="bg-[#050811] border border-slate-900/70 rounded-xl p-4">
                        <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-3">Recent Activity</h4>
                        <div className="space-y-2">
                          {[
                            ['Lab Report Available', 'Yesterday'],
                            ['Prescription Refilled', '2 days ago'],
                            ['Payment Successful',    '3 days ago'],
                          ].map(([title, time], idx) => (
                            <div key={idx} className="flex justify-between items-center text-[10px] pb-2 border-b border-slate-900 last:border-0 last:pb-0">
                              <div>
                                <p className="text-slate-300 font-medium">{title}</p>
                                <p className="text-slate-600 text-[8px]">{time}</p>
                              </div>
                              <span className="text-[#cca75a] font-semibold hover:underline cursor-pointer">View</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="bg-[#050811] border border-[#cca75a]/8 rounded-xl p-4 flex flex-col">
                        <div className="flex items-center gap-1.5 mb-2">
                          <Sparkles className="w-3.5 h-3.5 text-[#cca75a]" />
                          <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">AI Health Assistant</h4>
                        </div>
                        <p className="text-slate-500 text-[10px] leading-relaxed flex-1">
                          Ask about your health history, prescriptions, or get guidance — powered by Gemini AI.
                        </p>
                        <button
                          onClick={() => setPreviewTab('ai-assistant')}
                          className="mt-3 text-[10px] font-bold text-[#cca75a] flex items-center gap-1 hover:underline"
                        >
                          Open AI Assistant <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* APPOINTMENTS TAB */}
                {previewTab === 'appointments' && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Appointment History</h4>
                      <span className="text-[9px] bg-[#cca75a]/10 text-[#cca75a] px-2 py-0.5 rounded-full font-bold">3 total</span>
                    </div>
                    {[
                      { type: 'General Checkup',         doc: 'Dr. Sarah Johnson', date: 'Today, 10:00 AM',         status: 'Confirmed', sc: 'text-emerald-500 bg-emerald-500/8 border-emerald-500/20' },
                      { type: 'Cardiology Consultation', doc: 'Dr. Amruta N.',     date: 'Aug 15, 2026 — 2:30 PM', status: 'Completed', sc: 'text-slate-500 bg-slate-800/20 border-slate-700/30' },
                      { type: 'Follow-up Checkup',       doc: 'Dr. Sarah Johnson', date: 'Jul 10, 2026',            status: 'Completed', sc: 'text-slate-500 bg-slate-800/20 border-slate-700/30' },
                    ].map((a, ai) => (
                      <div key={ai} className="bg-[#050811] border border-slate-900/70 rounded-xl p-4 flex items-center justify-between gap-3">
                        <div className="min-w-0">
                          <p className="text-white text-xs font-semibold truncate">{a.type}</p>
                          <p className="text-slate-500 text-[10px] mt-0.5">{a.doc}</p>
                          <p className="text-slate-600 text-[9px] mt-0.5">{a.date}</p>
                        </div>
                        <span className={`shrink-0 text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-lg border ${a.sc}`}>
                          {a.status}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* AI ASSISTANT TAB */}
                {previewTab === 'ai-assistant' && (
                  <div className="flex flex-col bg-[#050811] border border-slate-900/70 rounded-xl overflow-hidden" style={{ height: 300 }}>
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                      {chatLog.map((msg, mi) => (
                        <div key={mi} className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-[82%] text-[11px] rounded-xl px-3 py-2 leading-relaxed ${
                            msg.from === 'user'
                              ? 'bg-[#cca75a]/10 border border-[#cca75a]/15 text-[#cca75a]'
                              : 'bg-[#080f1e] text-slate-300'
                          }`}>
                            {msg.text}
                          </div>
                        </div>
                      ))}
                    </div>
                    <form onSubmit={sendChat} className="flex gap-2 p-3 border-t border-slate-900">
                      <input
                        value={chatMsg}
                        onChange={e => setChatMsg(e.target.value)}
                        placeholder="Ask about prescriptions, appointments…"
                        className="flex-1 bg-[#080f1e] border border-slate-800 text-[11px] rounded-xl px-3 py-2 outline-none text-slate-300 focus:border-[#cca75a]/40 placeholder:text-slate-700"
                      />
                      <button
                        type="submit"
                        className="bg-gradient-to-r from-[#cca75a] to-[#ddb96a] text-[#050811] p-2.5 rounded-xl shrink-0"
                      >
                        <Send className="w-3.5 h-3.5" />
                      </button>
                    </form>
                  </div>
                )}

              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 7. CTA SECTION ────────────────────────────────── */}
      <section className="relative border-t border-slate-900/50 overflow-hidden bg-[#060b15] py-14 sm:py-16">
        <div aria-hidden className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="w-[600px] h-[400px] rounded-full bg-[#cca75a]/4 blur-[140px]" />
        </div>
        <div className="relative max-w-3xl mx-auto px-5 sm:px-8 text-center">
          <span className="text-[#cca75a] text-[10px] font-bold tracking-[0.18em] uppercase block mb-4">Get Started Today</span>
          <h2
            className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white leading-tight mb-5"
            style={{ fontFamily: "'Fraunces', serif" }}
          >
            Experience premium clinical care with CityCare
          </h2>
          <p className="text-slate-400 text-sm sm:text-[15px] leading-relaxed mb-8 max-w-xl mx-auto">
            Book appointments, access medical records, and stay connected with our AI health assistant — all in one place.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <button
              id="cta-book-btn"
              onClick={handleBook}
              className={`${GOLD_BTN} text-sm px-8 py-3.5 rounded-xl shadow-lg shadow-[#cca75a]/8`}
            >
              Book Appointment
            </button>
            <button
              onClick={() => { scrollTo('hero'); switchTab('signup') }}
              className={`${GHOST_BTN} text-sm px-8 py-3.5 rounded-xl`}
            >
              Create Account
            </button>
          </div>
        </div>
      </section>

      {/* ── 8. FOOTER ─────────────────────────────────────── */}
      <footer className="bg-[#050811] border-t border-slate-900/60 py-8">
        <div className="max-w-[1320px] mx-auto px-5 sm:px-8 flex flex-col sm:flex-row items-center justify-between gap-5">
          <div className="flex flex-wrap items-center justify-center gap-6 text-[11px] text-slate-600">
            {[
              [CheckCircle, 'HIPAA Compliant'],
              [Shield,      '256-bit Encryption'],
              [PhoneCall,   '24/7 Support'],
              [Lock,        'Privacy Focused'],
            ].map(([Icon, label]) => (
              <span key={label} className="flex items-center gap-1.5">
                <Icon className="w-3.5 h-3.5 text-[#cca75a]/60" /> {label}
              </span>
            ))}
          </div>
          <p className="text-[11px] text-slate-600 text-center sm:text-right">
            © {new Date().getFullYear()} CityCare Hospital System. All rights reserved.
          </p>
        </div>
      </footer>

    </div>
  )
}
