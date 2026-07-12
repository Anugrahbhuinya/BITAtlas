// src/features/navigation/pages/AdminNavigationPage.tsx

import React, { useState, useEffect } from "react";
import { 
  Map, Plus, Edit2, Trash2, Search, Filter, 
  MapPin, Landmark, Coffee, HelpCircle,
  ChevronLeft, ChevronRight, CheckCircle2, AlertCircle, Loader2, X
} from "lucide-react";
import adminApi from "../../admin/services/api";
import { LoadingState } from "../components/States";
import { GraphStatistics } from "../components/GraphStatistics";
import { ValidationPanel } from "../components/ValidationPanel";
import { GraphExplorer } from "../components/GraphExplorer";
import { navigationApi } from "../services/navigationApi";
import type { GraphSummary, GraphValidationReport, GraphNode } from "../types";
import { AdminDialog } from "../components/dialogs/AdminDialog";
import { DeleteConfirmDialog } from "../components/dialogs/DeleteConfirmDialog";
import {
  DialogSection,
  DialogFormGrid,
  DialogFormInput,
  DialogFooter,
  inputClasses,
  selectClasses,
  checkboxClasses
} from "../components/dialogs/DialogPrimitives";

// AdminGraphTab Subcomponent
const AdminGraphTab: React.FC = () => {
  const [subTab, setSubTab] = useState<"stats" | "explorer" | "validation">("stats");
  const [summary, setSummary] = useState<GraphSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [report, setReport] = useState<GraphValidationReport | null>(null);
  const [reportLoading, setReportLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [allNodes, setAllNodes] = useState<GraphNode[]>([]);

  const loadGraphData = async () => {
    setSummaryLoading(true);
    setReportLoading(true);
    try {
      const summaryData = await navigationApi.fetchGraphSummary();
      setSummary(summaryData);
      
      const validationData = await navigationApi.fetchGraphValidation();
      setReport(validationData);

      const nodesData = await navigationApi.fetchGraphNodes();
      setAllNodes(nodesData);
    } catch (err) {
      console.error("Failed to load graph data", err);
    } finally {
      setSummaryLoading(false);
      setReportLoading(false);
    }
  };

  useEffect(() => {
    loadGraphData();
  }, []);

  const handleRebuild = async () => {
    setRebuilding(true);
    try {
      const newSummary = await navigationApi.rebuildGraph();
      setSummary(newSummary);
      
      const validationData = await navigationApi.fetchGraphValidation();
      setReport(validationData);

      const nodesData = await navigationApi.fetchGraphNodes();
      setAllNodes(nodesData);
    } catch (err) {
      console.error("Failed to rebuild graph", err);
    } finally {
      setRebuilding(false);
    }
  };

  return (
    <div className="p-6 bg-surface border-t border-outline-variant/30 space-y-6">
      {/* Sub Tabs */}
      <div className="flex border-b border-outline-variant/30 mb-6 gap-2">
        {(["stats", "explorer", "validation"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSubTab(tab)}
            className={`px-4 py-2.5 text-xs font-bold capitalize border-b-2 transition duration-200 ${
              subTab === tab 
                ? "border-primary text-primary" 
                : "border-transparent text-on-surface/50 hover:text-on-surface/85"
            }`}
          >
            {tab === "stats" ? "Stats & Summary" : tab === "explorer" ? "Adjacency Explorer" : "Diagnostics & Validation"}
          </button>
        ))}
      </div>

      {subTab === "stats" && (
        <GraphStatistics
          summary={summary}
          loading={summaryLoading}
          onRebuild={handleRebuild}
          rebuilding={rebuilding}
          allNodes={allNodes}
        />
      )}

      {subTab === "explorer" && <GraphExplorer />}

      {subTab === "validation" && (
        <ValidationPanel
          report={report}
          loading={reportLoading}
        />
      )}
    </div>
  );
};

interface FormState {
  type: "building" | "room" | "facility" | "landmark" | "pathway";
  mode: "create" | "edit";
  id?: string;
}

