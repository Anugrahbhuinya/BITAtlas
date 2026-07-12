// src/features/navigation/store/useLiveNavigationStore.ts

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { GraphNode, Route } from "../types";
import { navigationApi } from "../services/navigationApi";

// Distance helper: squared Euclidean distance for local node matching
const getSquaredDistance = (lat1: number, lng1: number, lat2: number, lng2: number) => {
  return Math.pow(lat1 - lat2, 2) + Math.pow(lng1 - lng2, 2);
};

// Haversine distance in meters
const getHaversineDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
  const R = 6371e3; // metres
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // in meters
};

// Linear interpolation helper between two lat/lng points
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

interface LiveNavigationState {
  isNavigating: boolean;
  navigationStarted: boolean; // true after user clicks "Start" on the navigation page
  routeLoading: boolean;
  routeError: string | null;
  startNode: GraphNode | null;
  destinationNode: GraphNode | null;
  currentGPS: [number, number] | null;
  route: Route | null;
  routePathPoints: [number, number][];
  nextInstruction: string;
  remainingDistance: number; // in meters
  remainingTime: number; // in minutes
  routeProgress: number; // 0-1 fraction of route completed
  watchId: number | null;
  voiceEnabled: boolean;
  showLocationModal: boolean;
  isOffRoute: boolean;
  hasArrived: boolean;
  allNodes: GraphNode[];
  lastSpokenInstruction: string;
  accessibilityMode: boolean;

  // Simulation state
  isSimulating: boolean;
  simulationProgress: number; // cumulative distance walked in meters
  simulationTimerId: ReturnType<typeof setInterval> | null;

  setAllNodes: (nodes: GraphNode[]) => void;
  setStartNode: (node: GraphNode | null) => void;
  setDestinationNode: (node: GraphNode | null) => void;
  setVoiceEnabled: (enabled: boolean) => void;
  setShowLocationModal: (show: boolean) => void;
  startNavigation: (destination: GraphNode, allNodes: GraphNode[], explicitSource?: string | null) => Promise<void>;
  startNavigationWithRoute: (startNode: GraphNode, destNode: GraphNode, route: Route, pathPoints: [number, number][], allNodes: GraphNode[]) => void;
  beginNavigation: () => void; // Called when user clicks "Start" button on navigation page
  stopNavigation: () => void;
  updatePosition: (lat: number, lng: number) => Promise<void>;
  recalculateRoute: () => Promise<void>;
  startWatchingPosition: () => void;
  startSimulation: () => void;
  stopSimulation: () => void;
}

