// src/pages/Measure.jsx
import React, { useRef, useEffect, useState, useCallback } from "react";
import { Pose } from "@mediapipe/pose";
import { Camera } from "@mediapipe/camera_utils";
import { Camera as CameraIcon, Sparkles, Activity, Target, RotateCcw, Download } from 'lucide-react';

/* ---------- Calibration ---------- */
const A4_WIDTH_CM = 21.0; // reference width
const CHEST_MULTIPLIER = 1.75; // shoulder flat → chest circumference (tune 1.70–1.85)
const UPPER_WAIST_FACTOR = 0.90; // hip width ≈ a bit wider than upper waist

/* ---------- Overlay helpers ---------- */
const UPPER = [
  [0,1],[1,2],[2,3],[3,7],
  [0,11],[0,12],
  [11,13],[13,15],
  [12,14],[14,16],
  [11,12],
  [11,23],[12,24],
];
const LOWER = [
  [23,25],[25,27],[27,31],
  [24,26],[26,28],[28,32],
  [23,24],
];
const drawSeg = (ctx, lm, a, b, color, width, W, H) => {
  const A = lm[a], B = lm[b];
  if (!A || !B) return;
  if ((A.visibility ?? 0) < 0.4 || (B.visibility ?? 0) < 0.4) return;
  ctx.strokeStyle = color; ctx.lineWidth = width;
  ctx.beginPath(); ctx.moveTo(A.x*W, A.y*H); ctx.lineTo(B.x*W, B.y*H); ctx.stroke();
};
const drawBBox = (ctx, lm, W, H, color="rgba(0,255,0,0.9)") => {
  const pts = lm.filter(p => (p?.visibility ?? 0) > 0.4);
  if (!pts.length) return;
  const xs = pts.map(p=>p.x*W), ys = pts.map(p=>p.y*H);
  const minX = Math.max(0, Math.min(...xs)), maxX = Math.min(W, Math.max(...xs));
  const minY = Math.max(0, Math.min(...ys)), maxY = Math.min(H, Math.max(...ys));
  const pad = 8; ctx.strokeStyle = color; ctx.lineWidth = 3;
  ctx.strokeRect(minX-pad, minY-pad, (maxX-minX)+pad*2, (maxY-minY)+pad*2);
};

/* ---------- Size recommendation (using all three measurements) ---------- */
const recommendTopSize = (chestCm, waistCm, shoulderCm) => {
  if (!chestCm || !waistCm || !shoulderCm || chestCm <= 0 || waistCm <= 0 || shoulderCm <= 0) {
    return null;
  }
  
  // Simplified sizing algorithm that only recommends L or XL
  // L and XL are recommended interchangeably based on measurements
  
  // Calculate a score based on measurements to determine L vs XL
  let lScore = 0;
  let xlScore = 0;
  
  // Chest measurement scoring
  if (chestCm >= 100) xlScore += 3;       // Very large chest favors XL
  else if (chestCm >= 95) xlScore += 2;   // Large chest favors XL
  else if (chestCm >= 90) xlScore += 1;   // Medium-large chest slightly favors XL
  else if (chestCm >= 85) lScore += 2;    // Medium chest favors L
  else if (chestCm >= 80) lScore += 1;    // Small-medium chest slightly favors L
  
  // Shoulder measurement scoring
  if (shoulderCm >= 48) xlScore += 2;     // Very broad shoulders favor XL
  else if (shoulderCm >= 45) xlScore += 1; // Broad shoulders slightly favor XL
  else if (shoulderCm >= 42) lScore += 2;  // Medium shoulders favor L
  else if (shoulderCm >= 38) lScore += 1;  // Small-medium shoulders slightly favor L
  
  // Waist measurement scoring
  if (waistCm >= 85) xlScore += 2;        // Large waist favors XL
  else if (waistCm >= 80) xlScore += 1;   // Medium-large waist slightly favors XL
  else if (waistCm >= 75) lScore += 2;    // Medium waist favors L
  else if (waistCm >= 70) lScore += 1;    // Small-medium waist slightly favors L
  
  // Determine final size based on scores
  let finalSize = 'L'; // Default to L (most common recommendation)
  
  if (xlScore > lScore) {
    finalSize = 'XL';
  }
  
  // Log the calculation for debugging
  console.log(`Size Calculation (L/XL only):`, {
    chestCm,
    waistCm, 
    shoulderCm,
    lScore,
    xlScore,
    finalSize,
    reasoning: finalSize === 'XL' ? 'XL recommended (larger frame)' : 'L recommended (medium frame)'
  });
  
  return finalSize;
};

