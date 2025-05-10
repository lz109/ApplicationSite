import { Routes, Route } from "react-router-dom";
import './index.css';
import Home from "./pages/Home";
import OfficerDashboard from "./pages/officerDashboard";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/officer_dashboard/*" element={<OfficerDashboard />} />
    </Routes>
  );
}

export default App;
