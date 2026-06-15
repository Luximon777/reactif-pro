import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Observatoire from "@/components/opc/Observatoire";
import UbuntooApp from "@/UbuntooApp";
import LandingPage from "@/LandingPage";

export default function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/observatoire" element={<Observatoire />} />
          <Route path="/ubuntoo" element={<UbuntooApp />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}
