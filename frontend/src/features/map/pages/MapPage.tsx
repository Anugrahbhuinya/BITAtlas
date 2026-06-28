import CampusMap from "../components/CampusMap";

export const MapPage = () => {
  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col p-6 min-h-0 bg-background select-none">
      <div className="flex-1 rounded-xl overflow-hidden border border-outline-variant">
        <CampusMap />
      </div>
    </div>
  );
};

export default MapPage;
