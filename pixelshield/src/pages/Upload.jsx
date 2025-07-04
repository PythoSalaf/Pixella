import { useState } from "react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

const Upload = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploaded, setIsUploaded] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationProgress, setVerificationProgress] = useState(0);
  const [isVerified, setIsVerified] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null); // 'authentic' | 'ai' | 'edited'

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(URL.createObjectURL(file));
      setIsUploaded(false);
      setUploadProgress(0);
      setIsVerifying(false);
      setIsVerified(false);
      setShowResult(false);
      setVerificationResult(null);

      // Simulate upload
      let progress = 0;
      const interval = setInterval(() => {
        progress += 10;
        setUploadProgress(progress);
        if (progress >= 100) {
          clearInterval(interval);
          setIsUploaded(true);
        }
      }, 200);
    }
  };

  const handleVerify = () => {
    setIsVerifying(true);
    setVerificationProgress(0);
    setIsVerified(false);
    setShowResult(false);

    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setVerificationProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setIsVerifying(false);
        setIsVerified(true);
      }
    }, 300);
  };

  const handleViewResults = () => {
    // Randomly choose a result for demo (you can replace with real logic)
    const results = ["authentic", "ai", "edited"];
    const random = results[Math.floor(Math.random() * results.length)];
    setVerificationResult(random);
    setShowResult(true);
  };

  const renderResultCard = () => {
    if (!verificationResult || !selectedImage) return null;

    let resultProps = {
      color: "",
      title: "",
      message: "",
      action: "",
    };

    if (verificationResult === "authentic") {
      resultProps = {
        color: "green",
        title: "✅ Authentic image",
        message: "No edits or modifications detected.",
        action: "Download Certificate",
      };
    } else if (verificationResult === "ai") {
      resultProps = {
        color: "red",
        title: "❌ AI-Generated",
        message: "Potential AI-Generated or Deepfake Image",
        action: "Report Suspicious Image",
      };
    } else if (verificationResult === "edited") {
      resultProps = {
        color: "orange",
        title: "⚠️ Edited Image",
        message: "Changes detected in this image",
        action: "View Edit History",
      };
    }

    return (
      <div className="w-full mx-auto text-white flex flex-col items-center">
        <h3 className="text-lg font-semibold mb-2">Verification Result</h3>
        <div className="bg-[#1c2c45] p-4 rounded-xl shadow-md w-[55%] mx-auto">
          <img
            src={selectedImage}
            alt="verified"
            className="w-full rounded-md mb-3"
          />
          <div
            className={`flex items-center justify-between px-3 py-2 rounded-md mb-2 ${
              verificationResult === "authentic"
                ? "bg-green-600"
                : verificationResult === "ai"
                ? "bg-red-600"
                : "bg-yellow-600"
            }`}
          >
            <p className="text-sm font-bold">{resultProps.title}</p>
            <p className="text-sm">{resultProps.message}</p>
          </div>
          <div className="flex items-center justify-center gap-4 mt-3">
            <button className="px-4 py-1 bg-[#2BBBF3] rounded hover:bg-[#199ed4] text-sm">
              {resultProps.action}
            </button>
            <button className="px-4 py-1 bg-[#243b56] rounded hover:bg-[#2c4b6d] text-sm">
              Learn More
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full text-white bg-[#0F1B2C] flex items-start justify-between h-screen">
      {/* Left Side */}
      <div className="w-full md:w-[35%] lg:w-[32%]">
        <div className="mt-7">
          <h2 className="text-center text-xl md:text-2xl">Upload images</h2>
        </div>

        <div className="mt-24 flex flex-col items-center justify-center w-[60%] mx-auto bg-[#14243B] shadow rounded-2xl py-20">
          <h4 className="text-center">
            Drag & drop your image <br /> or{" "}
          </h4>
          <input
            type="file"
            accept="image/png, image/jpeg, image/jpg, image/webp"
            onChange={handleFileChange}
            className="w-[60%] mx-auto text-sm font-semibold text-[#2BBBF3] cursor-pointer"
          />
          <p className="text-sm font-semibold py-2">
            Supports: PNG, JPG, JPEG, WEBP
          </p>
        </div>

        {selectedImage && (
          <div className="mt-4 rounded-2xl flex items-center justify-center w-[60%] mx-auto bg-[#14243B] py-2">
            <div className="w-[90%] mx-auto flex items-center justify-between gap-x-2">
              <img
                src={selectedImage}
                alt="preview"
                className="w-10 h-10 rounded-lg object-cover"
              />
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div
                  className="bg-[#4DB151] h-3 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p
                className={`text-sm md:text-base font-semibold ${
                  isUploaded ? "text-[#4DB151]" : "text-[#F6A15E]"
                }`}
              >
                {isUploaded ? "Uploaded" : "Uploading"}
              </p>
            </div>
          </div>
        )}

        {isUploaded && !isVerifying && !isVerified && (
          <div className="flex items-center justify-center mt-4 w-[60%] mx-auto">
            <button
              onClick={handleVerify}
              className="w-full py-1.5 rounded-md cursor-pointer text-white font-medium bg-[#2BBBF3] hover:bg-[#1a9ccf]"
            >
              Verify Image
            </button>
          </div>
        )}
      </div>

      {/* Right Side */}
      <div className="w-full md:w-[65%] lg:w-[68%] bg-[#14243B] h-screen flex items-center justify-center">
        {!isVerifying && !isVerified && !showResult && (
          <h3 className="font-semibold text-xl md:text-2xl text-center px-4">
            <span className="text-[#2BBBF3]">Upload your image</span> to start
            verification
          </h3>
        )}

        {isVerifying && (
          <div className="relative w-[150px] h-[150px] md:w-[300px] md:h-[300px] flex flex-col items-center">
            <CircularProgressbar
              value={verificationProgress}
              styles={buildStyles({
                pathColor: "#2BBBF3",
                trailColor: "#1e3a5f",
              })}
            />
            <div className="absolute inset-0 flex flex-col items-center justify-center text-[#2BBBF3] text-sm">
              <p>Generating ZK Proof</p>
              <p className="text-xl font-bold">{verificationProgress}%</p>
            </div>
            <p className="mt-4 text-sm text-white">
              This would take approximately{" "}
              <span className="text-[#2BBBF3]">20 minutes</span>
            </p>
          </div>
        )}

        {isVerified && !showResult && (
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-[150px] h-[150px] md:w-[300px] md:h-[300px]">
              <CircularProgressbar
                value={100}
                styles={buildStyles({
                  pathColor: "#2BBBF3",
                  trailColor: "#1e3a5f",
                })}
              />
              <div className="absolute inset-0 flex flex-col items-center justify-center text-[#2BBBF3] text-sm">
                <p>Generating ZK Proof</p>
                <p className="text-xl font-bold">100%</p>
              </div>
            </div>
            <p className="text-sm text-white">Image Verification complete</p>
            <button
              onClick={handleViewResults}
              className="px-6 py-2 rounded-md bg-[#2BBBF3] text-white font-medium hover:bg-[#1a9ccf]"
            >
              View results
            </button>
          </div>
        )}
        {/* Render Result Card */}
        <div className="w-[90%]">{showResult && renderResultCard()}</div>
      </div>
    </div>
  );
};

export default Upload;
