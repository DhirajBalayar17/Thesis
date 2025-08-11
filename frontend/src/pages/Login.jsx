import React from 'react';
import { useNavigate } from 'react-router-dom';
import { X } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-purple-900/20 via-pink-900/20 to-indigo-900/20 backdrop-blur-xl flex items-center justify-center px-4">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -right-40 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      <div className="relative w-full max-w-md">
        {/* Glassmorphism container with enhanced effects */}
        <div className="relative bg-white/10 backdrop-blur-2xl p-8 rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
          {/* Subtle gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent rounded-3xl"></div>
          
          {/* Animated border effect */}
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-indigo-500/20 p-px">
            <div className="w-full h-full bg-white/5 rounded-3xl"></div>
          </div>

          {/* Cross Button with enhanced styling */}
          <button
            onClick={() => navigate('/')}
            className="absolute top-4 right-4 z-10 text-white/70 hover:text-white hover:bg-white/10 rounded-full p-2 transition-all duration-300 hover:scale-110 hover:rotate-90"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Content container */}
          <div className="relative z-10">
            {/* Enhanced title with gradient text */}
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 bg-clip-text text-transparent mb-2">
                Welcome Back
              </h2>
              <p className="text-white/60 text-sm">Sign in to your account</p>
            </div>

            <form className="space-y-6">
              <div className="group">
                <label className="block mb-2 text-sm font-medium text-white/80 group-focus-within:text-purple-300 transition-colors duration-300">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    placeholder="you@example.com"
                    className="w-full px-4 py-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl text-white placeholder-white/40 focus:border-purple-400/50 focus:bg-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400/20 transition-all duration-300 hover:bg-white/8"
                  />
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                </div>
              </div>

              <div className="group">
                <label className="block mb-2 text-sm font-medium text-white/80 group-focus-within:text-purple-300 transition-colors duration-300">
                  Password
                </label>
                <div className="relative">
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full px-4 py-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl text-white placeholder-white/40 focus:border-purple-400/50 focus:bg-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400/20 transition-all duration-300 hover:bg-white/8"
                  />
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                </div>
              </div>

              {/* Premium button with gradient and hover effects */}
              <button
                type="submit"
                className="w-full relative overflow-hidden bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 text-white py-4 rounded-2xl font-semibold text-lg shadow-lg hover:shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 hover:scale-[1.02] group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-700 via-pink-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <span className="relative z-10">Sign In</span>
                
                {/* Animated shine effect */}
                <div className="absolute inset-0 -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
              </button>
            </form>

            {/* Enhanced cancel button */}
            <button
              onClick={() => navigate('/')}
              className="block mx-auto mt-8 text-sm text-white/60 hover:text-white px-4 py-2 rounded-xl hover:bg-white/5 transition-all duration-300 hover:scale-105"
            >
              Cancel
            </button>
          </div>

          {/* Decorative elements */}
          <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-purple-400/20 to-transparent rounded-full blur-2xl -translate-x-16 -translate-y-16"></div>
          <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tl from-pink-400/20 to-transparent rounded-full blur-2xl translate-x-16 translate-y-16"></div>
        </div>
      </div>
    </div>
  );
};

export default Login;