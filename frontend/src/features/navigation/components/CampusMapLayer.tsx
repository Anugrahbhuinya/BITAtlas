// src/features/navigation/components/CampusMapLayer.tsx

import React, { useEffect } from "react";
import { Marker, Popup, useMap, Polyline, Polygon } from "react-leaflet";
import L from "leaflet";
import type { Building, Facility, Landmark } from "../types";

interface CampusMapLayerProps {
  buildings: Building[];
  landmarks: Landmark[];
  facilities: Facility[];
  showBuildings: boolean;
  showLandmarks: boolean;
  showFacilities: boolean;
  selectedEntity: any;
  selectedEntityType: "building" | "room" | "facility" | "landmark" | null;
  onEntityClick: (entity: any, type: "building" | "facility" | "landmark") => void;
  routePath?: [number, number][];
  showRouteLayer?: boolean;
  zoomToRouteTrigger?: number;
  onHoverEntity?: (entity: any, type: "building" | "facility" | "landmark" | null) => void;
}

// Custom Leaflet HTML DivIcon generators to match Stitch visual style
const createHtmlIcon = (bgColor: string, symbol: string, label: string, isHighlighted: boolean = false) => {
  const pulseClass = isHighlighted 
    ? "animate-pulse ring-4 ring-primary/40 border-primary scale-110" 
    : "border-background";
    
  return L.divIcon({
    html: `
      <div class="flex flex-col items-center group">
        <div class="w-8 h-8 rounded-full ${bgColor} flex items-center justify-center text-white border-2 ${pulseClass} shadow-lg transition-transform duration-200 transform group-hover:scale-110">
          <span class="text-[12px] font-bold">${symbol}</span>
        </div>
        <span class="text-[9px] font-bold px-1.5 py-0.2 mt-1 rounded bg-surface/85 text-on-surface border border-outline-variant/40 shadow-sm max-w-[80px] truncate">${label}</span>
      </div>
    `,
    className: "custom-leaflet-icon",
    iconSize: [60, 50],
    iconAnchor: [30, 25]
  });
};

