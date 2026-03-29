// src/components/Canvas.jsx
// Handwriting input canvas. Supports mouse, touch, and stylus.
// On submit, captures canvas as PNG and sends to AI service.

import { useRef, useEffect, useState } from "react";
import { recognizeHandwriting } from "../lib/api";

export default function Canvas({ onTextRecognized }) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Set up canvas context once on mount
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.strokeStyle = "#000000";   // Black ink
    ctx.lineWidth = 3;             // Good width for stylus
    ctx.lineCap = "round";         // Smooth line endings
    ctx.lineJoin = "round";
    // White background (needed for HTR model)
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }, []);

  // Get pointer position for both mouse and touch events
  const getPos = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const touch = e.touches?.[0] || e;
    return {
      x: touch.clientX - rect.left,
      y: touch.clientY - rect.top,
    };
  };

  const startDraw = (e) => {
    const ctx = canvasRef.current.getContext("2d");
    const { x, y } = getPos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    const ctx = canvasRef.current.getContext("2d");
    const { x, y } = getPos(e);
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDraw = () => setIsDrawing(false);

  // Export canvas as base64 PNG and send to AI
  const handleSubmit = async () => {
    setIsLoading(true);
    const canvas = canvasRef.current;
    // toDataURL gives us "data:image/png;base64,..."
    const base64 = canvas.toDataURL("image/png").split(",")[1];
    const text = await recognizeHandwriting(base64);
    onTextRecognized(text);
    setIsLoading(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  };

  return (
    <div className="flex flex-col gap-4">
      <canvas
        ref={canvasRef}
        width={800} height={300}
        className="border-2 border-blue-400 rounded-xl bg-white cursor-crosshair touch-none"
        onMouseDown={startDraw} onMouseMove={draw}
        onMouseUp={stopDraw} onMouseLeave={stopDraw}
        onTouchStart={startDraw} onTouchMove={draw} onTouchEnd={stopDraw}
      />
      <div className="flex gap-3">
        <button onClick={handleSubmit} disabled={isLoading}
          className="bg-blue-600 text-white px-6 py-3 rounded-xl text-lg font-bold">
          {isLoading ? "Recognizing..." : "Submit Handwriting"}
        </button>
        <button onClick={clearCanvas}
          className="bg-gray-200 px-6 py-3 rounded-xl text-lg">
          Clear
        </button>
      </div>
    </div>
  );
}
