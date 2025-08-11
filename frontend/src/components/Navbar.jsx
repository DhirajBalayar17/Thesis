import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

const Navbar = () => {
  return (
    <nav className="bg-white/95 backdrop-blur-md shadow-lg border-b border-white/20 px-6 py-4 flex justify-between items-center sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">
          AI Fashion Fit
        </div>
      </div>
      
      <ul className="flex gap-6">
        <li>
          <Link 
            to="/" 
            className="text-gray-700 hover:text-blue-600 font-medium transition-all duration-300 relative group"
          >
            Home
            <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-emerald-500 group-hover:w-full transition-all duration-300"></span>
          </Link>
        </li>
        <li>
         
        </li>
        <li>
          <Link 
            to="/contact" 
            className="text-gray-700 hover:text-blue-600 font-medium transition-all duration-300 relative group"
          >
            Contact
            <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-emerald-500 group-hover:w-full transition-all duration-300"></span>
          </Link>
        </li>
      </ul>
      
      <Link
        to="/login"
        className="bg-gradient-to-r from-blue-500 to-emerald-500 hover:from-blue-600 hover:to-emerald-600 text-white px-4 py-2 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
      >
        Login
      </Link>
    </nav>
  );
};

export default Navbar;