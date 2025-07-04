import { Routes, Route } from "react-router-dom";
import { Home, LandingLayout, Upload, DashLayout } from "./pages";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingLayout />}>
          <Route index element={<Home />} />
        </Route>
        <Route path="/upload" element={<DashLayout />}>
          <Route index element={<Upload />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