export const AdminNavigationPage: React.FC = () => {
  // Navigation Tabs
  const [activeTab, setActiveTab] = useState<"buildings" | "rooms" | "facilities" | "landmarks" | "pathways" | "graph">("buildings");
  
  // Data Lists
  const [buildings, setBuildings] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [facilities, setFacilities] = useState<any[]>([]);
  const [landmarks, setLandmarks] = useState<any[]>([]);
  const [pathways, setPathways] = useState<any[]>([]);
  
  // Search and Pagination
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Modal / Form state
  const [formOpen, setFormOpen] = useState(false);
  const [formConfig, setFormConfig] = useState<FormState | null>(null);
  
  // Form Payload states
  const [buildingForm, setBuildingForm] = useState({
    building_code: "",
    building_name: "",
    description: "",
    category: "Academic",
    latitude: 23.4129,
    longitude: 85.4407,
    address: "",
    opening_hours: "09:00 - 17:00",
    contact: "",
    departments: "",
    floors: "0,1,2",
    wheelchair_accessible: true,
    has_elevator: false,
    has_ramp: true
  });

  const [roomForm, setRoomForm] = useState({
    room_number: "",
    room_name: "",
    building_id: "",
    floor: 0,
    room_type: "Classroom",
    capacity: 60,
    description: "",
    facilities: "AC, Projector, Whiteboard",
    department: ""
  });

  const [facilityForm, setFacilityForm] = useState({
    name: "",
    latitude: 23.4129,
    longitude: 85.4407,
    category: "Cafeteria",
    timing: "08:30 - 21:00",
    services: "Food, Beverages",
    wheelchair_accessible: true
  });

  const [landmarkForm, setLandmarkForm] = useState({
    name: "",
    latitude: 23.4129,
    longitude: 85.4407,
    category: "Lawn",
    description: ""
  });

  const [pathwayForm, setPathwayForm] = useState({
    start_id: "",
    start_type: "building",
    start_name: "",
    end_id: "",
    end_type: "building",
    end_name: "",
    path_type: "walkway",
    distance: 50.0,
    surface: "concrete",
    accessible: true,
    lighting: "moderate",
    notes: ""
  });

  // Action Loading & Notifications
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const showToast = (message: string, type: "success" | "error") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === "buildings") {
        const res = await adminApi.get(`/api/navigation/buildings?skip=${(page-1)*10}&limit=10&search=${search}`);
        setBuildings(res.data.buildings || []);
        setTotalPages(Math.ceil((res.data.total || 0) / 10));
      } else if (activeTab === "rooms") {
        const res = await adminApi.get(`/api/navigation/rooms?skip=${(page-1)*10}&limit=10&search=${search}`);
        setRooms(res.data.rooms || []);
        setTotalPages(Math.ceil((res.data.total || 0) / 10));
      } else if (activeTab === "facilities") {
        const res = await adminApi.get(`/api/navigation/facilities?skip=${(page-1)*10}&limit=10&search=${search}`);
        setFacilities(res.data.facilities || []);
        setTotalPages(Math.ceil((res.data.total || 0) / 10));
      } else if (activeTab === "landmarks") {
        const res = await adminApi.get(`/api/navigation/landmarks?skip=${(page-1)*10}&limit=10&search=${search}`);
        setLandmarks(res.data.landmarks || []);
        setTotalPages(Math.ceil((res.data.total || 0) / 10));
      } else if (activeTab === "pathways") {
        const res = await adminApi.get(`/api/navigation/pathways?skip=${(page-1)*10}&limit=10`);
        setPathways(res.data.pathways || []);
        setTotalPages(Math.ceil((res.data.total || 0) / 10));
      }
    } catch (err: any) {
      console.error(err);
      showToast("Failed to fetch navigation data registry", "error");
    } finally {
      setLoading(false);
    }
  };

  // Prefetch buildings list for select dropdowns
  const [allBuildings, setAllBuildings] = useState<any[]>([]);
  const [allLandmarks, setAllLandmarks] = useState<any[]>([]);
  const [allFacilities, setAllFacilities] = useState<any[]>([]);

  const fetchDropdownLists = async () => {
    try {
      const resB = await adminApi.get("/api/navigation/buildings?limit=100");
      setAllBuildings(resB.data.buildings || []);
      const resL = await adminApi.get("/api/navigation/landmarks?limit=100");
      setAllLandmarks(resL.data.landmarks || []);
      const resF = await adminApi.get("/api/navigation/facilities?limit=100");
      setAllFacilities(resF.data.facilities || []);
    } catch (e) {
      console.error("Failed to load drop list inputs", e);
    }
  };

  useEffect(() => {
    setPage(1);
    setSearch("");
  }, [activeTab]);

  useEffect(() => {
    fetchData();
  }, [activeTab, page]);

  useEffect(() => {
    fetchDropdownLists();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchData();
  };

  const handleEdit = (item: any, type: typeof activeTab) => {
    setFormErrors({});
    setFormConfig({ type: type as any, mode: "edit", id: item._id });
    
    if (type === "buildings") {
      setBuildingForm({
        building_code: item.building_code,
        building_name: item.building_name,
        description: item.description,
        category: item.category,
        latitude: item.latitude,
        longitude: item.longitude,
        address: item.address,
        opening_hours: item.opening_hours,
        contact: item.contact,
        departments: (item.departments || []).join(", "),
        floors: (item.floors || []).join(","),
        wheelchair_accessible: item.accessibility?.wheelchair_accessible ?? true,
        has_elevator: item.accessibility?.has_elevator ?? false,
        has_ramp: item.accessibility?.has_ramp ?? true
      });
    } else if (type === "rooms") {
      setRoomForm({
        room_number: item.room_number,
        room_name: item.room_name,
        building_id: item.building_id,
        floor: item.floor,
        room_type: item.room_type,
        capacity: item.capacity,
        description: item.description,
        facilities: (item.facilities || []).join(", "),
        department: item.department || ""
      });
    } else if (type === "facilities") {
      setFacilityForm({
        name: item.name,
        latitude: item.latitude,
        longitude: item.longitude,
        category: item.category,
        timing: item.timing,
        services: (item.services || []).join(", "),
        wheelchair_accessible: item.accessibility?.wheelchair_accessible ?? true
      });
    } else if (type === "landmarks") {
      setLandmarkForm({
        name: item.name,
        latitude: item.latitude,
        longitude: item.longitude,
        category: item.category,
        description: item.description
      });
    } else if (type === "pathways") {
      setPathwayForm({
        start_id: item.start_node.id,
        start_type: item.start_node.type,
        start_name: item.start_node.name,
        end_id: item.end_node.id,
        end_type: item.end_node.type,
        end_name: item.end_node.name,
        path_type: item.path_type,
        distance: item.distance,
        surface: item.surface,
        accessible: item.accessible,
        lighting: item.lighting,
        notes: item.notes
      });
    }
    setFormOpen(true);
  };

  const handleOpenCreate = () => {
    setFormErrors({});
    setFormConfig({ type: activeTab as any, mode: "create" });
    if (activeTab === "buildings") {
      setBuildingForm({
        building_code: "",
        building_name: "",
        description: "",
        category: "Academic",
        latitude: 23.4129,
        longitude: 85.4407,
        address: "",
        opening_hours: "09:00 - 17:00",
        contact: "",
        departments: "",
        floors: "0,1,2",
        wheelchair_accessible: true,
        has_elevator: false,
        has_ramp: true
      });
    } else if (activeTab === "rooms") {
      setRoomForm({
        room_number: "",
        room_name: "",
        building_id: allBuildings[0]?._id || "",
        floor: 0,
        room_type: "Classroom",
        capacity: 60,
        description: "",
        facilities: "AC, Projector, Whiteboard",
        department: ""
      });
    } else if (activeTab === "facilities") {
      setFacilityForm({
        name: "",
        latitude: 23.4129,
        longitude: 85.4407,
        category: "Cafeteria",
        timing: "08:30 - 21:00",
        services: "Food, Beverages",
        wheelchair_accessible: true
      });
    } else if (activeTab === "landmarks") {
      setLandmarkForm({
        name: "",
        latitude: 23.4129,
        longitude: 85.4407,
        category: "Lawn",
        description: ""
      });
    } else if (activeTab === "pathways") {
      setPathwayForm({
        start_id: "",
        start_type: "building",
        start_name: "",
        end_id: "",
        end_type: "building",
        end_name: "",
        path_type: "walkway",
        distance: 50.0,
        surface: "concrete",
        accessible: true,
        lighting: "moderate",
        notes: ""
      });
    }
    setFormOpen(true);
  };

  const handleDeleteClick = (id: string) => {
    setDeleteId(id);
    setDeleteConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deleteId) return;
    setActionLoading(true);
    try {
      await adminApi.delete(`/api/navigation/${activeTab}/${deleteId}`);
      showToast("Item deleted successfully", "success");
      setDeleteConfirmOpen(false);
      setDeleteId(null);
      fetchData();
      fetchDropdownLists();
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Deletion failed", "error");
    } finally {
      setActionLoading(false);
    }
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    const type = formConfig?.type;
    
    if (type === "building") {
      if (!buildingForm.building_code.trim()) errors.building_code = "Building code is required.";
      if (!buildingForm.building_name.trim()) errors.building_name = "Building name is required.";
      if (buildingForm.latitude === 0 || isNaN(buildingForm.latitude)) errors.latitude = "Valid latitude coordinate is required.";
      if (buildingForm.longitude === 0 || isNaN(buildingForm.longitude)) errors.longitude = "Valid longitude coordinate is required.";
    } else if (type === "room") {
      if (!roomForm.room_number.trim()) errors.room_number = "Room number is required.";
      if (!roomForm.room_name.trim()) errors.room_name = "Room name is required.";
      if (!roomForm.building_id) errors.building_id = "Please select a parent building.";
    } else if (type === "facility") {
      if (!facilityForm.name.trim()) errors.name = "Facility name is required.";
      if (facilityForm.latitude === 0 || isNaN(facilityForm.latitude)) errors.latitude = "Valid latitude coordinate is required.";
      if (facilityForm.longitude === 0 || isNaN(facilityForm.longitude)) errors.longitude = "Valid longitude coordinate is required.";
    } else if (type === "landmark") {
      if (!landmarkForm.name.trim()) errors.name = "Landmark name is required.";
      if (landmarkForm.latitude === 0 || isNaN(landmarkForm.latitude)) errors.latitude = "Valid latitude coordinate is required.";
      if (landmarkForm.longitude === 0 || isNaN(landmarkForm.longitude)) errors.longitude = "Valid longitude coordinate is required.";
    } else if (type === "pathway") {
      if (!pathwayForm.start_id) errors.start_id = "Start location selection is required.";
      if (!pathwayForm.end_id) errors.end_id = "End location selection is required.";
      if (pathwayForm.distance <= 0 || isNaN(pathwayForm.distance)) errors.distance = "Distance must be greater than 0.";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formConfig) return;
    if (!validateForm()) return;
    
    setActionLoading(true);
    try {
      const type = formConfig.type;
      const isEdit = formConfig.mode === "edit";
      const id = formConfig.id;
      
      let payload: any = {};
      
      if (type === "building") {
        payload = {
          ...buildingForm,
          latitude: Number(buildingForm.latitude),
          longitude: Number(buildingForm.longitude),
          departments: buildingForm.departments.split(",").map(d => d.trim()).filter(Boolean),
          floors: buildingForm.floors.split(",").map(f => parseInt(f.trim())).filter(f => !isNaN(f)),
          accessibility: {
            wheelchair_accessible: buildingForm.wheelchair_accessible,
            has_elevator: buildingForm.has_elevator,
            has_ramp: buildingForm.has_ramp
          },
          entrances: [
            { name: "Main Entrance", latitude: Number(buildingForm.latitude), longitude: Number(buildingForm.longitude) }
          ]
        };
      } else if (type === "room") {
        payload = {
          ...roomForm,
          floor: Number(roomForm.floor),
          capacity: Number(roomForm.capacity),
          facilities: roomForm.facilities.split(",").map(f => f.trim()).filter(Boolean),
          department: roomForm.department.trim() || null
        };
      } else if (type === "facility") {
        payload = {
          ...facilityForm,
          latitude: Number(facilityForm.latitude),
          longitude: Number(facilityForm.longitude),
          services: facilityForm.services.split(",").map(s => s.trim()).filter(Boolean),
          accessibility: {
            wheelchair_accessible: facilityForm.wheelchair_accessible
          }
        };
      } else if (type === "landmark") {
        payload = {
          ...landmarkForm,
          latitude: Number(landmarkForm.latitude),
          longitude: Number(landmarkForm.longitude)
        };
      } else if (type === "pathway") {
        // Find names based on ID selection for start/end nodes
        const startName = findNodeName(pathwayForm.start_id, pathwayForm.start_type);
        const endName = findNodeName(pathwayForm.end_id, pathwayForm.end_type);
        
        payload = {
          start_node: {
            id: pathwayForm.start_id,
            type: pathwayForm.start_type,
            name: startName
          },
          end_node: {
            id: pathwayForm.end_id,
            type: pathwayForm.end_type,
            name: endName
          },
          path_type: pathwayForm.path_type,
          distance: Number(pathwayForm.distance),
          surface: pathwayForm.surface,
          accessible: pathwayForm.accessible,
          lighting: pathwayForm.lighting,
          notes: pathwayForm.notes
        };
      }

      if (isEdit && id) {
        await adminApi.put(`/api/navigation/${type}/${id}`, payload);
        showToast("Item updated successfully", "success");
      } else {
        await adminApi.post(`/api/navigation/${type}`, payload);
        showToast("Item created successfully", "success");
      }
      
      setFormOpen(false);
      fetchData();
      fetchDropdownLists();
    } catch (err: any) {
      showToast(err.response?.data?.detail || "Action failed", "error");
    } finally {
      setActionLoading(false);
    }
  };

  const findNodeName = (id: string, type: string) => {
    if (type === "building") return allBuildings.find(b => b._id === id)?.building_name || "Building";
    if (type === "landmark") return allLandmarks.find(l => l._id === id)?.name || "Landmark";
    if (type === "facility") return allFacilities.find(f => f._id === id)?.name || "Facility";
    return "Campus Location";
  };

  return (
    <div className="p-6 bg-background space-y-6 min-h-screen text-on-surface font-sans">
      
      {/* Toast Alert */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-xl border backdrop-blur-lg shadow-2xl transition-all duration-300 ${
          toast.type === "success" 
            ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-500" 
            : "border-error/20 bg-error/10 text-error"
        }`}>
          {toast.type === "success" ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          <span className="text-sm font-semibold">{toast.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2.5">
            <Map className="w-7 h-7 text-primary" />
            Campus Navigation Registry
          </h1>
          <p className="text-xs text-on-surface/60 mt-1">
            Build and manage the spatial datastore of BIT Mesra campus buildings, offices, POIs, and walkways.
          </p>
        </div>
        <button
          onClick={handleOpenCreate}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary text-background rounded-xl text-sm font-bold shadow-lg hover:bg-primary/95 hover:scale-[1.01] active:scale-[0.99] transition duration-200"
        >
          <Plus className="w-4 h-4" />
          Add Location Entity
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-outline-variant/60">
        {(["buildings", "rooms", "facilities", "landmarks", "pathways"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-3 text-sm font-bold capitalize border-b-2 transition duration-200 ${
              activeTab === tab 
                ? "border-primary text-primary" 
                : "border-transparent text-on-surface/50 hover:text-on-surface/85"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Search Filter bar */}
      {activeTab !== "pathways" && activeTab !== "graph" && (
        <form onSubmit={handleSearchSubmit} className="flex gap-2.5 max-w-md">
          <div className="relative flex-1 flex items-center bg-surface/40 border border-outline-variant/60 rounded-xl px-3.5 py-2">
            <Search className="w-4 h-4 text-on-surface/50 mr-2" />
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-transparent text-sm text-on-surface focus:outline-none flex-1"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-surface-variant text-on-surface text-sm font-bold rounded-xl border border-outline-variant/60 hover:bg-surface-variant/80 transition"
          >
            Search
          </button>
        </form>
      )}

      {/* Data Table / Graph tab */}
      {activeTab === "graph" ? (
        <AdminGraphTab />
      ) : loading ? (
        <LoadingState message={`Fetching registered ${activeTab} data...`} />
      ) : (
        <div className="border border-outline-variant/60 rounded-2xl bg-surface/30 backdrop-blur-md overflow-hidden">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-surface-variant/40 border-b border-outline-variant/60 text-xs uppercase font-bold tracking-wider text-on-surface/65">
                {activeTab === "buildings" && (
                  <>
                    <th className="p-4 font-bold">Code</th>
                    <th className="p-4 font-bold">Name</th>
                    <th className="p-4 font-bold">Category</th>
                    <th className="p-4 font-bold">Floors</th>
                    <th className="p-4 font-bold">Hours</th>
                    <th className="p-4 font-bold">Actions</th>
                  </>
                )}
                {activeTab === "rooms" && (
                  <>
                    <th className="p-4 font-bold">Room #</th>
                    <th className="p-4 font-bold">Name</th>
                    <th className="p-4 font-bold">Type</th>
                    <th className="p-4 font-bold">Capacity</th>
                    <th className="p-4 font-bold">Floor</th>
                    <th className="p-4 font-bold">Actions</th>
                  </>
                )}
                {activeTab === "facilities" && (
                  <>
                    <th className="p-4 font-bold">Name</th>
                    <th className="p-4 font-bold">Category</th>
                    <th className="p-4 font-bold">Timings</th>
                    <th className="p-4 font-bold">Services</th>
                    <th className="p-4 font-bold">Actions</th>
                  </>
                )}
                {activeTab === "landmarks" && (
                  <>
                    <th className="p-4 font-bold">Name</th>
                    <th className="p-4 font-bold">Category</th>
                    <th className="p-4 font-bold">Coordinates</th>
                    <th className="p-4 font-bold">Description</th>
                    <th className="p-4 font-bold">Actions</th>
                  </>
                )}
                {activeTab === "pathways" && (
                  <>
                    <th className="p-4 font-bold">Start Node</th>
                    <th className="p-4 font-bold">End Node</th>
                    <th className="p-4 font-bold">Distance</th>
                    <th className="p-4 font-bold">Surface</th>
                    <th className="p-4 font-bold">Lighting</th>
                    <th className="p-4 font-bold">Actions</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {activeTab === "buildings" && buildings.map((item) => (
                <tr key={item._id} className="border-b border-outline-variant/35 hover:bg-surface-variant/20 transition">
                  <td className="p-4 font-mono font-bold text-xs text-primary">{item.building_code}</td>
                  <td className="p-4 font-bold">{item.building_name}</td>
                  <td className="p-4 text-xs">{item.category}</td>
                  <td className="p-4 text-xs">{item.floors.join(",")}</td>
                  <td className="p-4 text-xs">{item.opening_hours}</td>
                  <td className="p-4 flex gap-2.5">
                    <button onClick={() => handleEdit(item, "buildings")} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-primary transition">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDeleteClick(item._id)} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-error transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {activeTab === "rooms" && rooms.map((item) => (
                <tr key={item._id} className="border-b border-outline-variant/35 hover:bg-surface-variant/20 transition">
                  <td className="p-4 font-mono font-bold text-xs">{item.room_number}</td>
                  <td className="p-4">{item.room_name}</td>
                  <td className="p-4 text-xs">{item.room_type}</td>
                  <td className="p-4 text-xs">{item.capacity}</td>
                  <td className="p-4 text-xs">{item.floor}</td>
                  <td className="p-4 flex gap-2.5">
                    <button onClick={() => handleEdit(item, "rooms")} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-primary transition">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDeleteClick(item._id)} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-error transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {activeTab === "facilities" && facilities.map((item) => (
                <tr key={item._id} className="border-b border-outline-variant/35 hover:bg-surface-variant/20 transition">
                  <td className="p-4 font-bold">{item.name}</td>
                  <td className="p-4 text-xs">{item.category}</td>
                  <td className="p-4 text-xs">{item.timing}</td>
                  <td className="p-4 text-xs max-w-xs truncate">{item.services.join(", ")}</td>
                  <td className="p-4 flex gap-2.5">
                    <button onClick={() => handleEdit(item, "facilities")} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-primary transition">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDeleteClick(item._id)} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-error transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {activeTab === "landmarks" && landmarks.map((item) => (
                <tr key={item._id} className="border-b border-outline-variant/35 hover:bg-surface-variant/20 transition">
                  <td className="p-4 font-bold">{item.name}</td>
                  <td className="p-4 text-xs">{item.category}</td>
                  <td className="p-4 font-mono text-xs">[{item.latitude.toFixed(4)}, {item.longitude.toFixed(4)}]</td>
                  <td className="p-4 text-xs max-w-xs truncate">{item.description}</td>
                  <td className="p-4 flex gap-2.5">
                    <button onClick={() => handleEdit(item, "landmarks")} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-primary transition">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDeleteClick(item._id)} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-error transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {activeTab === "pathways" && pathways.map((item) => (
                <tr key={item._id} className="border-b border-outline-variant/35 hover:bg-surface-variant/20 transition">
                  <td className="p-4 text-xs">
                    <span className="font-bold">{item.start_node.name}</span>
                    <span className="text-[10px] block opacity-60 capitalize">({item.start_node.type})</span>
                  </td>
                  <td className="p-4 text-xs">
                    <span className="font-bold">{item.end_node.name}</span>
                    <span className="text-[10px] block opacity-60 capitalize">({item.end_node.type})</span>
                  </td>
                  <td className="p-4 text-xs">{item.distance}m</td>
                  <td className="p-4 text-xs capitalize">{item.surface}</td>
                  <td className="p-4 text-xs capitalize">{item.lighting}</td>
                  <td className="p-4 flex gap-2.5">
                    <button onClick={() => handleEdit(item, "pathways")} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-primary transition">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDeleteClick(item._id)} className="p-1.5 rounded hover:bg-surface-variant text-on-surface/75 hover:text-error transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {((activeTab === "buildings" && buildings.length === 0) ||
                (activeTab === "rooms" && rooms.length === 0) ||
                (activeTab === "facilities" && facilities.length === 0) ||
                (activeTab === "landmarks" && landmarks.length === 0) ||
                (activeTab === "pathways" && pathways.length === 0)) && (
                <tr>
                  <td colSpan={6} className="p-12 text-center">
                    <div className="flex flex-col items-center justify-center space-y-3.5 py-6">
                      <div className="p-4 bg-surface-variant/40 rounded-full text-on-surface/30">
                        <Map className="w-10 h-10" />
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm font-bold text-on-surface/75">No Location Data Found</p>
                        <p className="text-xs text-on-surface/50 max-w-sm leading-normal">
                          There are no registered campus records in the "{activeTab}" category yet. Create a new location to build your campus spatial datastore.
                        </p>
                      </div>
                      <button
                        onClick={handleOpenCreate}
                        className="px-4 py-2 bg-primary text-background text-xs font-bold rounded-xl shadow hover:bg-primary/90 transition duration-200"
                      >
                        Add First Record
                      </button>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          
          {/* Pagination Footer */}
          {totalPages > 1 && (
            <div className="flex justify-between items-center px-4 py-3 bg-surface-variant/10 border-t border-outline-variant/40">
              <span className="text-xs text-on-surface/60">Page {page} of {totalPages}</span>
              <div className="flex gap-2">
                <button
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                  className="p-1 rounded bg-surface hover:bg-surface-variant border border-outline-variant/60 disabled:opacity-30 disabled:pointer-events-none transition"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={page === totalPages}
                  onClick={() => setPage(p => p + 1)}
                  className="p-1 rounded bg-surface hover:bg-surface-variant border border-outline-variant/60 disabled:opacity-30 disabled:pointer-events-none transition"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* DELETE DIALOG */}
      <DeleteConfirmDialog
        isOpen={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleConfirmDelete}
        title="Delete Location Record"
        description="Are you sure you want to remove this navigation record? This operation is permanent and will delete this location."
        loading={actionLoading}
      />

      {/* CREATE / EDIT MODAL FORM */}
      <AdminDialog
        isOpen={formOpen}
        onClose={() => setFormOpen(false)}
        title={formConfig ? `${formConfig.mode === "create" ? "Add New" : "Edit"} ${formConfig.type}` : ""}
        description={formConfig ? `Fill in details for this ${formConfig.type} entity below.` : ""}
        icon={formConfig ? (
          formConfig.type === "building" ? <MapPin className="w-6 h-6" /> :
          formConfig.type === "room" ? <HelpCircle className="w-6 h-6" /> :
          formConfig.type === "facility" ? <Coffee className="w-6 h-6" /> :
          formConfig.type === "landmark" ? <Landmark className="w-6 h-6" /> :
          <Map className="w-6 h-6" />
        ) : undefined}
        size="lg"
        closeOnOutsideClick={!actionLoading}
      >
        {formConfig && (
          <form onSubmit={handleFormSubmit} className="space-y-6">
            {formConfig.type === "building" && (
              <>
                <DialogSection title="General Information" description="Set code identifier, name, and visual category.">
                  <DialogFormGrid>
                    <DialogFormInput label="Building Code" required error={formErrors.building_code} helperText="Unique short code (e.g. CSE, MAIN, MECH)">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={buildingForm.building_code}
                        onChange={(e) => setBuildingForm({ ...buildingForm, building_code: e.target.value })}
                        className={inputClasses(!!formErrors.building_code)}
                        placeholder="e.g. CSE"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Building Name" required error={formErrors.building_name}>
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={buildingForm.building_name}
                        onChange={(e) => setBuildingForm({ ...buildingForm, building_name: e.target.value })}
                        className={inputClasses(!!formErrors.building_name)}
                        placeholder="e.g. Computer Science Department"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormGrid>
                    <DialogFormInput label="Category">
                      <select
                        disabled={actionLoading}
                        value={buildingForm.category}
                        onChange={(e) => setBuildingForm({ ...buildingForm, category: e.target.value })}
                        className={selectClasses()}
                      >
                        <option value="Academic">Academic</option>
                        <option value="Administrative">Administrative</option>
                        <option value="Residential">Residential</option>
                        <option value="Student Services">Student Services</option>
                        <option value="Sports">Sports</option>
                        <option value="Research">Research</option>
                        <option value="Other">Other</option>
                      </select>
                    </DialogFormInput>
                    <DialogFormInput label="Floors" helperText="Comma-separated levels (e.g., 0,1,2,3)">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={buildingForm.floors}
                        onChange={(e) => setBuildingForm({ ...buildingForm, floors: e.target.value })}
                        className={inputClasses()}
                        placeholder="0,1,2"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormInput label="Description">
                    <textarea
                      disabled={actionLoading}
                      value={buildingForm.description}
                      onChange={(e) => setBuildingForm({ ...buildingForm, description: e.target.value })}
                      className={`${inputClasses()} h-20 resize-none`}
                      placeholder="Brief details about the departments housed here..."
                    />
                  </DialogFormInput>
                </DialogSection>

                <DialogSection title="Location & Timing" description="Map coordinates, address, and opening schedule.">
                  <DialogFormGrid>
                    <DialogFormInput label="Latitude" required error={formErrors.latitude}>
                      <input
                        type="number"
                        step="0.000001"
                        disabled={actionLoading}
                        value={buildingForm.latitude}
                        onChange={(e) => setBuildingForm({ ...buildingForm, latitude: Number(e.target.value) })}
                        className={inputClasses(!!formErrors.latitude)}
                        placeholder="23.4129"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Longitude" required error={formErrors.longitude}>
                      <input
                        type="number"
                        step="0.000001"
                        disabled={actionLoading}
                        value={buildingForm.longitude}
                        onChange={(e) => setBuildingForm({ ...buildingForm, longitude: Number(e.target.value) })}
                        className={inputClasses(!!formErrors.longitude)}
                        placeholder="85.4407"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormGrid>
                    <DialogFormInput label="Address" helperText="Street description or campus zone">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={buildingForm.address}
                        onChange={(e) => setBuildingForm({ ...buildingForm, address: e.target.value })}
                        className={inputClasses()}
                        placeholder="e.g. Near Clock Tower Plaza"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Opening Hours" helperText="Format: HH:MM - HH:MM">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={buildingForm.opening_hours}
                        onChange={(e) => setBuildingForm({ ...buildingForm, opening_hours: e.target.value })}
                        className={inputClasses()}
                        placeholder="09:00 - 17:00"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                </DialogSection>

                <DialogSection title="Contact & Accessibility" description="Phone contacts and handicap access flags.">
                  <DialogFormGrid>
                    <DialogFormInput label="Contact Number">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={buildingForm.contact}
                        onChange={(e) => setBuildingForm({ ...buildingForm, contact: e.target.value })}
                        className={inputClasses()}
                        placeholder="e.g. +91 651 2275444"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Departments" helperText="Comma-separated names">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={buildingForm.departments}
                        onChange={(e) => setBuildingForm({ ...buildingForm, departments: e.target.value })}
                        className={inputClasses()}
                        placeholder="CSE, ECE, EEE"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <div className="flex flex-wrap gap-4 pt-2">
                    <label className="flex items-center gap-2 font-bold cursor-pointer text-xs">
                      <input
                        type="checkbox"
                        disabled={actionLoading}
                        checked={buildingForm.wheelchair_accessible}
                        onChange={(e) => setBuildingForm({ ...buildingForm, wheelchair_accessible: e.target.checked })}
                        className={checkboxClasses}
                      />
                      Wheelchair Accessible
                    </label>
                    <label className="flex items-center gap-2 font-bold cursor-pointer text-xs">
                      <input
                        type="checkbox"
                        disabled={actionLoading}
                        checked={buildingForm.has_elevator}
                        onChange={(e) => setBuildingForm({ ...buildingForm, has_elevator: e.target.checked })}
                        className={checkboxClasses}
                      />
                      Has Elevator
                    </label>
                    <label className="flex items-center gap-2 font-bold cursor-pointer text-xs">
                      <input
                        type="checkbox"
                        disabled={actionLoading}
                        checked={buildingForm.has_ramp}
                        onChange={(e) => setBuildingForm({ ...buildingForm, has_ramp: e.target.checked })}
                        className={checkboxClasses}
                      />
                      Has Ramp
                    </label>
                  </div>
                </DialogSection>
              </>
            )}

            {formConfig.type === "room" && (
              <>
                <DialogSection title="General Information" description="Set number label, name, type, and capacity.">
                  <DialogFormGrid>
                    <DialogFormInput label="Room Number / Identifier" required error={formErrors.room_number}>
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={roomForm.room_number}
                        onChange={(e) => setRoomForm({ ...roomForm, room_number: e.target.value })}
                        className={inputClasses(!!formErrors.room_number)}
                        placeholder="e.g. 201"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Room Name" required error={formErrors.room_name}>
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={roomForm.room_name}
                        onChange={(e) => setRoomForm({ ...roomForm, room_name: e.target.value })}
                        className={inputClasses(!!formErrors.room_name)}
                        placeholder="e.g. CSE Seminar Hall"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormGrid>
                    <DialogFormInput label="Room Type">
                      <select
                        disabled={actionLoading}
                        value={roomForm.room_type}
                        onChange={(e) => setRoomForm({ ...roomForm, room_type: e.target.value })}
                        className={selectClasses()}
                      >
                        <option value="Classroom">Classroom</option>
                        <option value="Lab">Lab</option>
                        <option value="Seminar Hall">Seminar Hall</option>
                        <option value="Office">Office</option>
                        <option value="Restroom">Restroom</option>
                        <option value="Common Room">Common Room</option>
                        <option value="Auditorium">Auditorium</option>
                        <option value="Other">Other</option>
                      </select>
                    </DialogFormInput>
                    <DialogFormInput label="Student Capacity">
                      <input
                        type="number"
                        disabled={actionLoading}
                        value={roomForm.capacity}
                        onChange={(e) => setRoomForm({ ...roomForm, capacity: Number(e.target.value) })}
                        className={inputClasses()}
                        placeholder="60"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormInput label="Description">
                    <textarea
                      disabled={actionLoading}
                      value={roomForm.description}
                      onChange={(e) => setRoomForm({ ...roomForm, description: e.target.value })}
                      className={`${inputClasses()} h-20 resize-none`}
                      placeholder="List purposes or access restrictions..."
                    />
                  </DialogFormInput>
                </DialogSection>

                <DialogSection title="Building & Floor Layout" description="Link to building and specify department.">
                  <DialogFormGrid>
                    <DialogFormInput label="Parent Building" required error={formErrors.building_id}>
                      <select
                        disabled={actionLoading}
                        value={roomForm.building_id}
                        onChange={(e) => setRoomForm({ ...roomForm, building_id: e.target.value })}
                        className={selectClasses(!!formErrors.building_id)}
                      >
                        <option value="">-- Select Parent Building --</option>
                        {allBuildings.map((b) => (
                          <option key={b._id} value={b._id}>
                            {b.building_name} ({b.building_code})
                          </option>
                        ))}
                      </select>
                    </DialogFormInput>
                    <DialogFormInput label="Floor Level" helperText="0 = Ground, 1 = First, etc.">
                      <input
                        type="number"
                        disabled={actionLoading}
                        value={roomForm.floor}
                        onChange={(e) => setRoomForm({ ...roomForm, floor: Number(e.target.value) })}
                        className={inputClasses()}
                        placeholder="0"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormInput label="Department Offset" helperText="Specify if tied to a particular branch">
                    <input
                      type="text"
                      disabled={actionLoading}
                      value={roomForm.department}
                      onChange={(e) => setRoomForm({ ...roomForm, department: e.target.value })}
                      className={inputClasses()}
                      placeholder="e.g. Computer Science"
                    />
                  </DialogFormInput>
                </DialogSection>

                <DialogSection title="Amenities & Equipment" description="Specify technical features.">
                  <DialogFormInput label="Facilities & Tools" helperText="Comma-separated equipment tags">
                    <input
                      type="text"
                      disabled={actionLoading}
                      value={roomForm.facilities}
                      onChange={(e) => setRoomForm({ ...roomForm, facilities: e.target.value })}
                      className={inputClasses()}
                      placeholder="Projector, Wi-Fi, AC, Smart Board, Sound System"
                    />
                  </DialogFormInput>
                </DialogSection>
              </>
            )}

            {formConfig.type === "facility" && (
              <>
                <DialogSection title="General Information" description="Set commercial/utility name and timings.">
                  <DialogFormGrid>
                    <DialogFormInput label="Facility Name" required error={formErrors.name}>
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={facilityForm.name}
                        onChange={(e) => setFacilityForm({ ...facilityForm, name: e.target.value })}
                        className={inputClasses(!!formErrors.name)}
                        placeholder="e.g. Central Library Xerox"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Category">
                      <select
                        disabled={actionLoading}
                        value={facilityForm.category}
                        onChange={(e) => setFacilityForm({ ...facilityForm, category: e.target.value })}
                        className={selectClasses()}
                      >
                        <option value="Xerox Shop">Xerox Shop</option>
                        <option value="ATM">ATM</option>
                        <option value="Cafeteria">Cafeteria</option>
                        <option value="Stationery">Stationery</option>
                        <option value="Medical Unit">Medical Unit</option>
                        <option value="Post Office">Post Office</option>
                        <option value="Bank">Bank</option>
                        <option value="Parking">Parking</option>
                        <option value="Bus Stop">Bus Stop</option>
                        <option value="Other">Other</option>
                      </select>
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormInput label="Operating Timings" helperText="Format: Opening - Closing details">
                    <input
                      type="text"
                      disabled={actionLoading}
                      value={facilityForm.timing}
                      onChange={(e) => setFacilityForm({ ...facilityForm, timing: e.target.value })}
                      className={inputClasses()}
                      placeholder="e.g. 08:30 AM - 08:00 PM"
                    />
                  </DialogFormInput>
                </DialogSection>

                <DialogSection title="Location Coordinates" description="Specify latitude and longitude values on campus.">
                  <DialogFormGrid>
                    <DialogFormInput label="Latitude" required error={formErrors.latitude}>
                      <input
                        type="number"
                        step="0.000001"
                        disabled={actionLoading}
                        value={facilityForm.latitude}
                        onChange={(e) => setFacilityForm({ ...facilityForm, latitude: Number(e.target.value) })}
                        className={inputClasses(!!formErrors.latitude)}
                        placeholder="23.4129"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Longitude" required error={formErrors.longitude}>
                      <input
                        type="number"
                        step="0.000001"
                        disabled={actionLoading}
                        value={facilityForm.longitude}
                        onChange={(e) => setFacilityForm({ ...facilityForm, longitude: Number(e.target.value) })}
                        className={inputClasses(!!formErrors.longitude)}
                        placeholder="85.4407"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                </DialogSection>

                <DialogSection title="Services & Access" description="Service offerings and accessibility.">
                  <DialogFormInput label="Services Provided" helperText="Comma-separated services list">
                    <input
                      type="text"
                      disabled={actionLoading}
                      value={facilityForm.services}
                      onChange={(e) => setFacilityForm({ ...facilityForm, services: e.target.value })}
                      className={inputClasses()}
                      placeholder="Xerox, Binding, Laminating, Printing"
                    />
                  </DialogFormInput>
                  <label className="flex items-center gap-2 font-bold cursor-pointer text-xs pt-2">
                    <input
                      type="checkbox"
                      disabled={actionLoading}
                      checked={facilityForm.wheelchair_accessible}
                      onChange={(e) => setFacilityForm({ ...facilityForm, wheelchair_accessible: e.target.checked })}
                      className={checkboxClasses}
                    />
                    Wheelchair Accessible Facility
                  </label>
                </DialogSection>
              </>
            )}

            {formConfig.type === "landmark" && (
              <>
                <DialogSection title="General Information" description="Label name, category and descriptive details.">
                  <DialogFormGrid>
                    <DialogFormInput label="Landmark Name" required error={formErrors.name}>
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={landmarkForm.name}
                        onChange={(e) => setLandmarkForm({ ...landmarkForm, name: e.target.value })}
                        className={inputClasses(!!formErrors.name)}
                        placeholder="e.g. Clock Tower Plaza"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Category">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={landmarkForm.category}
                        onChange={(e) => setLandmarkForm({ ...landmarkForm, category: e.target.value })}
                        className={inputClasses()}
                        placeholder="e.g. Lawn, Garden, Monument"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormInput label="Description">
                    <textarea
                      disabled={actionLoading}
                      value={landmarkForm.description}
                      onChange={(e) => setLandmarkForm({ ...landmarkForm, description: e.target.value })}
                      className={`${inputClasses()} h-20 resize-none`}
                      placeholder="Detail the landmark POI history or layout..."
                    />
                  </DialogFormInput>
                </DialogSection>

                <DialogSection title="Map Coordinates" description="Coordinates for geographical pins on map layers.">
                  <DialogFormGrid>
                    <DialogFormInput label="Latitude" required error={formErrors.latitude}>
                      <input
                        type="number"
                        step="0.000001"
                        disabled={actionLoading}
                        value={landmarkForm.latitude}
                        onChange={(e) => setLandmarkForm({ ...landmarkForm, latitude: Number(e.target.value) })}
                        className={inputClasses(!!formErrors.latitude)}
                        placeholder="23.4129"
                      />
                    </DialogFormInput>
                    <DialogFormInput label="Longitude" required error={formErrors.longitude}>
                      <input
                        type="number"
                        step="0.000001"
                        disabled={actionLoading}
                        value={landmarkForm.longitude}
                        onChange={(e) => setLandmarkForm({ ...landmarkForm, longitude: Number(e.target.value) })}
                        className={inputClasses(!!formErrors.longitude)}
                        placeholder="85.4407"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                </DialogSection>
              </>
            )}

            {formConfig.type === "pathway" && (
              <>
                <DialogSection title="Start Connection Node" description="Establish the starting junction link.">
                  <DialogFormGrid>
                    <DialogFormInput label="Start Node Type">
                      <select
                        disabled={actionLoading}
                        value={pathwayForm.start_type}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, start_type: e.target.value, start_id: "" })}
                        className={selectClasses()}
                      >
                        <option value="building">Building</option>
                        <option value="landmark">Landmark</option>
                        <option value="facility">Facility</option>
                      </select>
                    </DialogFormInput>
                    <DialogFormInput label="Start Location" required error={formErrors.start_id}>
                      <select
                        disabled={actionLoading}
                        value={pathwayForm.start_id}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, start_id: e.target.value })}
                        className={selectClasses(!!formErrors.start_id)}
                      >
                        <option value="">-- Select Location --</option>
                        {pathwayForm.start_type === "building" && allBuildings.map(b => <option key={b._id} value={b._id}>{b.building_name}</option>)}
                        {pathwayForm.start_type === "landmark" && allLandmarks.map(l => <option key={l._id} value={l._id}>{l.name}</option>)}
                        {pathwayForm.start_type === "facility" && allFacilities.map(f => <option key={f._id} value={f._id}>{f.name}</option>)}
                      </select>
                    </DialogFormInput>
                  </DialogFormGrid>
                </DialogSection>

                <DialogSection title="End Connection Node" description="Establish the terminal destination junction link.">
                  <DialogFormGrid>
                    <DialogFormInput label="End Node Type">
                      <select
                        disabled={actionLoading}
                        value={pathwayForm.end_type}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, end_type: e.target.value, end_id: "" })}
                        className={selectClasses()}
                      >
                        <option value="building">Building</option>
                        <option value="landmark">Landmark</option>
                        <option value="facility">Facility</option>
                      </select>
                    </DialogFormInput>
                    <DialogFormInput label="End Location" required error={formErrors.end_id}>
                      <select
                        disabled={actionLoading}
                        value={pathwayForm.end_id}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, end_id: e.target.value })}
                        className={selectClasses(!!formErrors.end_id)}
                      >
                        <option value="">-- Select Location --</option>
                        {pathwayForm.end_type === "building" && allBuildings.map(b => <option key={b._id} value={b._id}>{b.building_name}</option>)}
                        {pathwayForm.end_type === "landmark" && allLandmarks.map(l => <option key={l._id} value={l._id}>{l.name}</option>)}
                        {pathwayForm.end_type === "facility" && allFacilities.map(f => <option key={f._id} value={f._id}>{f.name}</option>)}
                      </select>
                    </DialogFormInput>
                  </DialogFormGrid>
                </DialogSection>

                <DialogSection title="Path Characteristics" description="Define walkways parameters and accessibility.">
                  <DialogFormGrid>
                    <DialogFormInput label="Path Type">
                      <select
                        disabled={actionLoading}
                        value={pathwayForm.path_type}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, path_type: e.target.value })}
                        className={selectClasses()}
                      >
                        <option value="walkway">Walkway</option>
                        <option value="corridor">Corridor</option>
                        <option value="road">Road</option>
                        <option value="staircase">Staircase</option>
                        <option value="elevator">Elevator</option>
                      </select>
                    </DialogFormInput>
                    <DialogFormInput label="Distance (Meters)" required error={formErrors.distance}>
                      <input
                        type="number"
                        step="0.1"
                        disabled={actionLoading}
                        value={pathwayForm.distance}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, distance: Number(e.target.value) })}
                        className={inputClasses(!!formErrors.distance)}
                        placeholder="50"
                      />
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormGrid>
                    <DialogFormInput label="Surface Material">
                      <select
                        disabled={actionLoading}
                        value={pathwayForm.surface}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, surface: e.target.value })}
                        className={selectClasses()}
                      >
                        <option value="concrete">Concrete</option>
                        <option value="asphalt">Asphalt</option>
                        <option value="grass">Grass</option>
                        <option value="tile">Tile</option>
                        <option value="dirt">Dirt</option>
                      </select>
                    </DialogFormInput>
                    <DialogFormInput label="Lighting Level">
                      <select
                        disabled={actionLoading}
                        value={pathwayForm.lighting}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, lighting: e.target.value })}
                        className={selectClasses()}
                      >
                        <option value="excellent">Excellent</option>
                        <option value="moderate">Moderate</option>
                        <option value="none">None</option>
                      </select>
                    </DialogFormInput>
                  </DialogFormGrid>
                  <DialogFormGrid>
                    <DialogFormInput label="Notes / Constraints">
                      <input
                        type="text"
                        disabled={actionLoading}
                        value={pathwayForm.notes}
                        onChange={(e) => setPathwayForm({ ...pathwayForm, notes: e.target.value })}
                        className={inputClasses()}
                        placeholder="e.g. Closed after dark"
                      />
                    </DialogFormInput>
                    <div className="flex items-center pt-5">
                      <label className="flex items-center gap-2 font-bold cursor-pointer text-xs">
                        <input
                          type="checkbox"
                          disabled={actionLoading}
                          checked={pathwayForm.accessible}
                          onChange={(e) => setPathwayForm({ ...pathwayForm, accessible: e.target.checked })}
                          className={checkboxClasses}
                        />
                        Wheelchair Accessible Path
                      </label>
                    </div>
                  </DialogFormGrid>
                </DialogSection>
              </>
            )}

            <DialogFooter>
              <button
                type="button"
                onClick={() => setFormOpen(false)}
                disabled={actionLoading}
                className="px-4 py-2 border border-outline-variant/60 hover:bg-surface-variant text-on-surface/75 text-xs font-bold rounded-xl transition duration-200 disabled:opacity-40"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary/95 text-background text-xs font-black rounded-xl shadow-lg transition duration-200 disabled:opacity-40"
              >
                {actionLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                {actionLoading ? "Saving..." : "Save Changes"}
              </button>
            </DialogFooter>
          </form>
        )}
      </AdminDialog>
    </div>
  );
};

export default AdminNavigationPage;