// Optional style hint based on proportions (very light heuristic)
const styleHint = (chestCm, shoulderCm) => {
  if (!chestCm || !shoulderCm) return "";
  const ratio = chestCm / (shoulderCm || 1); // ~3–5 normal range
  if (ratio < 3.6) return "Try regular/relaxed fits.";
  if (ratio > 4.6) return "Slim or tailored fits may suit better.";
  return "Regular fit is likely comfortable.";
};

// Add error handling wrapper at the top of the component
const MediaPipeErrorBoundary = ({ children }) => {
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (hasError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="bg-white/95 backdrop-blur-md rounded-3xl p-8 max-w-lg text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">MediaPipe Error</h2>
          <p className="text-gray-600 mb-6">{errorMessage}</p>
          <div className="space-y-3">
            <button 
              onClick={() => window.location.reload()}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-medium"
            >
              🔄 Refresh Page
            </button>
            <button 
              onClick={() => setHasError(false)}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-3 rounded-xl font-medium"
            >
              🚫 Dismiss
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary
      onError={(error) => {
        console.error('MediaPipe Error:', error);
        setErrorMessage(error.message || 'An error occurred with MediaPipe');
        setHasError(true);
      }}
    >
      {children}
    </ErrorBoundary>
  );
};

// Simple ErrorBoundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    if (this.props.onError) {
      this.props.onError(error);
    }
  }

  render() {
    if (this.state.hasError) {
      return null; // Let parent handle the error display
    }
    return this.props.children;
  }
}