export const CampusMapLayer: React.FC<CampusMapLayerProps> = ({
  buildings,
  landmarks,
  facilities,
  showBuildings,
  showLandmarks,
  showFacilities,
  selectedEntity,
  selectedEntityType,
  onEntityClick,
  routePath,
  showRouteLayer = true,
  zoomToRouteTrigger = 0,
  onHoverEntity
}) => {
  const map = useMap();

  // Focus effect: Fly-to selected location
  useEffect(() => {
    if (!selectedEntity || (routePath && routePath.length > 0)) return;

    const lat = selectedEntity.latitude || (selectedEntity.coordinates?.latitude);
    const lng = selectedEntity.longitude || (selectedEntity.coordinates?.longitude);

    if (lat && lng) {
      map.flyTo([lat, lng], 18, {
        duration: 1.8,
        easeLinearity: 0.25
      });
    }
  }, [selectedEntity, map, routePath]);

  // Adjust camera to fit route path bounds automatically
  useEffect(() => {
    if (routePath && routePath.length > 0 && showRouteLayer) {
      const bounds = L.latLngBounds(routePath);
      map.fitBounds(bounds, { padding: [50, 50], animate: true, duration: 1.5 });
    }
  }, [routePath, map, showRouteLayer, zoomToRouteTrigger]);

  // Check if a building is the destination of the active route
  const getIsBuildingDestination = (buildingId: string) => {
    if (!routePath || routePath.length === 0) return false;
    // Check if building matches selected entity
    if (selectedEntity && selectedEntity._id === buildingId) return true;
    return false;
  };

  return (
    <>
      {/* 0. High-fidelity Route Path Polyline Highlight with Glow outline */}
      {showRouteLayer && routePath && routePath.length > 0 && (
        <>
          {/* Glow Shadow Outline */}
          <Polyline
            positions={routePath}
            pathOptions={{
              color: "#3b82f6",
              weight: 10,
              opacity: 0.35,
              lineCap: "round",
              lineJoin: "round"
            }}
          />
          {/* Core Route Line */}
          <Polyline
            positions={routePath}
            pathOptions={{
              color: "#1d4ed8",
              weight: 5,
              opacity: 0.95,
              lineCap: "round",
              lineJoin: "round"
            }}
          />

          {/* Start Marker */}
          <Marker
            position={routePath[0]}
            icon={createHtmlIcon("bg-emerald-500", "🏁", "Start", true)}
          />

          {/* Destination Marker */}
          <Marker
            position={routePath[routePath.length - 1]}
            icon={createHtmlIcon("bg-red-500", "📍", "Destination", true)}
          />
        </>
      )}

      {/* 1. Buildings Markers & Boundaries */}
      {showBuildings &&
        buildings.map((b) => {
          let colorClass = "bg-blue-500";
          let symbol = "🏫";
          if (b.category === "Residential") {
            colorClass = "bg-emerald-500";
            symbol = "🏠";
          } else if (b.category === "Administrative") {
            colorClass = "bg-purple-500";
            symbol = "🏛️";
          }

          const isHighlighted = getIsBuildingDestination(b._id);
          const icon = createHtmlIcon(colorClass, symbol, b.building_code, isHighlighted);

          return (
            <React.Fragment key={b._id}>
              {b.geometry && b.geometry.length > 1 && (
                <Polygon
                  positions={b.geometry}
                  pathOptions={{
                    color: isHighlighted ? "#ef4444" : "#94a3b8",
                    fillColor: isHighlighted ? "#ef4444" : "#cbd5e1",
                    fillOpacity: isHighlighted ? 0.15 : 0.05,
                    weight: isHighlighted ? 2.5 : 1,
                    dashArray: isHighlighted ? "3" : undefined
                  }}
                />
              )}
              <Marker
                position={[b.latitude, b.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => onEntityClick(b, "building"),
                  mouseover: () => onHoverEntity?.(b, "building"),
                  mouseout: () => onHoverEntity?.(null, null)
                }}
              >
                <Popup>
                  <div className="p-1 min-w-[140px]">
                    <p className="font-bold text-xs text-primary mb-0.5">{b.building_name}</p>
                    <p className="text-[10px] text-on-surface/77 line-clamp-2 leading-tight">{b.description}</p>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}

      {/* 2. Landmarks Markers & Boundaries */}
      {showLandmarks &&
        landmarks.map((l) => {
          const isHighlighted = selectedEntity && selectedEntity._id === l._id;
          const icon = createHtmlIcon("bg-amber-500", "📍", l.name, isHighlighted);

          return (
            <React.Fragment key={l._id}>
              {l.geometry && l.geometry.length > 1 && (
                <Polygon
                  positions={l.geometry}
                  pathOptions={{
                    color: isHighlighted ? "#f59e0b" : "#d97706",
                    fillColor: isHighlighted ? "#f59e0b" : "#d97706",
                    fillOpacity: isHighlighted ? 0.15 : 0.05,
                    weight: 1
                  }}
                />
              )}
              <Marker
                position={[l.latitude, l.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => onEntityClick(l, "landmark"),
                  mouseover: () => onHoverEntity?.(l, "landmark"),
                  mouseout: () => onHoverEntity?.(null, null)
                }}
              >
                <Popup>
                  <div className="p-1 min-w-[140px]">
                    <p className="font-bold text-xs text-amber-600 mb-0.5">{l.name}</p>
                    <p className="text-[10px] text-on-surface/77 line-clamp-2 leading-tight">{l.description}</p>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}

      {/* 3. Facilities Markers & Boundaries */}
      {showFacilities &&
        facilities.map((f) => {
          let symbol = "⚙️";
          if (f.category === "ATM") symbol = "💵";
          else if (f.category === "Cafeteria") symbol = "☕";
          else if (f.category === "Xerox") symbol = "📄";
          else if (f.category === "Medical Centre") symbol = "🏥";
          else if (f.category === "Bank") symbol = "🏦";

          const isHighlighted = selectedEntity && selectedEntity._id === f._id;
          const icon = createHtmlIcon("bg-orange-500", symbol, f.name, isHighlighted);

          return (
            <React.Fragment key={f._id}>
              {f.geometry && f.geometry.length > 1 && (
                <Polygon
                  positions={f.geometry}
                  pathOptions={{
                    color: isHighlighted ? "#f97316" : "#ea580c",
                    fillColor: isHighlighted ? "#f97316" : "#ea580c",
                    fillOpacity: isHighlighted ? 0.15 : 0.05,
                    weight: 1
                  }}
                />
              )}
              <Marker
                position={[f.latitude, f.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => onEntityClick(f, "facility"),
                  mouseover: () => onHoverEntity?.(f, "facility"),
                  mouseout: () => onHoverEntity?.(null, null)
                }}
              >
                <Popup>
                  <div className="p-1 min-w-[140px]">
                    <p className="font-bold text-xs text-orange-600 mb-0.5">{f.name}</p>
                    <p className="text-[10px] text-on-surface/75 font-semibold">🕒 {f.timing}</p>
                    <p className="text-[9px] text-on-surface/60 truncate mt-0.5">Services: {f.services.join(", ")}</p>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
    </>
  );
};
export default CampusMapLayer;
