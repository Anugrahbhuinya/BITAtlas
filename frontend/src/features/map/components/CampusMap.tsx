// src/features/map/components/CampusMap.tsx

import React from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import { CampusMapLayer } from "../../navigation/components/CampusMapLayer";
import { MapContextMenu } from "../../navigation/components/MapContextMenu";
import type { Building, Facility, Landmark, GraphNode } from "../../navigation/types";

interface CampusMapProps {
  buildings: Building[];
  landmarks: Landmark[];
  facilities: Facility[];
  allNodes: GraphNode[];
  showBuildings: boolean;
  showLandmarks: boolean;
  showFacilities: boolean;
  selectedEntity: any;
  selectedEntityType: "building" | "room" | "facility" | "landmark" | null;
  onEntityClick: (entity: any, type: "building" | "facility" | "landmark") => void;
  onResetViewRef?: React.MutableRefObject<(() => void) | null>;
  routePath?: [number, number][];
  showRouteLayer?: boolean;
  zoomToRouteTrigger?: number;
  onHoverEntity?: (entity: any, type: "building" | "facility" | "landmark" | null) => void;

  // Context Menu Callbacks
  onSetStart: (id: string, name: string) => void;
  onSetDestination: (id: string, name: string) => void;
  onViewDetails: (entity: any, type: "building" | "facility" | "landmark") => void;
  onAddFavorite: (entity: any) => void;
}

const CENTER: [number, number] = [23.4129, 85.4407];
const ZOOM = 16;

// Ref-based controller to allow resetting view from parent toolbar
function MapController({ onResetViewRef }: { onResetViewRef?: React.MutableRefObject<(() => void) | null> }) {
  const map = React.useRef(null);
  const leafletMap = useMap();

  React.useEffect(() => {
    if (onResetViewRef) {
      onResetViewRef.current = () => {
        leafletMap.setView(CENTER, ZOOM, { animate: true });
      };
    }
  }, [leafletMap, onResetViewRef]);

  return null;
}

export const CampusMap: React.FC<CampusMapProps> = ({
  buildings,
  landmarks,
  facilities,
  allNodes,
  showBuildings,
  showLandmarks,
  showFacilities,
  selectedEntity,
  selectedEntityType,
  onEntityClick,
  onResetViewRef,
  routePath,
  showRouteLayer = true,
  zoomToRouteTrigger = 0,
  onSetStart,
  onSetDestination,
  onViewDetails,
  onAddFavorite,
  onHoverEntity
}) => {
  return (
    <MapContainer
      center={CENTER}
      zoom={ZOOM}
      className="h-full w-full rounded-xl z-0"
    >
      <TileLayer
        attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapController onResetViewRef={onResetViewRef} />

      <MapContextMenu
        buildings={buildings}
        facilities={facilities}
        landmarks={landmarks}
        allNodes={allNodes}
        onSetStart={onSetStart}
        onSetDestination={onSetDestination}
        onViewDetails={onViewDetails}
        onAddFavorite={onAddFavorite}
      />

      <CampusMapLayer
        buildings={buildings}
        landmarks={landmarks}
        facilities={facilities}
        showBuildings={showBuildings}
        showLandmarks={showLandmarks}
        showFacilities={showFacilities}
        selectedEntity={selectedEntity}
        selectedEntityType={selectedEntityType}
        onEntityClick={onEntityClick}
        routePath={routePath}
        showRouteLayer={showRouteLayer}
        zoomToRouteTrigger={zoomToRouteTrigger}
        onHoverEntity={onHoverEntity}
      />
    </MapContainer>
  );
};

export default CampusMap;
