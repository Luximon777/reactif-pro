import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Observatoire from "@/components/opc/Observatoire";
import UbuntooApp from "@/UbuntooApp";

export default function App() {
    return (
        <div className="App">
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Observatoire />} />
                    <Route path="/ubuntoo" element={<UbuntooApp />} />
                    <Route path="*" element={<Observatoire />} />
                </Routes>
            </BrowserRouter>
        </div>
    );
}
