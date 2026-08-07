import { useForm } from 'react-hook-form'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../components/Toast'
import Navbar from '../../components/Navbar'
import { Loader2, UserPlus } from 'lucide-react'

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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-slate-50 to-indigo-50 flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="card shadow-lg">
            <div className="text-center mb-7">
              <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-md shadow-blue-200">
                <UserPlus className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-slate-800">Create account</h1>
              <p className="text-slate-500 text-sm mt-1">Join CityCare Clinic today</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="signup-first-name" className="label">First Name</label>
                  <input
                    id="signup-first-name"
                    className={`input ${errors.first_name ? 'input-error' : ''}`}
                    placeholder="John"
                    {...register('first_name', { required: 'Required' })}
                  />
                  {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name.message}</p>}
                </div>
                <div>
                  <label htmlFor="signup-last-name" className="label">Last Name</label>
                  <input
                    id="signup-last-name"
                    className={`input ${errors.last_name ? 'input-error' : ''}`}
                    placeholder="Doe"
                    {...register('last_name', { required: 'Required' })}
                  />
                  {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name.message}</p>}
                </div>
              </div>

              <div>
                <label htmlFor="signup-email" className="label">Email</label>
                <input
                  id="signup-email"
                  type="email"
                  className={`input ${errors.email ? 'input-error' : ''}`}
                  placeholder="you@email.com"
                  {...register('email', { required: 'Email is required' })}
                />
                {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
              </div>

              <div>
                <label htmlFor="signup-password" className="label">Password</label>
                <input
                  id="signup-password"
                  type="password"
                  className={`input ${errors.password ? 'input-error' : ''}`}
                  placeholder="Min 8 characters"
                  {...register('password', { required: 'Password is required', minLength: { value: 8, message: 'Minimum 8 characters' } })}
                />
                {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
              </div>

              <div>
                <label htmlFor="signup-confirm-password" className="label">Confirm Password</label>
                <input
                  id="signup-confirm-password"
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
