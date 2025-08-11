// src/components/PoseOverlay.jsx
import React from 'react';

const PoseOverlay = ({ view = "side" }) => {
  const instructionText =
    view === 'front'
      ? 'Step 1: Stand facing the camera'
      : view === 'side'
      ? 'Step 2: Turn sideways (left or right)'
      : 'Step 3: Turn around, back to camera';

  return (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none z-20">
      {/* Green full-frame box */}
      <div className="absolute top-10 left-10 right-10 bottom-10 border-4 border-green-500"></div>

      {/* Pink inner box (side pose size) */}
      <div className="absolute top-14 left-[20%] right-[20%] bottom-14 border-4 border-pink-500"></div>

      {/* Center vertical dashed line */}
      <div className="absolute top-0 bottom-0 left-1/2 border-l-2 border-dashed border-black"></div>

      {/* Pose image and instruction */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 bg-black/50 px-4 py-2 rounded-xl text-white text-sm font-semibold text-center z-30">
        <img
          src={`/images/pose-${view}.png`}
          alt={`${view} pose`}
          className="w-20 h-auto mx-auto mb-2 opacity-90"
        />
        {instructionText}
      </div>
    </div>
  );
};

export default PoseOverlay;