export default function Measure() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const poseRef = useRef(null);
  const camRef = useRef(null);

  const [phase, setPhase] = useState("calibrate"); // 'calibrate' | 'measure' | 'locked'
  const [status, setStatus] = useState("Hold an A4 sheet at chest level and match the bar width.");
  const [barPx, setBarPx] = useState(300);
  const [cmPerPx, setCmPerPx] = useState(null);
 // 'Men' | 'Women' | 'Unisex'

  const [locked, setLocked] = useState(false);
  const [meas, setMeas] = useState(null); // { chestCm, shoulderCm, upperWaistCm, quality }

  // stability settings
  const GUIDE_MARGIN = 0.08;
  const STABILITY_FRAMES = 12;
  const MOVEMENT_EPS = 0.015;
  const recentShoulderN = useRef([]);
  const chestBuf = useRef([]);
  const shoulderBuf = useRef([]);
  const waistBuf = useRef([]);

  const getDistance = useCallback((a,b)=>Math.hypot(a.x-b.x,a.y-b.y),[]);

  const stopCamera = () => {
    try {
      camRef.current?.stop?.();
      const v = videoRef.current;
      v?.srcObject && v.srcObject.getTracks().forEach(t=>t.stop());
      if (v) v.srcObject = null;
    } catch {}
  };

  const startCamera = async (pose) => {
    const v = videoRef.current;
    const camera = new Camera(v, {
      onFrame: async () => { await pose.send({ image: v }); },
      width: 1280, height: 720,
    });
    camRef.current = camera;
    camera.start();
  };

    useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // Simple MediaPipe initialization with error handling
    try {
      const pose = new Pose({
        // Load from local public assets & force non‑SIMD to avoid WASM crash
        locateFile: (file) => `/mediapipe/pose/${file.replace('simd_', '')}`,
      });
      poseRef.current = pose;

      pose.setOptions({
        modelComplexity: 0, // Use lowest complexity to avoid crashes
        smoothLandmarks: true,
        enableSegmentation: false,
        minDetectionConfidence: 0.6, // Higher confidence for stability
        minTrackingConfidence: 0.6,
      });

      pose.onResults((res) => {
        if (locked) return;

        const W = res.image.width, H = res.image.height;
        if (canvas.width !== W) canvas.width = W;
        if (canvas.height !== H) canvas.height = H;

      ctx.save();
      ctx.clearRect(0,0,W,H);
      ctx.drawImage(res.image,0,0,W,H);

      // Enhanced guide box with gradient
      const gx = W*GUIDE_MARGIN, gy = H*GUIDE_MARGIN;
      const gW = W*(1-GUIDE_MARGIN*2), gH = H*(1-GUIDE_MARGIN*2);
      const gradient = ctx.createLinearGradient(gx, gy, gx + gW, gy + gH);
      gradient.addColorStop(0, "rgba(59, 130, 246, 0.8)"); // Blue
      gradient.addColorStop(0.5, "rgba(16, 185, 129, 0.8)"); // Emerald
      gradient.addColorStop(1, "rgba(139, 92, 246, 0.8)"); // Purple
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 4; 
      ctx.strokeRect(gx, gy, gW, gH);

      // calibration bar with better styling
      if (phase === "calibrate") {
        const barH = 20;
        const barY = H * 0.12;
        
        // Bar background with gradient
        const barGradient = ctx.createLinearGradient((W-barPx)/2, barY, (W-barPx)/2 + barPx, barY);
        barGradient.addColorStop(0, "rgba(59, 130, 246, 0.9)");
        barGradient.addColorStop(1, "rgba(16, 185, 129, 0.9)");
        ctx.fillStyle = barGradient;
        ctx.fillRect((W-barPx)/2, barY, barPx, barH);
        
        // Bar border
        ctx.strokeStyle = "rgba(255, 255, 255, 0.9)";
        ctx.lineWidth = 2;
        ctx.strokeRect((W-barPx)/2, barY, barPx, barH);
        
        // Instruction text with better styling
        ctx.font = "16px system-ui, -apple-system, sans-serif";
        ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
        ctx.strokeStyle = "rgba(0, 0, 0, 0.5)";
        ctx.lineWidth = 3;
        const text = "Match this bar to A4 width (21 cm) at chest depth";
        const textX = Math.max(20, (W - ctx.measureText(text).width) / 2);
        ctx.strokeText(text, textX, barY - 15);
        ctx.fillText(text, textX, barY - 15);
      }

      const lm = res.poseLandmarks;
      if (!lm) { setStatus("Detecting body…"); ctx.restore(); return; }

      // Enhanced overlay with better colors
      drawBBox(ctx, lm, W, H, "rgba(16, 185, 129, 0.9)");
      UPPER.forEach(([a,b])=>drawSeg(ctx,lm,a,b,"#3B82F6",4,W,H)); // Blue
      LOWER.forEach(([a,b])=>drawSeg(ctx,lm,a,b,"#F59E0B",4,W,H)); // Amber

      const vis = (i) => (lm[i]?.visibility ?? 0) > 0.45;
      const shouldersOK = vis(11) && vis(12);
      const hipsOK = vis(23) || vis(24);
      if (!(shouldersOK && hipsOK)) { setStatus("Show shoulders & upper torso."); ctx.restore(); return; }

      const Lsh = lm[11], Rsh = lm[12];
      const Lhip = lm[23], Rhip = lm[24];
      const hip = vis(23) ? Lhip : Rhip;

      // Enhanced key dots with glow effect
      const shMid = { x:(Lsh.x+Rsh.x)/2, y:(Lsh.y+Rsh.y)/2 };
      const keyPoints = [
        { point: Lsh, color: "#3B82F6" },
        { point: Rsh, color: "#3B82F6" },
        { point: shMid, color: "#10B981" },
        { point: hip, color: "#F59E0B" }
      ];
      
      keyPoints.forEach(({point, color}) => {
        if (point) {
          // Glow effect
          ctx.shadowColor = color;
          ctx.shadowBlur = 15;
          ctx.fillStyle = color;
          ctx.beginPath(); 
          ctx.arc(point.x*W, point.y*H, 8, 0, Math.PI*2); 
          ctx.fill();
          
          // Inner bright dot
          ctx.shadowBlur = 0;
          ctx.fillStyle = "white";
          ctx.beginPath(); 
          ctx.arc(point.x*W, point.y*H, 4, 0, Math.PI*2); 
          ctx.fill();
        }
      });
      ctx.shadowBlur = 0;

      // must be inside guide
      const inside = [Lsh,Rsh,hip].every(p => p.x*W>=gx && p.x*W<=gx+gW && p.y*H>=gy && p.y*H<=gy+gH);
      if (!inside) { setStatus("Step back/center inside the frame."); ctx.restore(); return; }

      if (phase === "calibrate") { setStatus("Adjust bar → Set calibration."); ctx.restore(); return; }
      if (!cmPerPx) { setStatus("Click Set calibration first."); ctx.restore(); return; }

      // normalized stability
      const shoulderWidthN = getDistance(Lsh,Rsh);
      const torsoHeightN = getDistance(shMid, hip);
      if (torsoHeightN <= 0) { setStatus("Hold still…"); ctx.restore(); return; }

      const bufN = recentShoulderN.current;
      bufN.push(shoulderWidthN); if (bufN.length > STABILITY_FRAMES) bufN.shift();
      const avg = bufN.reduce((a,b)=>a+b,0)/bufN.length;
      const maxDev = Math.max(...bufN.map(v=>Math.abs(v-avg)));

      // ----- measurements in cm -----
      const shoulderPx = Math.abs((Lsh.x - Rsh.x) * W);
      const shoulderCm = shoulderPx * cmPerPx;

      const chestCmInstant = shoulderCm * CHEST_MULTIPLIER;

      let upperWaistCmInstant = null;
      if (vis(23) && vis(24)) {
        const hipFlatCm = Math.abs((Lhip.x - Rhip.x) * W) * cmPerPx;
        upperWaistCmInstant = hipFlatCm * UPPER_WAIST_FACTOR;
      }

      // median smoothing
      const pushMed = (ref, val, n=15) => {
        if (val==null) return null;
        ref.current.push(val);
        if (ref.current.length>n) ref.current.shift();
        const s=[...ref.current].sort((a,b)=>a-b);
        const m=Math.floor(s.length/2);
        return s.length%2 ? s[m] : (s[m-1]+s[m])/2;
      };
      const chestMed = pushMed(chestBuf, chestCmInstant);
      const shoulderMed = pushMed(shoulderBuf, shoulderCm);
      const waistMed = pushMed(waistBuf, upperWaistCmInstant);

      // stability: normalized shoulders + cm spread
      const spread = chestBuf.current.length>=8 ? Math.max(...chestBuf.current)-Math.min(...chestBuf.current) : 999;
      const stable = bufN.length>=STABILITY_FRAMES && maxDev < MOVEMENT_EPS && spread < 1.8; // slightly relaxed

      if (stable && chestMed && shoulderMed) {
        const out = {
          chestCm: Number(chestMed.toFixed(1)),
          shoulderCm: Number(shoulderMed.toFixed(1)),
          upperWaistCm: waistMed ? Number(waistMed.toFixed(1)) : undefined,
          quality: { frames: chestBuf.current.length, spreadCm: Number(spread.toFixed(2)) }
        };
        setMeas(out);
        setLocked(true);
        setPhase("locked");
        setStatus("Locked ✔️");
        stopCamera();
      } else {
        setStatus("Hold still…");
      }

      ctx.restore();
    });

    startCamera(pose);
    return () => { stopCamera(); };
  } catch (error) {
    console.error("❌ MediaPipe initialization failed:", error);
    setStatus(`MediaPipe Error: ${error.message}. Please refresh the page.`);
    setPhase("error");
  }
  }, [phase, cmPerPx, getDistance, locked, barPx]);

  const setCalibration = () => {
    if (barPx < 40) return;
    setCmPerPx(A4_WIDTH_CM / barPx);
    setPhase("measure");
    setStatus("Calibration set. Stand centered; shoulders & upper torso visible.");
    // reset buffers
    chestBuf.current = []; shoulderBuf.current = []; waistBuf.current = []; recentShoulderN.current = [];
  };

  const retake = () => {
    setLocked(false); setMeas(null); setPhase("measure");
    setStatus("Stand centered; hold still 1–2 seconds.");
    chestBuf.current = []; shoulderBuf.current = []; waistBuf.current = []; recentShoulderN.current = [];
    if (poseRef.current) startCamera(poseRef.current);
  };

  const recalibrate = () => {
    setLocked(false); setMeas(null); setPhase("calibrate");
    setStatus("Hold an A4 sheet at chest level and match the bar width.");
    chestBuf.current = []; shoulderBuf.current = []; waistBuf.current = []; recentShoulderN.current = [];
    if (poseRef.current) startCamera(poseRef.current);
  };

  // Helper functions for UI
  const getStatusIcon = () => {
    if (phase === "locked") return <span className="text-emerald-500 text-xl">✅</span>;
    if (phase === "measure") return <Activity className="w-5 h-5 text-blue-500 animate-pulse" />;
    return <Target className="w-5 h-5 text-amber-500" />;
  };

  const getPhaseColor = () => {
    if (phase === "locked") return "from-emerald-500 to-green-500";
    if (phase === "measure") return "from-blue-500 to-cyan-500";
    return "from-amber-500 to-orange-500";
  };

  return (
    <MediaPipeErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute top-10 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl animate-pulse delay-2000"></div>
        </div>

        <div className="relative z-10 flex flex-col items-center min-h-screen">
          {/* Enhanced Header */}
          <div className="w-full max-w-7xl flex items-center justify-between px-6 py-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI Fashion Fit</h1>
                <p className="text-sm text-blue-200">Body Measurement System</p>
              </div>
            </div>
            
            {/* Enhanced Status Badge */}
            <div className="flex items-center space-x-3">
              <div className={`bg-gradient-to-r ${getPhaseColor()} rounded-full px-6 py-3 shadow-lg backdrop-blur-sm border border-white/10`}>
                <div className="flex items-center space-x-3 text-white">
                  {getStatusIcon()}
                  <span className="font-medium text-sm">{status}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Camera Section */}
          <div className="w-full max-w-6xl px-6 flex-1 flex items-center">
            <div className="relative w-full bg-black/20 backdrop-blur-lg rounded-3xl overflow-hidden shadow-2xl border border-white/10">
              <div className="relative aspect-video">
                <video ref={videoRef} className="absolute inset-0 w-full h-full object-contain bg-black rounded-3xl" autoPlay muted playsInline />
                <canvas ref={canvasRef} className="absolute inset-0 w-full h-full object-contain pointer-events-none" />

                {/* Enhanced Calibration UI */}
                {phase === "calibrate" && (
                  <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2">
                    <div className="bg-white/95 backdrop-blur-md rounded-2xl px-6 py-4 shadow-2xl border border-white/20">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <Target className="w-5 h-5 text-amber-600" />
                          <span className="text-sm font-medium text-gray-700">A4 width calibration</span>
                        </div>
                        <input 
                          type="range" 
                          min={120} 
                          max={900} 
                          value={barPx} 
                          onChange={(e)=>setBarPx(Number(e.target.value))} 
                          className="w-64 accent-blue-500"
                        />
                        <button 
                          onClick={setCalibration} 
                          className="bg-gradient-to-r from-blue-500 to-emerald-500 hover:from-blue-600 hover:to-emerald-600 text-white px-6 py-2 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center space-x-2"
                        >
                          <span className="text-white text-lg">✅</span>
                          <span>Set Calibration</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}




              </div>
            </div>
          </div>



          {/* Enhanced Instructions */}
          <div className="w-full max-w-4xl px-6 py-4">
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <div className="text-center text-white">
                <div className="flex items-center justify-center space-x-2 mb-3">
                  <CameraIcon className="w-5 h-5 text-blue-300" />
                  <h3 className="font-semibold">Instructions</h3>
                </div>
                <div className="text-sm text-white/80 space-y-2">
                  {phase === "calibrate" && (
                    <p>📄 Hold an A4 sheet at chest level and adjust the bar to match its width for accurate calibration.</p>
                  )}
                  {phase === "measure" && (
                    <p>🧍 Stand straight with arms slightly away from your body. Hold still for precise measurement.</p>
                  )}
                  {phase === "locked" && (
                    <p>✅ Measurements captured successfully! You can retake if needed or save your results.</p>
                  )}
                  <p className="text-blue-200 font-medium">📏 Size System: Only L and XL sizes available (L and XL recommended interchangeably)</p>
                </div>
              </div>
            </div>
          </div>

          {/* Fallback Results Display - Always visible when measurements exist */}
          {phase === "locked" && meas && (
            <div className="w-full max-w-4xl px-6 py-6">
              <div className="bg-white/95 backdrop-blur-md rounded-2xl p-6 border border-gray-200 shadow-xl">
                <div className="text-center text-gray-800">
                  <h3 className="text-xl font-bold mb-4">📊 Measurement Results</h3>
                  
                  {/* Measurements Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                      <div className="text-2xl font-bold text-blue-600">{meas.chestCm?.toFixed(1) || 'N/A'}</div>
                      <div className="text-sm text-blue-500">Chest (cm)</div>
                    </div>
                    <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
                      <div className="text-2xl font-bold text-emerald-600">{meas.shoulderCm?.toFixed(1) || 'N/A'}</div>
                      <div className="text-sm text-emerald-500">Shoulder (cm)</div>
                    </div>
                    <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
                      <div className="text-2xl font-bold text-purple-600">{meas.upperWaistCm?.toFixed(1) || 'N/A'}</div>
                      <div className="text-sm text-purple-500">Waist (cm)</div>
                    </div>
                  </div>

                  {/* Size Recommendation */}
                  <div className="bg-gradient-to-r from-blue-50 to-emerald-50 rounded-xl p-4 mb-6 border border-blue-200">
                    <div className="text-lg font-semibold text-gray-700 mb-2">Recommended Size</div>
                    <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">
                      {recommendTopSize(meas.chestCm, meas.upperWaistCm, meas.shoulderCm)}
                    </div>
                    <div className="text-sm text-gray-600 mt-2">
                      Based on your measurements, we recommend size <strong>{recommendTopSize(meas.chestCm, meas.upperWaistCm, meas.shoulderCm)}</strong>
                    </div>
                                      <div className="text-xs text-gray-500 mt-1">
                    Available sizes: L (most common) and XL
                  </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <button 
                      onClick={retake}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-3 rounded-xl font-medium transition-all duration-300 border-2 border-gray-300"
                    >
                      🔄 Retake
                    </button>
                    <button 
                      onClick={recalibrate}
                      className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-6 py-3 rounded-xl font-medium transition-all duration-300 border-2 border-blue-300"
                    >
                      🎯 Recalibrate
                    </button>
                    <button 
                      onClick={() => {
                        const recommendedSize = recommendTopSize(meas.chestCm, meas.upperWaistCm, meas.shoulderCm);
                        if (recommendedSize) {
                          // Pass all measurement data to recommendations page
                          const measurementData = encodeURIComponent(JSON.stringify({
                            size: recommendedSize,
                            gender: 'Men',
                            measurements: {
                              chestCm: meas.chestCm,
                              shoulderCm: meas.shoulderCm,
                              upperWaistCm: meas.upperWaistCm
                            }
                          }));
                          window.location.href = `/recommendations?data=${measurementData}`;
                        }
                      }}
                      className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 shadow-lg"
                    >
                      ✨ Get Recommendations
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </MediaPipeErrorBoundary>
  );
}