import { Link } from "react-router-dom";
import { Logo } from "../assets";

const Navbar = () => {
  return (
    <div className="w-full bg-[#0F1B2C] py-2 text-white flex items-center">
      <div className="w-[96%] md:w-[94%] mx-auto flex items-center justify-between">
        <Link to="/">
          <img src={Logo} alt="logo" className="w-36 md:w-44" />
        </Link>
        <div className="hidden md:flex items-center gap-x-6">
          <Link>Home</Link>
          <Link>About</Link>
          <Link to="/upload">Upload</Link>
        </div>
        <div className="hidden md:block">
          <button className="border-2 border-[#00ADF1] px-4 py-1 rounded-lg">
            Login
          </button>
        </div>
        <div className="block md:hidden">
          <h1>icon</h1>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
