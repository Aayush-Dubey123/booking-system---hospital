import { useForm } from 'react-hook-form'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../components/Toast'
import AuthShell from '../../components/AuthShell'
import { Loader2 } from 'lucide-react'

export default function Login() {
  const { register, handleSubmit, formState: { errors } } = useForm()
  const [loading, setLoading] = useState(false)
  const { login, isAuthenticated, role } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  // If already authenticated, redirect
  if (isAuthenticated) {
    const target = role === 'doctor' ? '/doctor/dashboard' : '/dashboard'
    navigate(target, { replace: true })
    return null
  }

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const userRole = await login(data)
      toast.success('Welcome back!', 'Login Successful')
      if (userRole === 'doctor') {
        navigate('/doctor/dashboard')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      toast.error(
        err.response?.data?.detail ?? 'Login failed. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      activeTab="signin"
      title="Good to see you"
      subtitle="Sign in to your CityCare account."
      footerText="New here?"
      footerLinkLabel="Create an account"
      footerLinkTab="signup"
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="cc-field">
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            type="email"
            placeholder="name@email.com"
            {...register('email', { required: 'Email is required' })}
          />
          {errors.email && <p className="auth-error">{errors.email.message}</p>}
        </div>

        <div className="cc-field">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            placeholder="Enter your password"
            {...register('password', {
              required: 'Password is required',
              minLength: { value: 8, message: 'Minimum 8 characters' },
            })}
          />
          {errors.password && <p className="auth-error">{errors.password.message}</p>}
        </div>

        <button type="submit" disabled={loading} className="btn-cc-primary" style={{ marginTop: '8px' }}>
          {loading ? <Loader2 size={16} className="animate-spin" /> : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: 17, height: 17 }}>
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          )}
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </AuthShell>
  )
}
