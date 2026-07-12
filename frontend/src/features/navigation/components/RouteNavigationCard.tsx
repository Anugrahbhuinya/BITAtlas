import React from "react";
import { Compass, Navigation } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLiveNavigationStore } from "../store/useLiveNavigationStore";
import type { GraphNode } from "../types";

interface Props {
  navigationContext: any;
  allNodes: GraphNode[];
}

export const RouteNavigationCard: React.FC<Props> = ({
  navigationContext: nav,
  allNodes,
}) => {
  const navigate = useNavigate();

  const handleStartNavigation = async () => {
    console.log("========== NAVIGATION DEBUG ==========");
    console.log("Navigate button clicked (RouteNavigationCard)");
    console.log("Generating route...");
    let destNode = allNodes.find(
      (n) => n.name.toLowerCase() === nav.destination.toLowerCase()
    );
    if (!destNode) {
      destNode = allNodes.find((n) =>
        n.name.toLowerCase().includes(nav.destination.toLowerCase())
      );
    }
    if (destNode) {
      console.log("Route generated: TRUE (Resolved Destination:", destNode.name, ")");
      console.log("Creating navigation session...");
      useLiveNavigationStore.setState({
        accessibilityMode: nav.accessibility_mode || false,
      });
      await useLiveNavigationStore
        .getState()
        .startNavigation(destNode, allNodes, nav.source);
      console.log("Navigation session created: TRUE");
      console.log("React Router navigating to /navigation...");
      console.log("======================================");
      navigate("/navigation");
    } else {
      console.error("Route generated: FALSE (Could not resolve destination node in graph)");
      console.log("======================================");
      alert("Destination node could not be resolved in campus graph.");
    }
  };

  return (
    <div className="bg-surface-container-high border border-outline-variant/60 rounded-2xl p-5 shadow-md max-w-sm w-full my-3 space-y-4 animate-in fade-in duration-200">
      <div className="flex items-start gap-3">
        <div className="p-2.5 bg-primary/10 rounded-xl text-primary shrink-0">
          <Compass size={18} />
        </div>
        <div>
          <h4 className="text-sm font-black text-on-surface tracking-tight">
            Route to {nav.destination}
          </h4>
          <p className="text-[10px] text-on-surface-variant/65 font-bold uppercase tracking-wider mt-0.5">
            Grounded Route Guidance
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 bg-surface-variant/20 p-2.5 rounded-xl border border-outline-variant/30 text-center select-none">
        <div>
          <span className="text-[8px] block text-on-surface/40 uppercase font-black">
            From
          </span>
          <span className="text-[10px] font-bold text-on-surface mt-0.5 block truncate">
            {nav.source}
          </span>
        </div>
        <div>
          <span className="text-[8px] block text-on-surface/40 uppercase font-black">
            Distance
          </span>
          <span className="text-[10px] font-bold text-on-surface mt-0.5 block">
            {nav.walking_distance} m
          </span>
        </div>
        <div>
          <span className="text-[8px] block text-on-surface/40 uppercase font-black">
            Walk Time
          </span>
          <span className="text-[10px] font-bold text-on-surface mt-0.5 block">
            {nav.estimated_time} min
          </span>
        </div>
      </div>

      {nav.directions && nav.directions.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-[9px] font-extrabold uppercase text-on-surface/45 tracking-wider">
            Directions Summary
          </p>
          <div className="space-y-1.5">
            {nav.directions.slice(0, 3).map((step: string, idx: number) => (
              <div
                key={idx}
                className="flex gap-2 items-start text-[11px] text-on-surface/80 leading-normal font-semibold"
              >
                <span className="w-3.5 h-3.5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[8px] font-bold mt-0.5 shrink-0">
                  {idx + 1}
                </span>
                <span>{step.replace(/^- /, "")}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {nav.landmarks && nav.landmarks.length > 0 && (
        <div className="space-y-1">
          <p className="text-[9px] font-extrabold uppercase text-on-surface/45 tracking-wider">
            Key Landmarks
          </p>
          <div className="flex flex-wrap gap-1.5">
            {nav.landmarks.map((l: string) => (
              <span
                key={l}
                className="px-2 py-0.5 bg-surface-variant/30 text-on-surface/70 text-[9px] font-bold rounded-lg border border-outline-variant/20"
              >
                {l}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="border-t border-outline-variant/30 pt-3">
        <button
          onClick={handleStartNavigation}
          className="w-full py-2.5 bg-primary hover:bg-primary/95 text-background text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 flex items-center justify-center gap-1.5 active:scale-[0.98] cursor-pointer shadow-sm"
        >
          <Navigation size={13} className="fill-current" />
          <span>Start Navigation</span>
        </button>
      </div>
    </div>
  );
};

export default RouteNavigationCard;
