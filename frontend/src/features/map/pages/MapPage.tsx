// src/features/map/pages/MapPage.tsx

import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CampusMap from "../components/CampusMap";
import { MapToolbar } from "../../navigation/components/MapToolbar";
import { LocationDetailsDrawer } from "../../navigation/components/LocationDetailsDrawer";
import { RoutePanel } from "../../navigation/components/RoutePanel";
import { LayersDrawer } from "../../navigation/components/LayersDrawer";
import { NavigationSidebar } from "../../navigation/components/NavigationSidebar";
import { MiniInfoCard } from "../../navigation/components/MiniInfoCard";
import { navigationApi } from "../../navigation/services/navigationApi";

import { useBuildings, useLandmarks, useFacilities } from "../../navigation/hooks/useNavigation";
import { useLiveNavigationStore } from "../../navigation/store/useLiveNavigationStore";
import type { Building, Facility, Landmark, Room, NavigationSearchResult, GraphNode, Route } from "../../navigation/types";

export const MapPage: React.FC = () => {
  const navigateTo = useNavigate();
  // 1. Fetch Real Spatial Datasets from custom hooks
  const { buildings, loading: buildingsLoading } = useBuildings();
  const { landmarks, loading: landmarksLoading } = useLandmarks();
  const { facilities, loading: facilitiesLoading } = useFacilities();

  // 2. Map Layer Visibility State (persisted to localStorage)
  const [showBuildings, setShowBuildings] = useState(() => {
    const saved = localStorage.getItem("map_show_buildings");
    return saved !== null ? JSON.parse(saved) : true;
  });
  const [showLandmarks, setShowLandmarks] = useState(() => {
    const saved = localStorage.getItem("map_show_landmarks");
    return saved !== null ? JSON.parse(saved) : true;
  });
  const [showFacilities, setShowFacilities] = useState(() => {
    const saved = localStorage.getItem("map_show_facilities");
    return saved !== null ? JSON.parse(saved) : true;
  });
  const [showRouteLayer, setShowRouteLayer] = useState(() => {
    const saved = localStorage.getItem("map_show_route_layer");
    return saved !== null ? JSON.parse(saved) : true;
  });

  const [isLayersDrawerOpen, setIsLayersDrawerOpen] = useState(false);
  const [zoomToRouteTrigger, setZoomToRouteTrigger] = useState(0);

  // Sync settings to localStorage
  useEffect(() => {
    localStorage.setItem("map_show_buildings", JSON.stringify(showBuildings));
  }, [showBuildings]);
  useEffect(() => {
    localStorage.setItem("map_show_landmarks", JSON.stringify(showLandmarks));
  }, [showLandmarks]);
  useEffect(() => {
    localStorage.setItem("map_show_facilities", JSON.stringify(showFacilities));
  }, [showFacilities]);
  useEffect(() => {
    localStorage.setItem("map_show_route_layer", JSON.stringify(showRouteLayer));
  }, [showRouteLayer]);

  // 3. Selection States
  const [selectedEntity, setSelectedEntity] = useState<any | null>(null);
  const [selectedEntityType, setSelectedEntityType] = useState<"building" | "room" | "facility" | "landmark" | null>(null);

  // 4. Hover States
  const [hoveredEntity, setHoveredEntity] = useState<any | null>(null);
  const [hoveredEntityType, setHoveredEntityType] = useState<"building" | "facility" | "landmark" | null>(null);

  // 5. Favorites State (loaded from localStorage)
  const [favorites, setFavorites] = useState<any[]>([]);
  const loadFavorites = () => {
    const saved = localStorage.getItem("map_favorites");
    setFavorites(saved ? JSON.parse(saved) : []);
  };
  useEffect(() => {
    loadFavorites();
    window.addEventListener("favorites_changed", loadFavorites);
    return () => window.removeEventListener("favorites_changed", loadFavorites);
  }, []);

  const handleAddFavorite = (entity: any) => {
    const favs = localStorage.getItem("map_favorites");
    let favList = favs ? JSON.parse(favs) : [];
    if (!favList.some((f: any) => f.id === entity._id)) {
      const name = entity.building_name || entity.name || "";
      const lat = entity.latitude || entity.coordinates?.latitude || 0;
      const lng = entity.longitude || entity.coordinates?.longitude || 0;
      let type = "building";
      if (buildings.some((b) => b._id === entity._id)) type = "building";
      else if (facilities.some((f) => f._id === entity._id)) type = "facility";
      else if (landmarks.some((l) => l._id === entity._id)) type = "landmark";

      favList.push({ id: entity._id, name, type, latitude: lat, longitude: lng });
      localStorage.setItem("map_favorites", JSON.stringify(favList));
      loadFavorites();
    }
  };

  const handleRemoveFavorite = (id: string) => {
    const favs = localStorage.getItem("map_favorites");
    if (favs) {
      let favList = JSON.parse(favs);
      favList = favList.filter((f: any) => f.id !== id);
      localStorage.setItem("map_favorites", JSON.stringify(favList));
      loadFavorites();
    }
  };

  // 6. Recents State
  const [recents, setRecents] = useState<any[]>([]);
  const loadRecents = () => {
    const saved = localStorage.getItem("map_recent_searches");
    setRecents(saved ? JSON.parse(saved) : []);
  };
  useEffect(() => {
    loadRecents();
  }, []);

  const handleClearRecents = () => {
    localStorage.removeItem("map_recent_searches");
    setRecents([]);
  };

  // 7. Ref to reset map camera zoom
  const resetViewRef = useRef<(() => void) | null>(null);

  // 8. Smart Routing States
  const [isRouting, setIsRouting] = useState(false);
  const [allNodes, setAllNodes] = useState<GraphNode[]>([]);
  const [routePath, setRoutePath] = useState<[number, number][]>([]);
  const [activeRoute, setActiveRoute] = useState<Route | null>(null);
  const [selectedStartNode, setSelectedStartNode] = useState<GraphNode | null>(null);
  const [selectedDestinationNode, setSelectedDestinationNode] = useState<GraphNode | null>(null);

  // Load all nodes on mount for routing selectors
  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const nodes = await navigationApi.fetchGraphNodes();
        setAllNodes(nodes);
      } catch (err) {
        console.error("Error loading graph nodes for routing", err);
      }
    };
    fetchNodes();
  }, []);

  const handleGetDirections = (id: string, name: string) => {
    let node = allNodes.find((n) => n.id === id);
    if (!node) {
      node = allNodes.find((n) => n.name.toLowerCase().includes(name.toLowerCase()));
    }
    if (node) {
      setSelectedDestinationNode(node);
      // Default start to Main Gate if not set
      if (!selectedStartNode) {
        const mainGateNode = allNodes.find((n) => n.id === "f_gate");
        if (mainGateNode) {
          setSelectedStartNode(mainGateNode);
        }
      }
      setIsRouting(true);
      setSelectedEntity(null);
      setSelectedEntityType(null);
    }
  };

  const handleSetStart = (id: string, name: string) => {
    let node = allNodes.find((n) => n.id === id);
    if (!node) {
      node = allNodes.find((n) => n.name.toLowerCase().includes(name.toLowerCase()));
    }
    if (node) {
      setSelectedStartNode(node);
      setIsRouting(true);
    }
  };

  const handleSetDestination = (id: string, name: string) => {
    let node = allNodes.find((n) => n.id === id);
    if (!node) {
      node = allNodes.find((n) => n.name.toLowerCase().includes(name.toLowerCase()));
    }
    if (node) {
      setSelectedDestinationNode(node);
      setIsRouting(true);
    }
  };

  // Filter lists based on category
  const filteredBuildings = buildings;
  const filteredFacilities = facilities;
  const filteredLandmarks = landmarks;

  const handleEntityClick = (entity: any, type: "building" | "facility" | "landmark") => {
    setSelectedEntity(entity);
    setSelectedEntityType(type);
  };

  const handleSearchResultSelect = (result: NavigationSearchResult) => {
    const type = result.type;
    let resolvedEntity = null;

    if (type === "building") {
      resolvedEntity = buildings.find((b) => b._id === result._id);
      setSelectedEntityType("building");
    } else if (type === "room") {
      resolvedEntity = {
        _id: result._id,
        room_number: result.metadata.room_number,
        room_name: result.name.split(" - ")[1] || result.name,
        building_id: result.metadata.building_id,
        floor: result.metadata.floor,
        room_type: result.category,
        capacity: result.metadata.capacity,
        latitude: result.latitude,
        longitude: result.longitude,
        description: result.description,
        facilities: result.metadata.facilities || [],
        metadata: {}
      };
      setSelectedEntityType("room");
    } else if (type === "landmark") {
      resolvedEntity = landmarks.find((l) => l._id === result._id);
      setSelectedEntityType("landmark");
    } else if (type === "facility") {
      resolvedEntity = facilities.find((f) => f._id === result._id);
      setSelectedEntityType("facility");
    }

    if (resolvedEntity) {
      setSelectedEntity(resolvedEntity);
      // Reload recents to include new search
      setTimeout(loadRecents, 200);
    }
  };

  const handleSubRoomSelect = (room: Room) => {
    setSelectedEntity(room);
    setSelectedEntityType("room");
  };

  const handleClearSearch = () => {
    setSelectedEntity(null);
    setSelectedEntityType(null);
  };

  const handleQuickDestinationSelect = (id: string, name: string) => {
    let destNode = allNodes.find((n) => n.id === id);
    if (!destNode) {
      destNode = allNodes.find((n) => n.name.toLowerCase().includes(name.toLowerCase()));
    }
    if (destNode) {
      setSelectedDestinationNode(destNode);
      if (!selectedStartNode) {
        const mainGateNode = allNodes.find((n) => n.id === "f_gate");
        if (mainGateNode) {
          setSelectedStartNode(mainGateNode);
        }
      }
      setIsRouting(true);
      setSelectedEntity(null);
      setSelectedEntityType(null);
    }
  };

  const handleSelectFavoriteOrRecent = (item: any) => {
    let entity = null;
    if (item.type === "building") {
      entity = buildings.find((b) => b._id === item.id);
    } else if (item.type === "facility") {
      entity = facilities.find((f) => f._id === item.id);
    } else if (item.type === "landmark") {
      entity = landmarks.find((l) => l._id === item.id);
    }
    if (entity) {
      setSelectedEntity(entity);
      setSelectedEntityType(item.type);
    }
  };

  const handleNavigateFavoriteOrRecent = (item: any) => {
    let node = allNodes.find((n) => n.id === item.id);
    if (!node) {
      node = allNodes.find((n) => n.name.toLowerCase().includes(item.name.toLowerCase()));
    }
    if (node) {
      setSelectedDestinationNode(node);
      if (!selectedStartNode) {
        const mainGateNode = allNodes.find((n) => n.id === "f_gate");
        if (mainGateNode) {
          setSelectedStartNode(mainGateNode);
        }
      }
      setIsRouting(true);
      setSelectedEntity(null);
      setSelectedEntityType(null);
    }
  };

  // Handler: Start immersive navigation from MapPage
  const handleStartNavigation = (startNode: GraphNode, destNode: GraphNode, route: Route, pathPoints: [number, number][]) => {
    useLiveNavigationStore.getState().startNavigationWithRoute(startNode, destNode, route, pathPoints, allNodes);
    navigateTo("/navigation");
  };

  // Render Sidebar route panel instance
  const routePanelElement = (
    <RoutePanel
      allNodes={allNodes}
      selectedStart={selectedStartNode}
      selectedDestination={selectedDestinationNode}
      onClear={() => {
        setIsRouting(false);
        setRoutePath([]);
        setActiveRoute(null);
        setSelectedDestinationNode(null);
        setSelectedStartNode(null);
      }}
      onRouteCalculated={(route, pathPoints) => {
        setActiveRoute(route);
        setRoutePath(pathPoints);
      }}
      onStartNavigation={handleStartNavigation}
    />
  );

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col p-6 min-h-0 bg-background select-none relative overflow-hidden text-left">
      
      {/* 1. MAP CONTAINER */}
      <div className="flex-1 rounded-2xl overflow-hidden border border-outline-variant/60 shadow-inner relative z-0">
        <CampusMap
          buildings={filteredBuildings}
          landmarks={filteredLandmarks}
          facilities={filteredFacilities}
          allNodes={allNodes}
          showBuildings={showBuildings}
          showLandmarks={showLandmarks}
          showFacilities={showFacilities}
          selectedEntity={selectedEntity}
          selectedEntityType={selectedEntityType}
          onEntityClick={handleEntityClick}
          onResetViewRef={resetViewRef}
          routePath={routePath}
          showRouteLayer={showRouteLayer}
          zoomToRouteTrigger={zoomToRouteTrigger}
          onSetStart={handleSetStart}
          onSetDestination={handleSetDestination}
          onViewDetails={handleEntityClick}
          onAddFavorite={handleAddFavorite}
          onHoverEntity={(entity, type) => {
            setHoveredEntity(entity);
            setHoveredEntityType(type as any);
          }}
        />
      </div>

      {/* 2. FLOATING OVERLAYS */}

      {/* Top Left: Custom Collapsible Sidebar */}
      <div className="absolute top-10 left-10 z-[1000] flex flex-col gap-3 max-w-sm w-full pr-16 md:pr-0">
        <NavigationSidebar
          allNodes={allNodes}
          buildings={buildings}
          facilities={facilities}
          landmarks={landmarks}
          onResultSelect={handleSearchResultSelect}
          onClearSearch={handleClearSearch}
          favorites={favorites}
          onSelectFavorite={handleSelectFavoriteOrRecent}
          onNavigateFavorite={handleNavigateFavoriteOrRecent}
          onRemoveFavorite={handleRemoveFavorite}
          recents={recents}
          onSelectRecent={handleSelectFavoriteOrRecent}
          onNavigateRecent={handleNavigateFavoriteOrRecent}
          onClearRecents={handleClearRecents}
          onQuickDestinationSelect={handleQuickDestinationSelect}
          selectedEntity={selectedEntity}
          onSelectNearby={handleEntityClick}
          onNavigateNearby={handleNavigateFavoriteOrRecent}
          onToggleLayers={() => setIsLayersDrawerOpen(!isLayersDrawerOpen)}
          isRouting={isRouting}
          routePanelElement={routePanelElement}
        />
      </div>

      {/* Top Right: Grouped Map Toolbar Controls */}
      <div className="absolute top-10 right-10 z-[1000]">
        <MapToolbar
          onToggleLayers={() => setIsLayersDrawerOpen(!isLayersDrawerOpen)}
          onLocate={() => resetViewRef.current?.()}
          onResetView={() => resetViewRef.current?.()}
          onZoomToRoute={() => setZoomToRouteTrigger((prev) => prev + 1)}
          onClearRoute={() => {
            setRoutePath([]);
            setActiveRoute(null);
            setIsRouting(false);
            setSelectedDestinationNode(null);
            setSelectedStartNode(null);
          }}
          routeActive={routePath.length > 0}
        />
      </div>

      {/* Bottom Right: Floating Hover Preview Card */}
      {hoveredEntity && hoveredEntityType && (
        <div className="absolute bottom-10 right-10 md:right-104 z-[2000]">
          <MiniInfoCard
            entity={hoveredEntity}
            type={hoveredEntityType}
            onNavigate={() => {
              const name = hoveredEntity.building_name || hoveredEntity.name || "";
              handleGetDirections(hoveredEntity._id, name);
              setHoveredEntity(null);
              setHoveredEntityType(null);
            }}
            onViewDetails={() => {
              setSelectedEntity(hoveredEntity);
              setSelectedEntityType(hoveredEntityType);
              setHoveredEntity(null);
              setHoveredEntityType(null);
            }}
          />
        </div>
      )}

      {/* Map settings sliding drawer */}
      <LayersDrawer
        isOpen={isLayersDrawerOpen}
        onClose={() => setIsLayersDrawerOpen(false)}
        showBuildings={showBuildings}
        setShowBuildings={setShowBuildings}
        showLandmarks={showLandmarks}
        setShowLandmarks={setShowLandmarks}
        showFacilities={showFacilities}
        setShowFacilities={setShowFacilities}
        showRouteLayer={showRouteLayer}
        setShowRouteLayer={setShowRouteLayer}
        buildings={buildings}
        landmarks={landmarks}
        facilities={facilities}
        routeActive={routePath.length > 0}
      />

      {/* Details Side Drawer */}
      <LocationDetailsDrawer
        entity={selectedEntity}
        entityType={selectedEntityType}
        onClose={() => {
          setSelectedEntity(null);
          setSelectedEntityType(null);
        }}
        onSelectSubRoom={handleSubRoomSelect}
        onGetDirections={handleGetDirections}
        onSelectEntity={handleEntityClick}
        allBuildings={buildings}
        allFacilities={facilities}
        allLandmarks={landmarks}
      />
    </div>
  );
};

export default MapPage;
