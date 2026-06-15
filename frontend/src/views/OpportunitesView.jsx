import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Target, Briefcase, BookOpen } from "lucide-react";
import ParticulierView from "@/views/ParticulierView";
import JobMatchingView from "@/views/JobMatchingView";

const OpportunitesView = ({ token }) => {
  const [activeTab, setActiveTab] = useState("matching-ia");

  return (
    <div className="space-y-6 animate-fade-in" data-testid="opportunites-view">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Opportunités
        </h1>
        <p className="text-slate-500 mt-1 text-sm">Analysez les offres, mesurez votre compatibilité et optimisez vos candidatures</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full grid grid-cols-3 h-11 bg-slate-100 rounded-xl p-1" data-testid="opportunites-tabs">
          <TabsTrigger value="matching-ia" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="opportunites-tab-matching-ia">
            <Target className="w-4 h-4 mr-1.5 hidden sm:inline" />Matching IA
          </TabsTrigger>
          <TabsTrigger value="offres" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="opportunites-tab-offres">
            <Briefcase className="w-4 h-4 mr-1.5 hidden sm:inline" />Offres
          </TabsTrigger>
          <TabsTrigger value="formations" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="opportunites-tab-formations">
            <BookOpen className="w-4 h-4 mr-1.5 hidden sm:inline" />Formations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="matching-ia" className="mt-6">
          <JobMatchingView token={token} />
        </TabsContent>
        <TabsContent value="offres" className="mt-6">
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
