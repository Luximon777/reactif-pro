import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import LandingPage from "@/LandingPage";
import Observatoire from "@/components/opc/Observatoire";
import UbuntooApp from "@/UbuntooApp";
import EspacePersonnel from "@/EspacePersonnel";
import { ReactifHome, ParticuliersPage, ServicesRHPage, PartenairesPage } from "@/ReactifPro";
import { ReactifLanding } from "@/ReactifLanding";

export default function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/observatoire" element={<Observatoire />} />
          <Route path="/ubuntoo" element={<UbuntooApp />} />
          <Route path="/espace-personnel" element={<EspacePersonnel />} />
          <Route path="/reactif" element={<ReactifLanding />} />
          <Route path="/reactif/accueil" element={<ReactifHome />} />
          <Route path="/reactif/particuliers" element={<ParticuliersPage />} />
          <Route path="/reactif/services-rh" element={<ServicesRHPage />} />
          <Route path="/reactif/partenaires" element={<PartenairesPage />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}
