import React from 'react';
import { Sparkles, Mail, Phone, MapPin, Twitter, Instagram, Facebook, Linkedin, Heart, ArrowUp } from 'lucide-react';

const Footer = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const quickLinks = [
    { name: 'Home', href: '#' },
    { name: 'Features', href: '#features' },

  ];

  const support = [
    { name: 'Help Center', href: '#' },
    { name: 'Contact Us', href: '#contact' },
    { name: 'Size Guide', href: '#' },
    { name: 'Returns', href: '#' },
    { name: 'FAQ', href: '#' }
  ];

  const legal = [
    { name: 'Privacy Policy', href: '#' },
    { name: 'Terms of Service', href: '#' },
    { name: 'Cookie Policy', href: '#' },
    { name: 'GDPR', href: '#' }
  ];

  const socialLinks = [
  
    { icon: Instagram, href: '#', label: 'Instagram' },
    { icon: Facebook, href: '#', label: 'Facebook' },
 
  ];

  return (
    <footer className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-blue-900 text-white overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10">
       

        {/* Main Footer Content */}
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12">
            {/* Brand Section */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-xl flex items-center justify-center">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                  AI Fashion Fit
                </span>
              </div>
              <p className="text-gray-300 leading-relaxed max-w-md">
                Revolutionizing online fashion with cutting-edge AI technology. Find your perfect fit instantly and shop with confidence like never before.
              </p>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors">
                  <Mail className="w-5 h-5 text-blue-400" />
                  <span>dhirajbalayar69@gmail.com</span>
                </div>
                <div className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors">
                  <Phone className="w-5 h-5 text-emerald-400" />
                  <span>9766978321</span>
                </div>
                <div className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors">
                  <MapPin className="w-5 h-5 text-purple-400" />
                  <span>Kathmandu,Nepal</span>
                </div>
              </div>
            </div>

            {/* Quick Links */}
            <div className="space-y-6">
              <h4 className="text-lg font-semibold text-white">Quick Links</h4>
              <ul className="space-y-3">
                {quickLinks.map((link, index) => (
                  <li key={index}>
                    <a 
                      href={link.href}
                      className="text-gray-300 hover:text-white hover:translate-x-1 transition-all duration-200 flex items-center group"
                    >
                      <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Support */}
            <div className="space-y-6">
              <h4 className="text-lg font-semibold text-white">Support</h4>
              <ul className="space-y-3">
                {support.map((link, index) => (
                  <li key={index}>
                    <a 
                      href={link.href}
                      className="text-gray-300 hover:text-white hover:translate-x-1 transition-all duration-200 flex items-center group"
                    >
                      <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal */}
            <div className="space-y-6">
              <h4 className="text-lg font-semibold text-white">Legal</h4>
              <ul className="space-y-3">
                {legal.map((link, index) => (
                  <li key={index}>
                    <a 
                      href={link.href}
                      className="text-gray-300 hover:text-white hover:translate-x-1 transition-all duration-200 flex items-center group"
                    >
                      <span className="w-1.5 h-1.5 bg-purple-400 rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Social Links */}
          <div className="mt-12 pt-8 border-t border-gray-700/50">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-6 md:space-y-0">
              <div className="flex items-center space-x-6">
                <span className="text-gray-300 font-medium">Follow me:</span>
                <div className="flex space-x-4">
                  {socialLinks.map((social, index) => (
                    <a
                      key={index}
                      href={social.href}
                      aria-label={social.label}
                      className="w-10 h-10 bg-white/10 hover:bg-gradient-to-r hover:from-blue-500 hover:to-emerald-500 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-110 backdrop-blur-sm group"
                    >
                      <social.icon className="w-5 h-5 text-gray-300 group-hover:text-white transition-colors" />
                    </a>
                  ))}
                </div>
              </div>
              
              {/* Scroll to top button */}
              <button
                onClick={scrollToTop}
                className="w-10 h-10 bg-white/10 hover:bg-gradient-to-r hover:from-blue-500 hover:to-emerald-500 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-110 backdrop-blur-sm group"
                aria-label="Scroll to top"
              >
                <ArrowUp className="w-5 h-5 text-gray-300 group-hover:text-white transition-colors" />
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700/50 bg-black/20">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0 text-sm text-gray-400">
              <div className="flex items-center space-x-2">
                <span>&copy; {new Date().getFullYear()} AI Fashion Fit. All rights reserved.</span>
              </div>
              <div className="flex items-center space-x-2">
                <span>Crafted with</span>
                <Heart className="w-4 h-4 text-red-500 fill-current animate-pulse" />
                <span>by</span>
                <a 
                  href="#" 
                  className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                >
                  Dhiraj Balayar
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;