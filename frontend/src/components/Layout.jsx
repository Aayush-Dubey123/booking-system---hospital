import { useState } from 'react'
import Sidebar from './Sidebar'
import { Menu, Search, Bell } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export default function Layout({ children, title = 'Overview' }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { role } = useAuth()
  
  const userName = role === 'doctor' ? 'Dr. Amruta' : 'John Doe'

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar onClose={() => setMobileOpen(false)} />
      </div>

      {/* Main content */}
      <main className="flex-1 min-w-0 flex flex-col">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center gap-3 px-4 py-3 bg-white border-b border-slate-100 sticky top-0 z-30">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 rounded-xl hover:bg-slate-100 transition-colors"
          >
            <Menu className="w-5 h-5 text-slate-600" />
          </button>
          <span className="font-bold text-slate-800 text-sm">CityCare</span>
        </div>

        {/* Desktop Header */}
        <header className="hidden lg:flex h-20 bg-[#F8FAFC] items-center justify-between px-8">
          <div>
            <h2 className="text-xl font-bold text-slate-800">{title}</h2>
          </div>
          <div className="flex items-center gap-6">
            <div className="relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search..." 
                className="pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 w-64 shadow-sm"
              />
            </div>
            <button className="relative p-2 rounded-full hover:bg-white border border-transparent hover:border-slate-200 hover:shadow-sm transition-all text-slate-500">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-[#F8FAFC]"></span>
            </button>
            <div className="flex items-center gap-3 pl-6 border-l border-slate-200">
              <div className="text-right">
                <p className="text-sm font-semibold text-slate-800">{userName}</p>
                <p className="text-xs font-medium text-slate-500 capitalize">{role}</p>
              </div>
              <img src="https://i.pravatar.cc/150?img=32" alt="Avatar" className="w-10 h-10 rounded-full border-2 border-white shadow-sm object-cover" />
            </div>
          </div>
        </header>

        <div className="p-4 sm:p-6 lg:px-8 lg:py-6 flex-1">
          {children}
        </div>
      </main>
    </div>
  )
}
