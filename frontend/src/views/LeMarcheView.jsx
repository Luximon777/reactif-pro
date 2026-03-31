import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, Gauge, Layers, Users } from "lucide-react";
import ObservatoireView from "@/views/ObservatoireView";
import EvolutionIndexView from "@/views/EvolutionIndexView";
import ExplorateurView from "@/views/ExplorateurView";

const LeMarcheView = ({ token }) => {
  const [activeTab, setActiveTab] = useState("observatoire");

  return (
    <div className="space-y-6 animate-fade-in" data-testid="le-marche-view">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Le Marché
        </h1>
        <p className="text-slate-500 mt-1 text-sm">Veille sectorielle, tendances et évolution des compétences</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full grid grid-cols-3 h-11 bg-slate-100 rounded-xl p-1" data-testid="marche-tabs">
          <TabsTrigger value="observatoire" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="marche-tab-observatoire">
            <BarChart3 className="w-4 h-4 mr-1.5 hidden sm:inline" />Observatoire
          </TabsTrigger>
          <TabsTrigger value="evolution" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="marche-tab-evolution">
            <Gauge className="w-4 h-4 mr-1.5 hidden sm:inline" />Évolution
          </TabsTrigger>
          <TabsTrigger value="explorateur" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="marche-tab-explorateur">
            <Layers className="w-4 h-4 mr-1.5 hidden sm:inline" />Explorateur
          </TabsTrigger>
        </TabsList>

        <TabsContent value="observatoire" className="mt-6">
          <ObservatoireView token={token} embedded />
        </TabsContent>
        <TabsContent value="evolution" className="mt-6">
          <EvolutionIndexView token={token} embedded />
        </TabsContent>
        <TabsContent value="explorateur" className="mt-6">
          <ExplorateurView token={token} embedded />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default LeMarcheView;
