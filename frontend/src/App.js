import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { ReactifLanding } from "@/ReactifLanding";
import { ReactifHome, ParticuliersPage, ServicesRHPage } from "@/ReactifPro";
import Observatoire from "@/components/opc/Observatoire";
import UbuntooApp from "@/UbuntooApp";

export default function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ReactifLanding />} />
          <Route path="/reactif/landing" element={<ReactifLanding />} />
          <Route path="/reactif/accueil" element={<ReactifHome />} />
          <Route path="/reactif/particuliers" element={<ParticuliersPage />} />
          <Route path="/reactif/services-rh" element={<ServicesRHPage />} />
          <Route path="/observatoire" element={<Observatoire />} />
          <Route path="/ubuntoo" element={<UbuntooApp />} />
          <Route path="*" element={<ReactifLanding />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}
