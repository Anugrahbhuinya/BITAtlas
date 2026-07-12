import React from "react";
import { MapPinned, Navigation } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLiveNavigationStore } from "../store/useLiveNavigationStore";
import type { GraphNode } from "../types";

interface Props {
  navigationContext: any;
  allNodes: GraphNode[];
}

export const PlaceInformationCard: React.FC<Props> = ({
  navigationContext: nav,
  allNodes,
}) => {
  const navigate = useNavigate();

  const handleNavigate = async () => {
    console.log("========== NAVIGATION DEBUG ==========");
    console.log("Navigate button clicked (PlaceInformationCard)");
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
        .startNavigation(destNode, allNodes, null);
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
          <MapPinned size={18} />
        </div>
        <div>
          <h4 className="text-sm font-black text-on-surface tracking-tight">
            {nav.destination}
          </h4>
          <p className="text-[10px] text-on-surface-variant/65 font-bold uppercase tracking-wider mt-0.5">
            {nav.building_metadata?.category || "Campus Location"}
          </p>
        </div>
      </div>

      {nav.building_metadata?.description && (
        <p className="text-[11px] text-on-surface/85 leading-relaxed font-semibold">
          {nav.building_metadata.description}
        </p>
      )}

      {nav.building_metadata?.address && (
        <p className="text-[10px] text-on-surface-variant/70 leading-relaxed italic">
          {nav.building_metadata.address}
        </p>
      )}

      {nav.landmarks && nav.landmarks.length > 0 && (
        <div className="space-y-1">
          <p className="text-[9px] font-extrabold uppercase text-on-surface/45 tracking-wider">
            Nearby Landmarks
          </p>
          <ul className="list-disc list-inside text-[11px] text-on-surface/75 space-y-0.5 font-medium">
            {nav.landmarks.map((l: string) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </div>
      )}

      {nav.nearby_facilities && nav.nearby_facilities.length > 0 && (
        <div className="space-y-1">
          <p className="text-[9px] font-extrabold uppercase text-on-surface/45 tracking-wider">
            Nearby Facilities
          </p>
          <ul className="list-disc list-inside text-[11px] text-on-surface/75 space-y-0.5 font-medium">
            {nav.nearby_facilities.map((f: string) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="border-t border-outline-variant/30 pt-3">
        <button
          onClick={handleNavigate}
          className="w-full py-2.5 bg-primary hover:bg-primary/95 text-background text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 flex items-center justify-center gap-1.5 active:scale-[0.98] cursor-pointer shadow-sm"
        >
          <Navigation size={13} className="fill-current" />
          <span>Navigate</span>
        </button>
      </div>
    </div>
  );
};

export default PlaceInformationCard;
