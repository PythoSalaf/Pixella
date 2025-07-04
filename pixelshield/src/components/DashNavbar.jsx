import { Link, NavLink } from "react-router-dom";
import { Logo, Profile } from "../assets";

const DashNavbar = () => {
  return (
    <div className="w-full bg-[#0F1B2C] py-2 text-white flex items-center">
      <div className="w-[96%] md:w-[94%] mx-auto flex items-center justify-between">
        <Link to="/">
          <img src={Logo} alt="logo" className="w-36 md:w-44" />
        </Link>
        <div className="hidden md:flex items-center gap-x-6 bg-[#14243B] px-5 py-2 rounded-2xl">
          <NavLink className="text-base font-semibold">Upload</NavLink>
          <NavLink className="text-base font-semibold">Verification</NavLink>
          <NavLink className="text-base font-semibold">Integration</NavLink>
        </div>
        <div className="hidden md:flex items-center gap-x-3">
          <img src={Profile} alt="profile-icon" className="w-[45px] " />
        </div>
        <div className="block md:hidden">
          <h1>icon</h1>
        </div>
      </div>
    </div>
  );
};

export default DashNavbar;
