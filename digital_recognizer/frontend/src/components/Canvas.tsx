import { useState, useRef, useEffect } from "react";
import { RefreshCw } from "lucide-react";

export const Canvas = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [prediction, setPrediction] = useState<string | null>(null);
  const contextRef = useRef<CanvasRenderingContext2D | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.style.width = "100%";
    canvas.style.height = "100%";

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = 300 * dpr;
    canvas.height = 300 * dpr;

    const context = canvas.getContext("2d");
    if (!context) return;

    context.scale(dpr, dpr);
    context.lineCap = "round";
    context.lineJoin = "round";
    context.lineWidth = 12;
    context.strokeStyle = "#000000";
    contextRef.current = context;

    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
  }, []);

  const startDrawing = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    if (!canvas || !contextRef.current) return;

    const rect = canvas.getBoundingClientRect();
    const x =
      "touches" in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y =
      "touches" in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;

    contextRef.current.beginPath();
    contextRef.current.moveTo(x, y);
  };

  const draw = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    if (!isDrawing || !contextRef.current || !canvasRef.current) return;

    e.preventDefault();
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x =
      "touches" in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y =
      "touches" in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;

    contextRef.current.lineTo(x, y);
    contextRef.current.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    if (contextRef.current) {
      contextRef.current.closePath();
    }
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const context = contextRef.current;
    if (!canvas || !context) return;

    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
  };

  const handlePredict = async () => {
    if (!canvasRef.current || !contextRef.current) return;

    setIsPredicting(true);
    setPrediction(null);
    // Capture the image from the canvas
    const canvas = canvasRef.current;
    const dataURL = canvas.toDataURL("image/png"); // Get the base64 string representation of the image

    try {
      // Send the image to the Flask API
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // Set the content type to JSON
        },
        body: JSON.stringify({
          image: dataURL, // Send the base64 string in JSON
        }),
      });

      if (!response.ok) {
        throw new Error("Prediction failed");
      }

      const data = await response.json();
      console.log("Prediction:", data.prediction); // Handle the predicted result as needed
      setPrediction(data.prediction);
      setIsPredicting(false);
    } catch (error) {
      console.error("Error during prediction:", error);
      setIsPredicting(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-6">
      <div
        className="relative w-[80%] aspect-square bg-white rounded-3xl shadow-[0_0_40px_rgba(99,102,241,0.15)] 
                    overflow-hidden border-4 border-indigo-100/50 transition-all duration-300 hover:shadow-[0_0_60px_rgba(99,102,241,0.25)]"
      >
        <canvas
          ref={canvasRef}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
          className="touch-none cursor-crosshair"
        />
      </div>

      <div className="flex gap-4 w-full justify-center">
        <button
          onClick={clearCanvas}
          className="group flex items-center gap-2 px-6 py-3 bg-white text-indigo-600 rounded-xl shadow-sm 
                   hover:bg-indigo-50 active:bg-indigo-100 transition-all duration-200 ease-in-out
                   border-2 border-indigo-100"
        >
          <RefreshCw className="w-5 h-5 transition-transform group-hover:rotate-180 duration-500" />
          <span>Clear</span>
        </button>

        <button
          onClick={handlePredict}
          disabled={isPredicting}
          className={`px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl shadow-sm
                    hover:from-indigo-500 hover:to-purple-500 active:from-indigo-700 active:to-purple-700 
                    transition-all duration-200 ease-in-out font-medium
                    ${isPredicting ? "opacity-75 cursor-not-allowed" : ""}`}
        >
          {isPredicting ? "✨ Predicting..." : "✨ Predict"}
        </button>
      </div>

      {/* Display prediction result */}
      {prediction !== null && (
        <div className="mt-4 text-xl font-semibold text-indigo-600">
          Predicted: {prediction}
        </div>
      )}
    </div>
  );
};
