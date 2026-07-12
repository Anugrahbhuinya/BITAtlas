// src/features/navigation/components/NavigationLocationModal.tsx

import React, { useState } from "react";
import { MapPin, X, Compass } from "lucide-react";
import type { GraphNode } from "../types";
import { useLiveNavigationStore } from "../store/useLiveNavigationStore";
import { navigationApi } from "../services/navigationApi";

const getSquaredDistance = (lat1: number, lng1: number, lat2: number, lng2: number) => {
  return Math.pow(lat1 - lat2, 2) + Math.pow(lng1 - lng2, 2);
};

interface Props {
  isOpen: boolean;
  onClose: () => void;
  allNodes: GraphNode[];
}

export const NavigationLocationModal: React.FC<Props> = ({ isOpen, onClose, allNodes }) => {
  const [search, setSearch] = useState("");
  const [promptMode, setPromptMode] = useState(true);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsError, setGpsError] = useState<string | null>(null);

  const startNode = useLiveNavigationStore((s) => s.startNode);
  const destinationNode = useLiveNavigationStore((s) => s.destinationNode);
  const accessibilityMode = useLiveNavigationStore((s) => s.accessibilityMode);
  
  if (!isOpen) return null;

  const handleUseGPS = () => {
    setGpsLoading(true);
    setGpsError(null);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const { latitude, longitude } = pos.coords;
          useLiveNavigationStore.setState({ currentGPS: [latitude, longitude], routeLoading: true, routeError: null });

          let nearest: GraphNode | null = null;
          let minD = Infinity;
          for (const node of allNodes) {
            const d = getSquaredDistance(latitude, longitude, node.coordinates.latitude, node.coordinates.longitude);
            if (d < minD) {
              minD = d;
              nearest = node;
            }
          }

          if (nearest && destinationNode) {
            useLiveNavigationStore.setState({ startNode: nearest });
            const strategy = accessibilityMode ? "accessible" : "shortest";
            try {
              const routeRes = await navigationApi.calculateRoute(nearest.id, destinationNode.id, strategy as any);
              let pathPoints: [number, number][] = [];
              if (routeRes.geometry && routeRes.geometry.length > 0) {
                pathPoints = routeRes.geometry.map((pt) => [pt[0], pt[1]]);
              } else {
                pathPoints = routeRes.ordered_nodes.map((n) => [
                  n.coordinates.latitude,
                  n.coordinates.longitude,
                ]);
              }
              const firstInstruction = routeRes.navigation_instructions[0] || "Head towards destination.";
              
              useLiveNavigationStore.setState({
                route: routeRes,
                routePathPoints: pathPoints,
                remainingDistance: routeRes.total_distance,
                remainingTime: Math.round(routeRes.estimated_walking_time / 60),
                nextInstruction: firstInstruction,
                routeLoading: false,
                showLocationModal: false,
                isNavigating: true,
              });

              // Start live GPS tracking watch
              const storeState = useLiveNavigationStore.getState();
              storeState.startWatchingPosition();

              // Close modal
              onClose();
            } catch (err) {
              console.error("Routing calculation failed:", err);
              useLiveNavigationStore.setState({
                routeLoading: false,
                routeError: "Failed to calculate navigation route from current location."
              });
              setGpsError("Failed to calculate route from current location.");
              setGpsLoading(false);
            }
          } else {
            useLiveNavigationStore.setState({ routeLoading: false });
            setGpsError("No nearby campus node could be resolved.");
            setGpsLoading(false);
          }
        },
        (err) => {
          console.warn("GPS Permission Denied / Error:", err);
          setGpsLoading(false);
          // Fall back to manually choosing building
          setPromptMode(false);
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    } else {
      setGpsError("Geolocation is not supported by your browser.");
      setGpsLoading(false);
    }
  };

  const handleSelect = async (node: GraphNode) => {
    useLiveNavigationStore.setState({ startNode: node, showLocationModal: false, isNavigating: true, routeLoading: true, routeError: null });
    
    // Calculate initial route from manually selected location
    if (destinationNode) {
      const strategy = accessibilityMode ? "accessible" : "shortest";
      try {
        const routeRes = await navigationApi.calculateRoute(node.id, destinationNode.id, strategy as any);
        let pathPoints: [number, number][] = [];
        if (routeRes.geometry && routeRes.geometry.length > 0) {
          pathPoints = routeRes.geometry.map((pt) => [pt[0], pt[1]]);
        } else {
          pathPoints = routeRes.ordered_nodes.map((n) => [
            n.coordinates.latitude,
            n.coordinates.longitude,
          ]);
        }
        
        const firstInstruction = routeRes.navigation_instructions[0] || "Head towards destination.";
        
        useLiveNavigationStore.setState({
          route: routeRes,
          routePathPoints: pathPoints,
          remainingDistance: routeRes.total_distance,
          remainingTime: Math.round(routeRes.estimated_walking_time / 60),
          nextInstruction: firstInstruction,
          currentGPS: [node.coordinates.latitude, node.coordinates.longitude],
          routeLoading: false,
          showLocationModal: false,
          isNavigating: true,
        });
        
        // Speak initial step
        try {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(`Starting navigation from ${node.name}. ${firstInstruction}`);
          window.speechSynthesis.speak(utterance);
        } catch (e) {}
      } catch (err) {
        console.error("Routing calculation failed:", err);
        useLiveNavigationStore.setState({
          routeLoading: false,
          routeError: "Failed to calculate navigation route from selected start location."
        });
      }
    } else {
      useLiveNavigationStore.setState({ routeLoading: false });
    }
    onClose();
  };

  // Filter starting locations (Buildings, Hostels, Landmarks, Facilities)
  const candidates = allNodes.filter(
    (n) =>
      n.id !== destinationNode?.id &&
      (n.type.toLowerCase() === "building" || n.type.toLowerCase() === "hostel" || n.type.toLowerCase() === "landmark" || n.type.toLowerCase() === "facility") &&
      n.name.toLowerCase().includes(search.toLowerCase())
  ).slice(0, 8);

  if (promptMode) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-[9999] flex items-center justify-center p-4 animate-in fade-in duration-200 select-none">
        <div className="bg-surface border border-outline-variant/60 rounded-3xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col p-6 space-y-6">
          <div className="text-center space-y-2">
            <div className="mx-auto w-12 h-12 bg-primary/10 rounded-2xl text-primary flex items-center justify-center">
              <Compass size={24} className="animate-spin" style={{ animationDuration: '3s' }} />
            </div>
            <h3 className="text-base font-black text-on-surface tracking-tight">Select Starting Location</h3>
            <p className="text-[11px] text-on-surface-variant/70 leading-relaxed font-semibold max-w-xs mx-auto">
              Please specify where you would like to start your route to <strong>{destinationNode?.name}</strong>.
            </p>
          </div>

          {gpsError && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-500 rounded-xl text-[10px] font-bold text-center leading-relaxed">
              {gpsError}
            </div>
          )}

          <div className="flex flex-col gap-3">
            <button
              onClick={handleUseGPS}
              disabled={gpsLoading}
              className="w-full p-4 bg-primary hover:bg-primary/95 text-background font-bold text-xs uppercase tracking-wider rounded-2xl shadow-md transition duration-150 active:scale-[0.98] cursor-pointer flex items-center justify-center gap-2 border border-primary disabled:opacity-50"
            >
              {gpsLoading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-background border-t-transparent rounded-full animate-spin"></span>
                  <span>Acquiring GPS Signal...</span>
                </>
              ) : (
                <>
                  <Compass size={14} className="fill-current" />
                  <span>Use Current Location</span>
                </>
              )}
            </button>

            <button
              onClick={() => setPromptMode(false)}
              disabled={gpsLoading}
              className="w-full p-4 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/60 text-on-surface font-bold text-xs uppercase tracking-wider rounded-2xl shadow-sm transition duration-150 active:scale-[0.98] cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <MapPin size={14} className="text-primary" />
              <span>Select Starting Building</span>
            </button>
          </div>

          <div className="flex justify-center pt-2">
            <button
              onClick={onClose}
              className="text-[10px] text-on-surface-variant/60 hover:text-on-surface uppercase tracking-wider font-extrabold transition"
            >
              Cancel Navigation
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-[9999] flex items-center justify-center p-4 animate-in fade-in duration-200 select-none">
      <div className="bg-surface border border-outline-variant/60 rounded-3xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-outline-variant/30 flex justify-between items-center bg-surface-container-low">
          <div className="flex items-center gap-2 text-primary">
            <MapPin size={18} className="animate-bounce" />
            <h3 className="font-extrabold text-sm tracking-tight uppercase">Select Start Location</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-full hover:bg-surface-variant text-on-surface/40 hover:text-on-surface transition"
          >
            <X size={16} />
          </button>
        </div>

        {/* Input */}
        <div className="p-4">
          <input
            type="text"
            placeholder="Search starting building, hostel or landmark..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full p-2.5 bg-surface-variant/40 hover:bg-surface-variant/75 border border-outline-variant/50 focus:border-primary focus:outline-none rounded-xl text-xs transition font-semibold"
          />
        </div>

        {/* Selection Area */}
        <div className="flex-1 max-h-60 overflow-y-auto px-4 pb-4 space-y-1.5 custom-scrollbar">
          {candidates.map((node) => (
            <button
              key={node.id}
              onClick={() => handleSelect(node)}
              className="w-full text-left p-3 hover:bg-primary/10 border border-outline-variant/20 rounded-xl transition flex items-center justify-between group cursor-pointer"
            >
              <div className="flex flex-col text-left">
                <span className="text-xs font-bold text-on-surface group-hover:text-primary transition-colors">
                  {node.name}
                </span>
                <span className="text-[9px] text-on-surface-variant/50 font-bold uppercase tracking-wider mt-0.5">
                  Category: {node.type}
                </span>
              </div>
              <MapPin size={14} className="text-on-surface/20 group-hover:text-primary transition-colors" />
            </button>
          ))}
          {candidates.length === 0 && (
            <div className="text-center py-6 text-xs text-on-surface/40 font-semibold">
              No matching locations found
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NavigationLocationModal;