export const useLiveNavigationStore = create<LiveNavigationState>()(
  persist(
    (set, get) => {
  // Voice reader helper
  const speakDirection = (text: string) => {
    if (!get().voiceEnabled || !text) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.error("Speech Synthesis failed:", e);
    }
  };

  // Helper to compute total polyline length in meters
  const computePolylineLength = (points: [number, number][]) => {
    let total = 0;
    for (let i = 0; i < points.length - 1; i++) {
      total += getHaversineDistance(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]);
    }
    return total;
  };

  // Helper to find the position along polyline at a given cumulative distance
  const getPositionAtDistance = (points: [number, number][], targetDist: number): [number, number] => {
    let accumulated = 0;
    for (let i = 0; i < points.length - 1; i++) {
      const segLen = getHaversineDistance(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]);
      if (accumulated + segLen >= targetDist) {
        const t = segLen > 0 ? (targetDist - accumulated) / segLen : 0;
        return [lerp(points[i][0], points[i + 1][0], t), lerp(points[i][1], points[i + 1][1], t)];
      }
      accumulated += segLen;
    }
    // Return last point if distance exceeds polyline
    return points[points.length - 1];
  };

  return {
    isNavigating: false,
    navigationStarted: false,
    routeLoading: false,
    routeError: null,
    startNode: null,
    destinationNode: null,
    currentGPS: null,
    route: null,
    routePathPoints: [],
    nextInstruction: "Preparing route...",
    remainingDistance: 0,
    remainingTime: 0,
    routeProgress: 0,
    watchId: null,
    voiceEnabled: true,
    showLocationModal: false,
    isOffRoute: false,
    hasArrived: false,
    allNodes: [],
    lastSpokenInstruction: "",
    accessibilityMode: false,
    isSimulating: false,
    simulationProgress: 0,
    simulationTimerId: null,

    setAllNodes: (nodes) => set({ allNodes: nodes }),
    setStartNode: (node) => set({ startNode: node }),
    setDestinationNode: (node) => set({ destinationNode: node }),
    setVoiceEnabled: (enabled) => set({ voiceEnabled: enabled }),
    setShowLocationModal: (show) => set({ showLocationModal: show }),

    // Pre-load a calculated route directly (used when transitioning from MapPage)
    startNavigationWithRoute: (startNode, destNode, route, pathPoints, allNodes) => {
      const firstInstruction = route.navigation_instructions[0] || "Head towards destination.";
      set({
        isNavigating: true,
        navigationStarted: false,
        routeLoading: false,
        routeError: null,
        startNode,
        destinationNode: destNode,
        route,
        routePathPoints: pathPoints,
        allNodes,
        currentGPS: [pathPoints[0][0], pathPoints[0][1]],
        remainingDistance: route.total_distance,
        remainingTime: Math.round(route.estimated_walking_time / 60),
        nextInstruction: firstInstruction,
        hasArrived: false,
        isOffRoute: false,
        lastSpokenInstruction: "",
        showLocationModal: false,
        routeProgress: 0,
        isSimulating: false,
        simulationProgress: 0,
      });
    },

    // Called when user clicks "Start" button on navigation page to begin movement
    beginNavigation: () => {
      const { routePathPoints, destinationNode, startNode } = get();
      if (!routePathPoints.length || !destinationNode) return;

      set({ navigationStarted: true });

      const firstInstruction = get().route?.navigation_instructions[0] || "Head towards destination.";
      speakDirection(`Starting navigation to ${destinationNode.name}${startNode ? ` from ${startNode.name}` : ""}. ${firstInstruction}`);

      // Try GPS first, fall back to simulation
      let gpsAvailable = false;
      if (navigator.geolocation) {
        try {
          navigator.geolocation.getCurrentPosition(
            () => {
              gpsAvailable = true;
              get().startWatchingPosition();
            },
            () => {
              // GPS denied or unavailable — start simulation
              console.log("GPS unavailable, starting simulation mode");
              get().startSimulation();
            },
            { enableHighAccuracy: true, timeout: 3000 }
          );
        } catch {
          get().startSimulation();
        }
      } else {
        get().startSimulation();
      }
    },

    startNavigation: async (destination, allNodes, explicitSource = null) => {
      // Keep track of previous startNode before resetting for last known location fallback
      const prevStartNode = get().startNode;

      set({ 
        destinationNode: destination, 
        allNodes, 
        isNavigating: true,
        navigationStarted: false,
        hasArrived: false,
        isOffRoute: false,
        lastSpokenInstruction: "",
        routeLoading: true,
        routeError: null,
        route: null,
        routePathPoints: [],
        currentGPS: null,
        startNode: null,
        routeProgress: 0,
        isSimulating: false,
        simulationProgress: 0,
      });

      // Check if permission is already granted
      let permissionGranted = false;
      try {
        if (navigator.permissions && navigator.geolocation) {
          const status = await navigator.permissions.query({ name: "geolocation" });
          if (status.state === "granted") {
            permissionGranted = true;
          }
        }
      } catch (e) {
        console.warn("navigator.permissions query not supported:", e);
      }

      // Priority 1: Browser GPS (if permission is already granted)
      if (permissionGranted && navigator.geolocation) {
        try {
          const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 3000 });
          });
          const { latitude, longitude } = pos.coords;
          set({ currentGPS: [latitude, longitude] });

          // Find nearest node
          let nearest: GraphNode | null = null;
          let minD = Infinity;
          for (const node of allNodes) {
            const d = getSquaredDistance(latitude, longitude, node.coordinates.latitude, node.coordinates.longitude);
            if (d < minD) {
              minD = d;
              nearest = node;
            }
          }

          if (nearest) {
            set({ startNode: nearest });
            const strategy = get().accessibilityMode ? "accessible" : "shortest";
            const routeRes = await navigationApi.calculateRoute(nearest.id, destination.id, strategy as any);
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
            set({
              route: routeRes,
              routePathPoints: pathPoints,
              remainingDistance: routeRes.total_distance,
              remainingTime: Math.round(routeRes.estimated_walking_time / 60),
              nextInstruction: firstInstruction,
              routeLoading: false,
            });
            // Don't auto-start navigation — wait for user to click "Start"
            return;
          }
        } catch (err) {
          console.error("Auto GPS routing failed, falling back to priority list:", err);
        }
      }

      // Priority 2: User explicitly provided source (if any)
      if (explicitSource) {
        const resolvedStartNode = allNodes.find(
          (n) => n.name.toLowerCase() === explicitSource.toLowerCase()
        ) || allNodes.find((n) =>
          n.name.toLowerCase().includes(explicitSource.toLowerCase())
        );

        if (resolvedStartNode) {
          set({ 
            startNode: resolvedStartNode,
            currentGPS: [resolvedStartNode.coordinates.latitude, resolvedStartNode.coordinates.longitude]
          });
          const strategy = get().accessibilityMode ? "accessible" : "shortest";
          try {
            const routeRes = await navigationApi.calculateRoute(resolvedStartNode.id, destination.id, strategy as any);
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
            set({
              route: routeRes,
              routePathPoints: pathPoints,
              remainingDistance: routeRes.total_distance,
              remainingTime: Math.round(routeRes.estimated_walking_time / 60),
              nextInstruction: firstInstruction,
              routeLoading: false,
            });
            return;
          } catch (err) {
            console.error("Routing from explicit source failed:", err);
          }
        }
      }

      // Priority 3: Last known location from the current navigation session
      if (prevStartNode) {
        set({ 
          startNode: prevStartNode,
          currentGPS: [prevStartNode.coordinates.latitude, prevStartNode.coordinates.longitude]
        });
        const strategy = get().accessibilityMode ? "accessible" : "shortest";
        try {
          const routeRes = await navigationApi.calculateRoute(prevStartNode.id, destination.id, strategy as any);
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
          set({
            route: routeRes,
            routePathPoints: pathPoints,
            remainingDistance: routeRes.total_distance,
            remainingTime: Math.round(routeRes.estimated_walking_time / 60),
            nextInstruction: firstInstruction,
            routeLoading: false,
          });
          return;
        } catch (err) {
          console.error("Routing from last known startNode failed:", err);
        }
      }

      // Priority 4: Ask the user to choose a starting location
      set({ 
        routeLoading: false, 
        showLocationModal: true,
        routeError: null
      });
    },

    stopNavigation: () => {
      const { watchId, simulationTimerId } = get();
      if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
      }
      if (simulationTimerId !== null) {
        clearInterval(simulationTimerId);
      }
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}

      set({
        isNavigating: false,
        navigationStarted: false,
        routeLoading: false,
        routeError: null,
        startNode: null,
        destinationNode: null,
        currentGPS: null,
        route: null,
        routePathPoints: [],
        nextInstruction: "Preparing route...",
        remainingDistance: 0,
        remainingTime: 0,
        routeProgress: 0,
        watchId: null,
        isOffRoute: false,
        hasArrived: false,
        lastSpokenInstruction: "",
        isSimulating: false,
        simulationProgress: 0,
        simulationTimerId: null,
      });
    },

    updatePosition: async (lat, lng) => {
      const { destinationNode, route, routePathPoints, lastSpokenInstruction } = get();
      set({ currentGPS: [lat, lng] });
      if (!destinationNode || !route) return;

      // 1. Calculate distance to destination
      const distanceToDest = getHaversineDistance(
        lat,
        lng,
        destinationNode.coordinates.latitude,
        destinationNode.coordinates.longitude
      );

      // Compute route progress
      const totalRouteLength = computePolylineLength(routePathPoints);

      // Check arrival (< 15 meters)
      if (distanceToDest < 15) {
        get().stopSimulation();
        set({ hasArrived: true, remainingDistance: 0, remainingTime: 0, nextInstruction: "You have arrived!", routeProgress: 1 });
        speakDirection(`Arrived at ${destinationNode.name}. Navigation complete.`);
        return;
      }

      // 2. Off-Route Detection (skip during simulation)
      if (!get().isSimulating) {
        let minPolyDistance = Infinity;
        for (const pt of routePathPoints) {
          const d = getHaversineDistance(lat, lng, pt[0], pt[1]);
          if (d < minPolyDistance) {
            minPolyDistance = d;
          }
        }
        if (minPolyDistance > 35) {
          set({ isOffRoute: true, nextInstruction: "Recalculating route..." });
          speakDirection("Recalculating route.");
          await get().recalculateRoute();
          return;
        }
      }

      // 3. Dynamic instruction tracking
      let nearestIndex = 0;
      let minNodeDistance = Infinity;
      const ordered = route.ordered_nodes;
      for (let i = 0; i < ordered.length; i++) {
        const node = ordered[i];
        const d = getSquaredDistance(lat, lng, node.coordinates.latitude, node.coordinates.longitude);
        if (d < minNodeDistance) {
          minNodeDistance = d;
          nearestIndex = i;
        }
      }

      const remainingNodes = ordered.slice(nearestIndex);
      let calculatedDistance = 0;
      for (let i = 0; i < remainingNodes.length - 1; i++) {
        calculatedDistance += getHaversineDistance(
          remainingNodes[i].coordinates.latitude,
          remainingNodes[i].coordinates.longitude,
          remainingNodes[i+1].coordinates.latitude,
          remainingNodes[i+1].coordinates.longitude
        );
      }

      const activeInstructions = route.navigation_instructions.slice(nearestIndex);
      const activeStep = activeInstructions[0] || "Continue straight ahead.";
      
      const newTime = Math.max(1, Math.round((calculatedDistance / 1.3)));
      const minsRemaining = Math.round(newTime / 60);

      // Calculate progress fraction
      const progressFraction = totalRouteLength > 0 ? Math.min(1, Math.max(0, 1 - (calculatedDistance / totalRouteLength))) : 0;

      set({
        remainingDistance: Math.round(calculatedDistance),
        remainingTime: minsRemaining,
        nextInstruction: activeStep,
        isOffRoute: false,
        routeProgress: progressFraction,
      });

      // Voice prompt triggers when turn changes
      if (activeStep !== lastSpokenInstruction) {
        set({ lastSpokenInstruction: activeStep });
        speakDirection(activeStep);
      }
    },

    recalculateRoute: async () => {
      const { currentGPS, destinationNode, allNodes, accessibilityMode } = get();
      if (!currentGPS || !destinationNode) return;

      set({ routeLoading: true, routeError: null });

      const [lat, lng] = currentGPS;
      let nearest: GraphNode | null = null;
      let minD = Infinity;
      for (const node of allNodes) {
        const d = getSquaredDistance(lat, lng, node.coordinates.latitude, node.coordinates.longitude);
        if (d < minD) {
          minD = d;
          nearest = node;
        }
      }

      if (nearest) {
        set({ startNode: nearest });
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
          const nextStep = routeRes.navigation_instructions[0] || "Head towards destination.";
          set({
            route: routeRes,
            routePathPoints: pathPoints,
            remainingDistance: routeRes.total_distance,
            remainingTime: Math.round(routeRes.estimated_walking_time / 60),
            nextInstruction: nextStep,
            isOffRoute: false,
            lastSpokenInstruction: nextStep,
            routeLoading: false,
          });
          speakDirection(`Route recalculated. ${nextStep}`);
        } catch (e) {
          console.error("Recalculation routing error:", e);
          set({ routeLoading: false, routeError: "Failed to recalculate navigation route." });
        }
      } else {
        set({ routeLoading: false, routeError: "No nearby campus node could be resolved for recalculation." });
      }
    },

    startWatchingPosition: () => {
      const { watchId } = get();
      if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
      }
      
      if (navigator.geolocation) {
        const newWatchId = navigator.geolocation.watchPosition(
          async (pos) => {
            const { latitude, longitude } = pos.coords;
            await get().updatePosition(latitude, longitude);
          },
          (err) => console.error("watchPosition error:", err),
          { enableHighAccuracy: true, maximumAge: 1000 }
        );
        set({ watchId: newWatchId });
      }
    },

    // Simulation: animate blue dot along the route at walking speed
    startSimulation: () => {
      const { simulationTimerId, routePathPoints } = get();
      if (simulationTimerId !== null) {
        clearInterval(simulationTimerId);
      }
      if (routePathPoints.length < 2) return;

      const totalLength = computePolylineLength(routePathPoints);
      const WALKING_SPEED = 1.3; // m/s
      const TICK_MS = 200; // update every 200ms
      const distPerTick = WALKING_SPEED * (TICK_MS / 1000); // meters per tick

      set({ isSimulating: true, simulationProgress: 0 });

      const timerId = setInterval(async () => {
        const state = get();
        if (!state.isSimulating || state.hasArrived) {
          clearInterval(timerId);
          set({ simulationTimerId: null });
          return;
        }

        const newProgress = state.simulationProgress + distPerTick;
        if (newProgress >= totalLength) {
          // Arrived
          const lastPt = routePathPoints[routePathPoints.length - 1];
          set({ simulationProgress: totalLength });
          await get().updatePosition(lastPt[0], lastPt[1]);
          clearInterval(timerId);
          set({ simulationTimerId: null });
          return;
        }

        set({ simulationProgress: newProgress });
        const pos = getPositionAtDistance(routePathPoints, newProgress);
        await get().updatePosition(pos[0], pos[1]);
      }, TICK_MS);

      set({ simulationTimerId: timerId });
    },

    stopSimulation: () => {
      const { simulationTimerId } = get();
      if (simulationTimerId !== null) {
        clearInterval(simulationTimerId);
      }
      set({ isSimulating: false, simulationTimerId: null });
    },
  };
},
{
      name: "live-navigation-storage",
      partialize: (state) => ({
        isNavigating: state.isNavigating,
        navigationStarted: state.navigationStarted,
        startNode: state.startNode,
        destinationNode: state.destinationNode,
        currentGPS: state.currentGPS,
        route: state.route,
        routePathPoints: state.routePathPoints,
        nextInstruction: state.nextInstruction,
        remainingDistance: state.remainingDistance,
        remainingTime: state.remainingTime,
        routeProgress: state.routeProgress,
        voiceEnabled: state.voiceEnabled,
        isOffRoute: state.isOffRoute,
        hasArrived: state.hasArrived,
        lastSpokenInstruction: state.lastSpokenInstruction,
        accessibilityMode: state.accessibilityMode,
      }),
    }
  )
);
