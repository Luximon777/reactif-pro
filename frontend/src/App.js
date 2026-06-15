import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import LandingPage from "@/LandingPage";
import Observatoire from "@/components/opc/Observatoire";
import UbuntooApp from "@/UbuntooApp";

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
      <Toaster />
    </div>
  );
}
