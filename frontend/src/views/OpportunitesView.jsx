import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Briefcase, BookOpen } from "lucide-react";
import ParticulierView from "@/views/ParticulierView";

const OpportunitesView = ({ token }) => {
  const [activeTab, setActiveTab] = useState("matching");

  return (
    <div className="space-y-6 animate-fade-in" data-testid="opportunites-view">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Opportunités
        </h1>
        <p className="text-slate-500 mt-1 text-sm">Offres d'emploi compatibles et formations recommandées</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full grid grid-cols-2 h-11 bg-slate-100 rounded-xl p-1" data-testid="opportunites-tabs">
          <TabsTrigger value="matching" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="opportunites-tab-matching">
            <Briefcase className="w-4 h-4 mr-1.5 hidden sm:inline" />Matching
          </TabsTrigger>
          <TabsTrigger value="formations" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="opportunites-tab-formations">
            <BookOpen className="w-4 h-4 mr-1.5 hidden sm:inline" />Formations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="matching" className="mt-6">
          <ParticulierView token={token} section="jobs" />
        </TabsContent>
        <TabsContent value="formations" className="mt-6">
          <ParticulierView token={token} section="learning" />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OpportunitesView;
