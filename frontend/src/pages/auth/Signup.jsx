import { useForm } from 'react-hook-form'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../components/Toast'
import AuthShell from '../../components/AuthShell'
import { Loader2 } from 'lucide-react'

export default function Signup() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm()
  const [loading, setLoading] = useState(false)
  const { signup, login } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const password = watch('password')

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      // Signup
      await signup({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        password: data.password,
      })
      // Auto-login
      const userRole = await login({ email: data.email, password: data.password })
      toast.success('Your account has been created!', 'Welcome to CityCare')
      if (userRole === 'doctor') {
        navigate('/doctor/dashboard')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      toast.error(
        err.response?.data?.detail ?? 'Signup failed. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      activeTab="signup"
      title="Create your account"
      subtitle="Takes less than a minute to get set up."
      footerText="Already registered?"
      footerLinkLabel="Sign in instead"
      footerLinkTab="signin"
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="cc-field" style={{ marginBottom: 0 }}>
            <label htmlFor="signup-first-name">First Name</label>
            <input
              id="signup-first-name"
              placeholder="John"
              {...register('first_name', { required: 'Required' })}
            />
            {errors.first_name && <p className="auth-error">{errors.first_name.message}</p>}
          </div>
          <div className="cc-field" style={{ marginBottom: 0 }}>
            <label htmlFor="signup-last-name">Last Name</label>
            <input
              id="signup-last-name"
              placeholder="Doe"
              {...register('last_name', { required: 'Required' })}
            />
            {errors.last_name && <p className="auth-error">{errors.last_name.message}</p>}
          </div>
        </div>

        <div className="cc-field" style={{ marginTop: '14px' }}>
          <label htmlFor="signup-email">Email</label>
          <input
            id="signup-email"
            type="email"
            placeholder="name@email.com"
            {...register('email', { required: 'Email is required' })}
          />
          {errors.email && <p className="auth-error">{errors.email.message}</p>}
        </div>

        <div className="cc-field">
          <label htmlFor="signup-password">Password</label>
          <input
            id="signup-password"
            type="password"
            placeholder="Create a password"
            {...register('password', {
              required: 'Password is required',
              minLength: { value: 8, message: 'Minimum 8 characters' },
            })}
          />
          {errors.password && <p className="auth-error">{errors.password.message}</p>}
        </div>

        <div className="cc-field">
          <label htmlFor="signup-confirm-password">Confirm Password</label>
          <input
            id="signup-confirm-password"
            type="password"
            placeholder="Repeat password"
            {...register('confirm_password', {
              required: 'Please confirm your password',
              validate: (v) => v === password || 'Passwords do not match',
            })}
          />
          {errors.confirm_password && <p className="auth-error">{errors.confirm_password.message}</p>}
        </div>

        <button type="submit" disabled={loading} className="btn-cc-primary">
          {loading ? <Loader2 size={16} className="animate-spin" /> : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: 17, height: 17 }}>
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          )}
          {loading ? 'Creating account…' : 'Create account'}
        </button>
      </form>
    </AuthShell>
  )
}
