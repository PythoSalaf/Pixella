import { Hero } from "../assets";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();
  return (
    <div className="w-full relative h-screen text-white bg-[#14243B]  flex items-start justify-center">
      <div className="absolute inset-0  flex items-start justify-start  ">
        <div className="w-[350px] h-[350px] bg-[#2BBBF3] blur-[350px] opacity-40"></div>
      </div>
      <div className="relative  gap-y-9 w-[95%] mt-8 md:mt-14 md:w-[92%] mx-auto flex items-center justify-between flex-col md:flex-row">
        <div className="text-white w-full">
          <h2 className="text-3xl md:text-4xl lg:text-5xl  font-semibold text-white leading-12 md:leading-16">
            Verify <span className="text-[#6BBE6E]">Image Authenticity</span>{" "}
            <br /> with ZK Proofs
          </h2>

          <p className="py-2 md:py-6 text-base md:text-lg lg:text-xl">
            Ensure trust in digital media by proving the authenticity and edit
            history of images. Our ZK-powered verification stack helps
            developers and users detect AI-generated or manipulated content with
            ease.
          </p>
          <div className="mt-4 md:mt-8 flex items-center gap-x-8">
            <button
              className="bg-[#2BBBF3] text-white rounded-md px-6 hover:bg-[#0e235d] cursor-pointer flex items-center gap-x-1.5 py-2 text-sm md:text-base font-semibold"
              onClick={() => navigate("/upload")}
            >
              Get started for free
            </button>
          </div>
        </div>
        <div className="w-full ">
          <img
            src={Hero}
            alt="hero"
            className="w-[96%] md:w-[85%] lg:w-[80%] mx-auto animate-scale"
          />
        </div>
      </div>
    </div>
  );
};

export default Home;
