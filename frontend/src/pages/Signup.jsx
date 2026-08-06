import { useForm } from 'react-hook-form'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signup, login } from '../api/auth'
import ErrorBanner from '../components/ErrorBanner'
import Navbar from '../components/Navbar'
import { Loader2, UserPlus } from 'lucide-react'

export default function Signup() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const password = watch('password')

  const onSubmit = async (data) => {
    setLoading(true)
    setError('')
    try {
      // Signup
      await signup({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        password: data.password,
      })
      // Auto-login
      const loginRes = await login({ email: data.email, password: data.password })
      localStorage.setItem('access_token', loginRes.data.access_token)
      localStorage.setItem('role', loginRes.data.role)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-slate-100 flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="card shadow-lg">
            <div className="text-center mb-7">
              <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <UserPlus className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-slate-800">Create account</h1>
              <p className="text-slate-500 text-sm mt-1">Join CityCare Clinic today</p>
            </div>

            <ErrorBanner message={error} />

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">First Name</label>
                  <input
                    className={`input ${errors.first_name ? 'input-error' : ''}`}
                    placeholder="John"
                    {...register('first_name', { required: 'Required' })}
                  />
                  {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name.message}</p>}
                </div>
                <div>
                  <label className="label">Last Name</label>
                  <input
                    className={`input ${errors.last_name ? 'input-error' : ''}`}
                    placeholder="Doe"
                    {...register('last_name', { required: 'Required' })}
                  />
                  {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name.message}</p>}
                </div>
              </div>

              <div>
                <label className="label">Email</label>
                <input
                  type="email"
                  className={`input ${errors.email ? 'input-error' : ''}`}
                  placeholder="you@email.com"
                  {...register('email', { required: 'Email is required' })}
                />
                {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
              </div>

              <div>
                <label className="label">Password</label>
                <input
                  type="password"
                  className={`input ${errors.password ? 'input-error' : ''}`}
                  placeholder="Min 8 characters"
                  {...register('password', { required: 'Password is required', minLength: { value: 8, message: 'Minimum 8 characters' } })}
                />
                {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
              </div>

              <div>
                <label className="label">Confirm Password</label>
                <input
                  type="password"
                  className={`input ${errors.confirm_password ? 'input-error' : ''}`}
                  placeholder="Repeat password"
                  {...register('confirm_password', {
                    required: 'Please confirm your password',
                    validate: (v) => v === password || 'Passwords do not match',
                  })}
                />
                {errors.confirm_password && <p className="text-red-500 text-xs mt-1">{errors.confirm_password.message}</p>}
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                {loading ? 'Creating account...' : 'Create account'}
              </button>
            </form>

            <p className="text-center text-slate-500 text-sm mt-6">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 font-semibold hover:underline">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
