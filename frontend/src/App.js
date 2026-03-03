import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { QuestionnairePage } from "./pages/QuestionnairePage";
import { CarteIdentitePage } from "./pages/CarteIdentitePage";

function App() {
  return (
    <div className="App min-h-screen">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/questionnaire" element={<QuestionnairePage />} />
          <Route path="/carte-identite" element={<CarteIdentitePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
