import { Canvas } from "@/components/Canvas";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-blue-50 to-purple-50 flex items-center">
      <div className="container mx-auto px-10 flex items-center gap-10">
        <div className="w-1/2">
          <h1
            className="text-8xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-pink-500 text-transparent bg-clip-text 
                       tracking-tight leading-tight pb-2"
          >
            Letter
            <br />
            Recognition
          </h1>
          <p className="text-2xl text-gray-600 mt-2">
            Draw a letter and let AI predict what it is
          </p>
        </div>

        <div className="w-1/2 relative">
          <div className="mx-auto relative flex flex-col items-center">
            <span
              className="absolute -top-8 text-sm font-medium text-indigo-600 bg-white/70 backdrop-blur-sm 
                           px-4 py-1.5 rounded-full shadow-sm inline-block animate-bounce z-10"
            >
              ✨ Draw Here ✨
            </span>
            <Canvas />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
