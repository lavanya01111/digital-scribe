import React, { useRef, useEffect, useState } from 'react';

const DrawingBoard = ({ onProcess }) => {
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);

    // Initialize canvas
    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        // Set white background instead of transparent
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        // Stroke settings
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#000000';
    }, []);

    const startDrawing = (e) => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const rect = canvas.getBoundingClientRect();

        // Support touching & mouse
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        ctx.beginPath();
        ctx.moveTo(clientX - rect.left, clientY - rect.top);
        setIsDrawing(true);
    };

    const draw = (e) => {
        if (!isDrawing) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const rect = canvas.getBoundingClientRect();

        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        ctx.lineTo(clientX - rect.left, clientY - rect.top);
        ctx.stroke();
    };

    const endDrawing = () => {
        setIsDrawing(false);
    };

    const clearCanvas = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    };

    const handleSubmit = () => {
        const canvas = canvasRef.current;
        const base64Image = canvas.toDataURL('image/png');
        onProcess(base64Image);
        // Optionally clear canvas after submit
        clearCanvas();
    };

    return (
        <div className="flex flex-col gap-4">
            <div className="border-2 border-slate-200 rounded-lg overflow-hidden touch-none relative bg-white">
                <canvas
                    ref={canvasRef}
                    width={800}
                    height={400}
                    className="w-full h-auto cursor-crosshair"
                    style={{ touchAction: 'none' }}
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={endDrawing}
                    onMouseOut={endDrawing}
                    onTouchStart={startDrawing}
                    onTouchMove={draw}
                    onTouchEnd={endDrawing}
                />
            </div>
            <div className="flex justify-between">
                <button
                    onClick={clearCanvas}
                    className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition"
                >
                    Clear Canvas
                </button>
                <button
                    onClick={handleSubmit}
                    className="px-6 py-2 bg-scribe-primary text-white font-medium rounded-lg shadow hover:bg-blue-600 transition"
                >
                    Transcribe Writing
                </button>
            </div>
        </div>
    );
};

export default DrawingBoard;
