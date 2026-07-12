// src/features/navigation/pages/NavigationPage.tsx

import React, { useEffect, useState, useRef, useCallback } from "react";
import { MapContainer, TileLayer, Marker, Polyline, useMap, Popup, Polygon } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { 
  Volume2, VolumeX, Navigation, Compass, MapPin, 
  X, Award, Sparkles,
  ZoomIn, ZoomOut, Target, RefreshCw, AlertCircle, Play, ArrowLeft
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLiveNavigationStore } from "../store/useLiveNavigationStore";
import { NavigationLocationModal } from "../components/NavigationLocationModal";
import { navigationApi } from "../services/navigationApi";

class MapErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error("Map rendering error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-full w-full flex flex-col items-center justify-center bg-surface-container-low p-6 text-center select-none">
          <div className="w-12 h-12 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mb-4">
            <AlertCircle size={24} />
          </div>
          <h3 className="text-sm font-black text-on-surface tracking-tight">Map Initialization Failed</h3>
          <p className="text-[11px] text-on-surface-variant/70 max-w-xs mt-1.5 leading-relaxed font-semibold">
            An error occurred while loading the map layers.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-primary hover:bg-primary/95 text-background text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 active:scale-[0.98] cursor-pointer"
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Blue User Geolocation GPS Marker icon with pulsing ring
const createUserIcon = () => L.divIcon({
  html: `
    <div class="flex flex-col items-center">
      <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center border-2 border-white shadow-xl ring-4 ring-blue-500/30 animate-pulse">
        <div class="w-3 h-3 rounded-full bg-white"></div>
      </div>
    </div>
  `,
  className: "custom-leaflet-icon",
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

// Green Start marker icon
const createStartIcon = (label: string) => L.divIcon({
  html: `
    <div class="flex flex-col items-center">
      <div class="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center border-2 border-white shadow-xl ring-4 ring-emerald-500/20">
        <span class="text-white text-xs font-bold">A</span>
      </div>
      <span class="text-[9px] font-extrabold px-1.5 py-0.5 mt-1 rounded bg-emerald-500 text-white shadow-sm whitespace-nowrap max-w-[120px] truncate">${label}</span>
    </div>
  `,
  className: "custom-leaflet-icon",
  iconSize: [60, 50],
  iconAnchor: [30, 25]
});

// Red Destination marker icon
const createDestinationIcon = (label: string) => L.divIcon({
  html: `
    <div class="flex flex-col items-center">
      <div class="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center border-2 border-white shadow-xl ring-4 ring-red-500/20">
        <span class="text-white text-xs">📍</span>
      </div>
      <span class="text-[9px] font-extrabold px-1.5 py-0.5 mt-1 rounded bg-red-500 text-white shadow-sm whitespace-nowrap max-w-[120px] truncate">${label}</span>
    </div>
  `,
  className: "custom-leaflet-icon",
  iconSize: [60, 50],
  iconAnchor: [30, 25]
});

// Map camera controller with auto-follow
function MapCameraController({
  currentGPS,
  routePathPoints,
  fitRouteTrigger,
  autoFollow,
  navigationStarted
}: {
  currentGPS: [number, number] | null;
  routePathPoints: [number, number][];
  fitRouteTrigger: number;
  autoFollow: boolean;
  navigationStarted: boolean;
}) {
  const map = useMap();
  const hasInitialFit = useRef(false);

  // Fit route bounds on initial load
  useEffect(() => {
    if (routePathPoints.length > 0 && !hasInitialFit.current) {
      const bounds = L.latLngBounds(routePathPoints);
      map.fitBounds(bounds, { padding: [60, 60], animate: true, duration: 1.2 });
      hasInitialFit.current = true;
    }
  }, [routePathPoints, map]);

  // Re-fit route on trigger
  useEffect(() => {
    if (fitRouteTrigger > 0 && routePathPoints.length > 0) {
      const bounds = L.latLngBounds(routePathPoints);
      map.fitBounds(bounds, { padding: [60, 60], animate: true, duration: 1.2 });
    }
  }, [fitRouteTrigger, routePathPoints, map]);

  // Auto-follow user position during active navigation
  useEffect(() => {
    if (autoFollow && currentGPS && navigationStarted) {
      map.setView(currentGPS, Math.max(map.getZoom(), 18), { animate: true, duration: 0.5 });
    }
  }, [currentGPS, autoFollow, navigationStarted, map]);

  return null;
}

export const NavigationPage: React.FC = () => {
  const navigate = useNavigate();

  const {
    isNavigating,
    navigationStarted,
    routeLoading,
    routeError,
    startNode,
    destinationNode,
    currentGPS,
    route,
    routePathPoints,
    nextInstruction,
    remainingDistance,
    remainingTime,
    routeProgress,
    voiceEnabled,
    showLocationModal,
    isOffRoute,
    hasArrived,
    allNodes,
    isSimulating,
    setAllNodes,
    setVoiceEnabled,
    setShowLocationModal,
    stopNavigation,
    beginNavigation,
  } = useLiveNavigationStore();

  const [fitRouteTrigger, setFitRouteTrigger] = useState(0);
  const [mapRef, setMapRef] = useState<L.Map | null>(null);
  const [autoFollow, setAutoFollow] = useState(true);

  const handleStop = () => {
    stopNavigation();
    navigate("/map");
  };

  const handleBack = () => {
    stopNavigation();
    navigate(-1);
  };

  // Load all nodes on mount for fallback modal matching
  useEffect(() => {
    const loadNodes = async () => {
      try {
        const nodes = await navigationApi.fetchGraphNodes();
        setAllNodes(nodes);
      } catch (err) {
        console.error("Failed to load graph nodes in NavigationPage:", err);
      }
    };
    loadNodes();
  }, [setAllNodes]);

  // Restart watching position on mount if session is active
  useEffect(() => {
    if (isNavigating && navigationStarted) {
      // If GPS is being watched, resume it
      const state = useLiveNavigationStore.getState();
      if (!state.isSimulating && state.watchId === null) {
        state.startWatchingPosition();
      }
    }
  }, [isNavigating, navigationStarted]);

  // Map zoom handles
  const handleZoomIn = () => mapRef?.zoomIn();
  const handleZoomOut = () => mapRef?.zoomOut();

  const handleLocateMe = () => {
    if (currentGPS) {
      mapRef?.setView(currentGPS, 18, { animate: true });
      setAutoFollow(true);
    }
  };

  const handleFitRoute = () => {
    setFitRouteTrigger((prev) => prev + 1);
    setAutoFollow(false);
  };

  const getEstimatedArrival = (mins: number) => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + mins);
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  // Compute the completed and remaining polyline segments
  const getRouteSegments = useCallback(() => {
    if (!currentGPS || routePathPoints.length < 2) {
      return { completed: [] as [number, number][], remaining: routePathPoints };
    }

    // Find the closest point on the polyline
    let closestIdx = 0;
    let closestDist = Infinity;
    for (let i = 0; i < routePathPoints.length; i++) {
      const dx = currentGPS[0] - routePathPoints[i][0];
      const dy = currentGPS[1] - routePathPoints[i][1];
      const d = dx * dx + dy * dy;
      if (d < closestDist) {
        closestDist = d;
        closestIdx = i;
      }
    }

    const completed = routePathPoints.slice(0, closestIdx + 1);
    const remaining = [routePathPoints[closestIdx], ...routePathPoints.slice(closestIdx + 1)];
    return { completed, remaining };
  }, [currentGPS, routePathPoints]);

  // If required navigation data is missing, show an error screen
  if (!isNavigating || !destinationNode) {
    return (
      <div className="h-[calc(100vh-4rem)] w-full flex flex-col items-center justify-center bg-background p-6 text-center select-none">
        <div className="flex flex-col items-center gap-4 animate-in fade-in duration-300">
          <div className="p-4 bg-amber-500/10 rounded-2xl text-amber-500">
            <AlertCircle size={32} />
          </div>
          <div className="space-y-1.5">
            <h3 className="text-sm font-black text-on-surface tracking-tight">Navigation Session Data Missing</h3>
            <p className="text-[11px] text-on-surface-variant/70 max-w-xs mt-1.5 leading-relaxed font-semibold">
              The active navigation session is missing. Please start navigation again from the map or chat.
            </p>
          </div>
          <button
            onClick={() => navigate("/map")}
            className="mt-4 px-5 py-2.5 bg-primary hover:bg-primary/95 text-background text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 active:scale-[0.98] cursor-pointer"
          >
            Go to Map
          </button>
        </div>
      </div>
    );
  }

  if (routeLoading) {
    return (
      <div className="h-[calc(100vh-4rem)] w-full flex flex-col items-center justify-center bg-background p-6 text-center select-none">
        <div className="flex flex-col items-center gap-4 animate-in fade-in duration-300">
          <div className="p-4 bg-primary/10 rounded-2xl text-primary animate-pulse">
            <Navigation size={32} className="animate-bounce" />
          </div>
          <div className="space-y-1.5">
            <h3 className="text-sm font-black text-on-surface tracking-tight">Generating Route...</h3>
            <p className="text-[11px] text-on-surface-variant/70 max-w-xs mt-1.5 leading-relaxed font-semibold">
              Calculating the optimal route to <strong>{destinationNode?.name || "destination"}</strong>.
            </p>
          </div>
          <div className="flex items-center gap-1.5 py-1 px-3 bg-primary/5 text-primary border border-primary/10 rounded-xl text-[10px] font-bold uppercase tracking-wider mt-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping"></span> Checking Graph Pathways
          </div>
        </div>
      </div>
    );
  }

  if (routeError) {
    return (
      <div className="h-[calc(100vh-4rem)] w-full flex flex-col items-center justify-center bg-background p-6 text-center select-none">
        <div className="flex flex-col items-center gap-4 animate-in fade-in duration-300">
          <div className="p-4 bg-red-500/10 rounded-2xl text-red-500">
            <AlertCircle size={32} />
          </div>
          <div className="space-y-1.5">
            <h3 className="text-sm font-black text-on-surface tracking-tight">Route Generation Failed</h3>
            <p className="text-[11px] text-on-surface-variant/70 max-w-xs mt-1.5 leading-relaxed font-semibold">
              {routeError}
            </p>
          </div>
          <button
            onClick={handleStop}
            className="mt-4 px-5 py-2.5 bg-primary hover:bg-primary/95 text-background text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 active:scale-[0.98] cursor-pointer"
          >
            Return to Map
          </button>
        </div>
      </div>
    );
  }

  const { completed, remaining } = getRouteSegments();

  return (
    <div className="h-[calc(100vh-4rem)] flex min-h-0 bg-background text-left relative overflow-hidden">
      
      {/* FULL-WIDTH MAP */}
      <div className="flex-1 h-full relative flex flex-col min-w-0">
        
        {/* LEAFLET INTERACTIVE CAMPUS MAP */}
        <div className="absolute inset-0 z-0 bg-surface-container">
          <MapErrorBoundary>
            <MapContainer
              center={[23.4129, 85.4407]}
              zoom={17}
              zoomControl={false}
              ref={setMapRef}
              className="h-full w-full"
            >
            <TileLayer
              attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Camera Controller */}
            <MapCameraController
              currentGPS={currentGPS}
              routePathPoints={routePathPoints}
              fitRouteTrigger={fitRouteTrigger}
              autoFollow={autoFollow}
              navigationStarted={navigationStarted}
            />

            {/* Start marker */}
            {startNode && (
              <Marker 
                position={[startNode.coordinates.latitude, startNode.coordinates.longitude]} 
                icon={createStartIcon(startNode.name)}
              >
                <Popup>
                  <div className="text-xs font-bold p-1">Start: {startNode.name}</div>
                </Popup>
              </Marker>
            )}

            {/* Blue Current User Location GPS marker */}
            {currentGPS && navigationStarted && (
              <Marker position={currentGPS} icon={createUserIcon()}>
                <Popup>
                  <div className="text-xs font-bold p-1">Your Position</div>
                </Popup>
              </Marker>
            )}

            {/* Red Destination Pin */}
            {destinationNode && (() => {
              const entrance = destinationNode.metadata?.entrance;
              const position: [number, number] = (entrance && entrance[0] && entrance[1])
                ? [entrance[0], entrance[1]]
                : [destinationNode.coordinates.latitude, destinationNode.coordinates.longitude];
              return (
                <Marker
                  position={position}
                  icon={createDestinationIcon(destinationNode.name)}
                >
                  <Popup>
                    <div className="text-xs font-bold p-1">{destinationNode.name}</div>
                  </Popup>
                </Marker>
              );
            })()}

            {/* Building Polygon Outline for destination */}
            {destinationNode && destinationNode.metadata?.geometry && destinationNode.metadata.geometry.length > 1 && (
              <Polygon
                positions={destinationNode.metadata.geometry}
                pathOptions={{
                  color: "#ef4444",
                  fillColor: "#ef4444",
                  fillOpacity: 0.15,
                  weight: 2,
                  dashArray: "3"
                }}
              />
            )}

            {/* Route polyline - split into completed (grey) and remaining (blue) */}
            {navigationStarted && completed.length > 1 && (
              <Polyline
                positions={completed}
                pathOptions={{ color: "#9ca3af", weight: 6, lineCap: "round", opacity: 0.6 }}
              />
            )}
            {navigationStarted && remaining.length > 1 && (
              <>
                <Polyline
                  positions={remaining}
                  pathOptions={{ color: "rgba(59, 130, 246, 0.4)", weight: 10, lineCap: "round" }}
                />
                <Polyline
                  positions={remaining}
                  pathOptions={{ color: "#3b82f6", weight: 5, lineCap: "round", dashArray: "1" }}
                />
              </>
            )}

            {/* Full route polyline when not yet started */}
            {!navigationStarted && routePathPoints.length > 0 && (
              <>
                <Polyline
                  positions={routePathPoints}
                  pathOptions={{ color: "rgba(59, 130, 246, 0.4)", weight: 10, lineCap: "round" }}
                />
                <Polyline
                  positions={routePathPoints}
                  pathOptions={{ color: "#3b82f6", weight: 5, lineCap: "round", dashArray: "1" }}
                />
              </>
            )}
          </MapContainer>
          </MapErrorBoundary>
        </div>

        {/* FLOATING TOP BAR */}
        <div className="absolute top-4 left-4 right-4 z-10 pointer-events-none flex flex-col gap-2 max-w-lg mx-auto select-none">
          <div className="bg-surface/90 backdrop-blur-md border border-outline-variant/60 rounded-2xl p-4 shadow-xl pointer-events-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={handleBack}
                className="p-2 hover:bg-surface-variant/40 rounded-xl text-on-surface/60 hover:text-on-surface transition"
              >
                <ArrowLeft size={18} />
              </button>
              <div className="text-left">
                <p className="text-[10px] text-on-surface-variant/60 font-bold uppercase tracking-wider">
                  {startNode ? `${startNode.name} → ` : ""}Navigating to
                </p>
                <h4 className="text-xs font-black text-on-surface tracking-tight truncate max-w-[200px] md:max-w-[320px]">
                  {destinationNode?.name || "Target Building"}
                </h4>
              </div>
            </div>

            {/* Status indicators */}
            <div className="flex flex-col items-end">
              <span className="text-[9px] font-black uppercase text-on-surface/40 tracking-wider">Status</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                {!navigationStarted ? (
                  <span className="flex items-center gap-1 text-[10px] font-bold text-amber-500 uppercase bg-amber-500/10 px-2 py-0.5 rounded-full">
                    Ready
                  </span>
                ) : isOffRoute ? (
                  <span className="flex items-center gap-1 text-[10px] font-bold text-amber-500 uppercase bg-amber-500/10 px-2 py-0.5 rounded-full">
                    <RefreshCw size={10} className="animate-spin" /> Recalculating
                  </span>
                ) : isSimulating ? (
                  <span className="flex items-center gap-1 text-[10px] font-bold text-blue-500 uppercase bg-blue-500/10 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping"></span> Simulating
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-500 uppercase bg-emerald-500/10 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span> Live GPS
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* FLOATING MAP CONTROLS (RIGHT) */}
        <div className="absolute right-4 top-24 z-10 flex flex-col gap-2 pointer-events-auto">
          <button
            onClick={handleLocateMe}
            title="My Location"
            className={`p-3 border border-outline-variant/60 hover:border-primary rounded-xl shadow-lg transition active:scale-95 cursor-pointer backdrop-blur ${autoFollow ? 'bg-primary/10 text-primary' : 'bg-surface/90 text-on-surface hover:text-primary'}`}
          >
            <Target size={16} />
          </button>
          <button
            onClick={handleFitRoute}
            title="Fit Route"
            className="p-3 bg-surface/90 border border-outline-variant/60 hover:border-primary text-on-surface hover:text-primary rounded-xl shadow-lg transition active:scale-95 cursor-pointer backdrop-blur"
          >
            <Compass size={16} />
          </button>
          <div className="flex flex-col border border-outline-variant/60 rounded-xl overflow-hidden shadow-lg bg-surface/90 backdrop-blur">
            <button
              onClick={handleZoomIn}
              title="Zoom In"
              className="p-3 hover:bg-surface-variant/40 text-on-surface hover:text-primary transition active:scale-95 cursor-pointer"
            >
              <ZoomIn size={16} />
            </button>
            <div className="h-[1px] bg-outline-variant/30" />
            <button
              onClick={handleZoomOut}
              title="Zoom Out"
              className="p-3 hover:bg-surface-variant/40 text-on-surface hover:text-primary transition active:scale-95 cursor-pointer"
            >
              <ZoomOut size={16} />
            </button>
          </div>
        </div>

        {/* BOTTOM PANEL: Pre-navigation "Start" or Turn-by-turn instructions */}
        <div className="absolute bottom-4 left-4 right-4 z-10 pointer-events-none max-w-lg mx-auto select-none">
          
          {/* Pre-navigation: Show "Start Navigation" button */}
          {!navigationStarted && !hasArrived && route && (
            <div className="bg-surface/95 backdrop-blur-md border border-outline-variant/65 rounded-2xl p-5 shadow-2xl pointer-events-auto flex flex-col gap-4">
              {/* Route summary */}
              <div className="grid grid-cols-3 gap-2 bg-surface-variant/20 p-3 rounded-xl border border-outline-variant/30 text-center text-xs font-semibold">
                <div>
                  <span className="text-[8px] block text-on-surface/40 uppercase font-black">Distance</span>
                  <span className="text-sm font-black text-on-surface mt-0.5 block">
                    {remainingDistance >= 1000 ? `${(remainingDistance / 1000).toFixed(1)} km` : `${remainingDistance} m`}
                  </span>
                </div>
                <div>
                  <span className="text-[8px] block text-on-surface/40 uppercase font-black">Walk Time</span>
                  <span className="text-sm font-black text-on-surface mt-0.5 block">{remainingTime} min</span>
                </div>
                <div>
                  <span className="text-[8px] block text-on-surface/40 uppercase font-black">Steps</span>
                  <span className="text-sm font-black text-on-surface mt-0.5 block">{route.navigation_instructions.length}</span>
                </div>
              </div>

              {/* First instruction preview */}
              <div className="flex items-start gap-3 text-left">
                <div className="p-2 bg-primary/10 rounded-xl text-primary shrink-0 mt-0.5">
                  <Navigation size={16} />
                </div>
                <div>
                  <p className="text-[10px] text-on-surface-variant/60 font-bold uppercase tracking-wider">First Direction</p>
                  <p className="text-xs font-bold text-on-surface leading-snug mt-0.5">{nextInstruction}</p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleStop}
                  className="px-4 py-3 border border-outline-variant/60 hover:bg-surface-variant/30 text-on-surface/70 text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 active:scale-[0.98] cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={() => beginNavigation()}
                  className="flex-1 py-3 bg-primary hover:bg-primary/90 text-background text-sm font-black uppercase tracking-wider rounded-xl transition duration-150 flex items-center justify-center gap-2 active:scale-[0.98] cursor-pointer shadow-lg"
                >
                  <Play size={16} className="fill-current" />
                  <span>Start Navigation</span>
                </button>
              </div>
            </div>
          )}

          {/* Active navigation: Turn-by-turn instructions */}
          {navigationStarted && !hasArrived && (
            <div className="bg-surface/95 backdrop-blur-md border border-outline-variant/65 rounded-2xl p-4.5 shadow-2xl pointer-events-auto flex flex-col gap-3">
              {/* Progress bar */}
              <div className="w-full h-1.5 bg-surface-variant/30 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${Math.round(routeProgress * 100)}%` }}
                />
              </div>

              <div className="flex justify-between items-start gap-4">
                <div>
                  <p className="text-[10px] text-primary font-bold uppercase tracking-wider">Next Turn</p>
                  <p className="text-xs font-black text-on-surface leading-snug mt-0.5">
                    {nextInstruction}
                  </p>
                </div>
                <button
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                  title={voiceEnabled ? "Mute speech guidance" : "Unmute speech guidance"}
                  className={`p-2 rounded-lg border transition ${
                    voiceEnabled
                      ? "bg-primary/5 border-primary/20 text-primary hover:bg-primary/10"
                      : "bg-surface-variant/30 border-outline-variant text-on-surface-variant hover:text-primary"
                  }`}
                >
                  {voiceEnabled ? <Volume2 size={14} /> : <VolumeX size={14} />}
                </button>
              </div>

              <div className="grid grid-cols-3 gap-2 bg-surface-variant/20 p-2.5 rounded-xl border border-outline-variant/30 text-center text-xs font-semibold">
                <div>
                  <span className="text-[8px] block text-on-surface/40 uppercase font-black">Remaining</span>
                  <span className="text-xs font-black text-on-surface mt-0.5 block">
                    {remainingDistance >= 1000 ? `${(remainingDistance / 1000).toFixed(1)} km` : `${remainingDistance} m`}
                  </span>
                </div>
                <div>
                  <span className="text-[8px] block text-on-surface/40 uppercase font-black">Time</span>
                  <span className="text-xs font-black text-on-surface mt-0.5 block">{remainingTime} min</span>
                </div>
                <div>
                  <span className="text-[8px] block text-on-surface/40 uppercase font-black">Arrival</span>
                  <span className="text-xs font-black text-on-surface mt-0.5 block">{getEstimatedArrival(remainingTime)}</span>
                </div>
              </div>

              <button
                onClick={handleStop}
                className="w-full py-2.5 bg-red-500 hover:bg-red-600 text-white text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 flex items-center justify-center gap-1 active:scale-[0.98] cursor-pointer"
              >
                <X size={14} />
                <span>Stop Navigation</span>
              </button>
            </div>
          )}
        </div>

        {/* ARRIVAL CELEBRATION OVERLAY */}
        {hasArrived && (
          <div className="absolute inset-0 bg-background/90 backdrop-blur-md z-[3000] flex flex-col items-center justify-center p-6 text-center select-none animate-in fade-in duration-300">
            <div className="bg-surface border border-outline-variant/60 rounded-3xl p-8 max-w-sm w-full shadow-2xl flex flex-col items-center gap-4">
              <div className="w-16 h-16 bg-emerald-500/10 text-emerald-500 rounded-full flex items-center justify-center animate-bounce">
                <Award size={36} />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-black text-on-surface tracking-tight">Destination Reached!</h3>
                <p className="text-xs text-on-surface-variant font-semibold">
                  You have arrived safely at:
                </p>
                <h4 className="text-base font-black text-primary mt-1">
                  {destinationNode?.name}
                </h4>
              </div>
              <div className="flex items-center gap-1.5 py-1 px-3 bg-emerald-500/5 text-emerald-500 border border-emerald-500/15 rounded-xl text-[10px] font-bold uppercase tracking-wider">
                <Sparkles size={12} className="animate-spin" /> Route completed
              </div>
              <button
                onClick={handleStop}
                className="w-full py-3 bg-primary hover:bg-primary/95 text-background text-xs font-bold uppercase tracking-wider rounded-xl transition duration-150 active:scale-[0.98] cursor-pointer"
              >
                Finish Navigation
              </button>
            </div>
          </div>
        )}

        {/* GPS FALLBACK MANUAL DROPDOWN MODAL */}
        <NavigationLocationModal
          isOpen={showLocationModal}
          onClose={() => setShowLocationModal(false)}
          allNodes={allNodes}
        />
      </div>
    </div>
  );
};
export default NavigationPage;
