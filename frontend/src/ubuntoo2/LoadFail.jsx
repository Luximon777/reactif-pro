import React from "react";
import { Button } from "@/components/ui/button";
import { RefreshCw, CloudOff } from "lucide-react";

export const LoadFail = ({ onRetry }) => (
  <div className="flex flex-col items-center justify-center py-14 gap-3 text-center" data-testid="load-fail">
    <CloudOff className="w-8 h-8 text-stone-300" />
    <p className="text-sm text-stone-500">Impossible de charger les données.<br />Vérifiez votre connexion et réessayez.</p>
    <Button variant="outline" className="rounded-xl" onClick={onRetry} data-testid="retry-load-btn">
      <RefreshCw className="w-4 h-4 mr-2" />Réessayer
    </Button>
  </div>
);
