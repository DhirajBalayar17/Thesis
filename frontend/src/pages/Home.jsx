import React, { useState, useEffect } from 'react';
import { Camera, Sparkles, Zap, Users, Star, ArrowRight, Upload, Smartphone } from 'lucide-react';

const Home = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % 3);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const testimonials = [
    { name: "Sarah M.", rating: 5, text: "Found my perfect size instantly! No more returns." },
    { name: "Mike R.", rating: 5, text: "The AI recommendations are spot-on. Love my new style!" },
    { name: "Emma L.", rating: 5, text: "Shopping has never been this easy and accurate." }
  ];

  const features = [
    { icon: Camera, title: "AI Body Analysis", desc: "Advanced computer vision measures your body with precision" },
    { icon: Sparkles, title: "Smart Recommendations", desc: "Personalized outfit suggestions based on your measurements" },
    { icon: Zap, title: "Instant Results", desc: "Get your perfect fit in seconds, not hours" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50 overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-100 rounded-full mix-blend-multiply filter blur-xl opacity-40 animate-pulse"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-emerald-100 rounded-full mix-blend-multiply filter blur-xl opacity-40 animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 w-72 h-72 bg-cyan-100 rounded-full mix-blend-multiply filter blur-xl opacity-40 animate-pulse delay-2000"></div>
      </div>

      <div className="relative z-10">
        {/* Hero Section */}
        <section className="px-6 py-20">
          <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
            <div className={`space-y-8 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium">
                <Star className="w-4 h-4 fill-current" />
                <span></span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-extrabold leading-tight">
                <span className="bg-gradient-to-r from-blue-600 via-emerald-500 to-cyan-600 bg-clip-text text-transparent">
                  Smarter Fitting.
                </span>
                <br />
                <span className="text-gray-800">Styled by AI.</span>
              </h1>
              
             
              
              <div className="flex flex-col sm:flex-row gap-4">
                <a
                  href="/measure"
                  className="group inline-flex items-center justify-center bg-gradient-to-r from-blue-500 to-emerald-500 text-white px-8 py-4 rounded-2xl hover:from-blue-600 hover:to-emerald-600 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-2xl font-semibold text-lg"
                >
                  <Camera className="w-5 h-5 mr-2" />
                  Get Your Perfect Fit
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </a>
                
                
              </div>
              
              <div className="flex items-center space-x-6 pt-4">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-400 to-emerald-400 border-2 border-white flex items-center justify-center text-white font-bold text-sm">
                      {String.fromCharCode(64 + i)}
                    </div>
                  ))}
                </div>
                <div className="text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star key={star} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                 
                </div>
              </div>
            </div>
            
            {/* Hero Image/Illustration */}
            <div className={`relative transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="relative bg-gradient-to-br from-blue-50 to-emerald-50 rounded-3xl p-12 shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-300/20 to-emerald-300/20 rounded-3xl"></div>
                
                {/* Phone mockup */}
                <div className="relative bg-gray-900 rounded-[3rem] p-2 shadow-2xl transform rotate-6 hover:rotate-3 transition-transform duration-500">
                  <div className="bg-white rounded-[2.5rem] p-6 h-96">
                    <div className="w-full h-full bg-gradient-to-br from-blue-50 to-emerald-50 rounded-2xl flex flex-col items-center justify-center space-y-4">
                      <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-2xl flex items-center justify-center">
                        <Smartphone className="w-10 h-10 text-white" />
                      </div>
                      <div className="text-center space-y-2">
                        <div className="text-lg font-bold text-gray-800">AI Analysis</div>
                        <div className="text-sm text-gray-600">Perfect fit found!</div>
                      </div>
                      <div className="w-full space-y-2">
                        {[85, 92, 78].map((width, i) => (
                          <div key={i} className="bg-blue-100 h-2 rounded-full overflow-hidden">
                            <div 
                              className="bg-gradient-to-r from-blue-500 to-emerald-500 h-full rounded-full transition-all duration-1000 delay-500"
                              style={{ width: `${width}%` }}
                            ></div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Floating elements */}
                <div className="absolute top-4 right-4 bg-white rounded-2xl p-4 shadow-lg animate-bounce delay-1000">
                  <Zap className="w-6 h-6 text-yellow-500" />
                </div>
                <div className="absolute bottom-4 left-4 bg-white rounded-2xl p-4 shadow-lg animate-bounce delay-2000">
                  <Sparkles className="w-6 h-6 text-emerald-500" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="px-6 py-20 bg-white/30 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
                Why Choose <span className="bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">FitAI</span>?
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Experience the future of online shopping with our cutting-edge AI technology
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div 
                  key={index}
                  className="group bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-white/50"
                >
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-800 mb-3">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Social Proof */}
        <section className="px-6 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-white/80 backdrop-blur-lg rounded-3xl p-8 shadow-xl border border-white/30">
              <div className="flex items-center justify-center space-x-1 mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star key={star} className="w-6 h-6 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <blockquote className="text-2xl font-medium text-gray-800 mb-4 transition-all duration-500">
                "{testimonials[currentTestimonial].text}"
              </blockquote>
              <cite className="text-lg text-blue-600 font-semibold">
                - {testimonials[currentTestimonial].name}
              </cite>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="px-6 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gradient-to-r from-blue-500 to-emerald-500 rounded-3xl p-12 shadow-2xl">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Ready to Find Your Perfect Fit?
              </h2>
              <p className="text-xl text-blue-50 mb-8 max-w-2xl mx-auto">
                Join thousands of satisfied customers who never worry about sizing again.
              </p>
              <a
                href="/measure"
                className="inline-flex items-center bg-white text-blue-600 px-8 py-4 rounded-2xl hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl font-semibold text-lg"
              >
                <Camera className="w-5 h-5 mr-2" />
                Start Your AI Fitting Now
                <ArrowRight className="w-5 h-5 ml-2" />
              </a>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Home;