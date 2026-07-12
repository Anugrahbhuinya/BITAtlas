// src/features/navigation/components/GraphExplorer.tsx

import React, { useState, useEffect } from "react";
import { Search, Share2, MapPin, Tag, ShieldCheck, ShieldAlert, ArrowRight, CornerDownRight } from "lucide-react";
import { navigationApi } from "../services/navigationApi";
import type { GraphNode, GraphNeighbor } from "../types";

export const GraphExplorer: React.FC = () => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [nodesLoading, setNodesLoading] = useState(true);
  const [selectedNodeId, setSelectedNodeId] = useState<string>("");
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  
  const [neighbors, setNeighbors] = useState<GraphNeighbor[]>([]);
  const [neighborsLoading, setNeighborsLoading] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  // Load all nodes on mount
  useEffect(() => {
    const loadNodes = async () => {
      setNodesLoading(true);
      try {
        const data = await navigationApi.fetchGraphNodes();
        setNodes(data);
      } catch (err) {
        console.error("Failed to load graph nodes", err);
      } finally {
        setNodesLoading(false);
      }
    };
    loadNodes();
  }, []);

  // Load details and neighbors when selected node changes
  useEffect(() => {
    if (!selectedNodeId) {
      setSelectedNode(null);
      setNeighbors([]);
      return;
    }

    const loadNeighbors = async () => {
      setNeighborsLoading(true);
      try {
        const nodeData = await navigationApi.fetchGraphNode(selectedNodeId);
        setSelectedNode(nodeData);
        
        const neighborsData = await navigationApi.fetchGraphNeighbors(selectedNodeId);
        setNeighbors(neighborsData);
      } catch (err) {
        console.error("Failed to load neighbors for node", selectedNodeId, err);
      } finally {
        setNeighborsLoading(false);
      }
    };

    loadNeighbors();
  }, [selectedNodeId]);

  const filteredNodes = nodes.filter((n) => {
    const matchesSearch = n.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          n.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === "" || n.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const nodeTypes = Array.from(new Set(nodes.map((n) => n.type)));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Sidebar Selector */}
      <div className="lg:col-span-1 bg-surface border border-outline-variant/45 rounded-2xl p-4 shadow-sm flex flex-col h-[550px]">
        <h4 className="font-extrabold text-sm text-on-surface mb-3 flex items-center gap-2">
          <Search className="w-4 h-4 text-primary" />
          Select Graph Node
        </h4>

        {/* Filter Toolbar */}
        <div className="space-y-2 mb-4">
          <input
            type="text"
            placeholder="Search nodes by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full p-2 bg-surface border border-outline-variant/50 rounded-xl text-xs"
          />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="w-full p-2 bg-surface border border-outline-variant/50 rounded-xl text-xs capitalize"
          >
            <option value="">All Types</option>
            {nodeTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        {/* Nodes Scrollable List */}
        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
          {nodesLoading ? (
            <p className="text-xs text-on-surface/50 text-center py-8">Loading nodes list...</p>
          ) : filteredNodes.length === 0 ? (
            <p className="text-xs text-on-surface/40 text-center py-8">No matching nodes found.</p>
          ) : (
            filteredNodes.map((n) => (
              <button
                key={n.id}
                onClick={() => setSelectedNodeId(n.id)}
                className={`w-full text-left p-2.5 rounded-xl border text-xs flex justify-between items-center transition ${
                  selectedNodeId === n.id
                    ? "bg-primary/10 border-primary text-primary font-bold"
                    : "bg-surface hover:bg-surface-variant/20 border-outline-variant/30 text-on-surface/85"
                }`}
              >
                <div className="truncate pr-2">
                  <p className="truncate font-semibold text-on-surface">{n.name}</p>
                  <p className="text-[10px] opacity-65 truncate font-mono mt-0.5">{n.id}</p>
                </div>
                <span className={`px-2 py-0.5 rounded font-black text-[9px] uppercase tracking-wider ${
                  selectedNodeId === n.id ? "bg-primary/15" : "bg-surface-variant text-on-surface-variant"
                }`}>
                  {n.type}
                </span>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Node & Relationships Inspection Area */}
      <div className="lg:col-span-2 space-y-6">
        {selectedNode ? (
          <>
            {/* Attributes Panel */}
            <div className="bg-surface border border-outline-variant/45 rounded-2xl p-5 shadow-sm">
              <div className="flex justify-between items-start gap-4 border-b border-outline-variant/20 pb-3 mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-primary/10 text-primary rounded font-black text-[9px] uppercase tracking-wider">
                      {selectedNode.type}
                    </span>
                    <span className="font-mono text-[10px] text-on-surface/50">{selectedNode.id}</span>
                  </div>
                  <h3 className="text-md font-black text-on-surface mt-1">{selectedNode.name}</h3>
                </div>
                
                <div className="text-right text-[11px] text-on-surface/65 font-mono">
                  <div className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-primary" />
                    <span>[{selectedNode.coordinates.latitude.toFixed(5)}, {selectedNode.coordinates.longitude.toFixed(5)}]</span>
                  </div>
                </div>
              </div>

              {/* Metadata Attributes table */}
              <div className="space-y-2">
                <h5 className="text-[10px] uppercase font-bold tracking-wider text-on-surface/55">Node Attributes</h5>
                <div className="bg-surface-variant/10 rounded-xl p-3 border border-outline-variant/30 text-xs font-mono max-h-40 overflow-y-auto">
                  {Object.keys(selectedNode.metadata).length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {Object.entries(selectedNode.metadata).map(([key, val]) => (
                        <div key={key} className="flex flex-col border-b border-outline-variant/20 pb-1.5">
                          <span className="text-[9px] uppercase font-bold text-on-surface/55 tracking-wider">{key}</span>
                          <span className="text-on-surface/85 truncate mt-0.5 font-semibold">
                            {Array.isArray(val) ? val.join(", ") : typeof val === "object" ? JSON.stringify(val) : String(val)}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[10px] text-on-surface/40 text-center py-2">No custom metadata attributes on this node.</p>
                  )}
                </div>
              </div>
            </div>

            {/* Relationships/Edges Panel */}
            <div className="bg-surface border border-outline-variant/45 rounded-2xl p-5 shadow-sm">
              <h4 className="font-extrabold text-sm text-on-surface mb-3 flex items-center gap-2">
                <Share2 className="w-4 h-4 text-secondary" />
                Connected Neighbors ({neighbors.length})
              </h4>

              <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
                {neighborsLoading ? (
                  <p className="text-xs text-on-surface/50 text-center py-6">Loading connections...</p>
                ) : neighbors.length === 0 ? (
                  <p className="text-xs text-on-surface/40 text-center py-6">This node has no outgoing edges.</p>
                ) : (
                  neighbors.map((n, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-surface-variant/5 border border-outline-variant/30 rounded-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 text-xs"
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <CornerDownRight className="w-4 h-4 text-on-surface/40 flex-shrink-0" />
                        <div className="truncate">
                          <div className="flex items-center gap-1.5">
                            <span className="font-bold text-on-surface">{n.node.name}</span>
                            <span className="px-1.5 py-0.2 bg-surface-variant text-on-surface-variant rounded text-[9px] uppercase tracking-wider">
                              {n.node.type}
                            </span>
                          </div>
                          <p className="text-[10px] font-mono text-on-surface/50 truncate mt-0.5">{n.node.id}</p>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2.5 text-[10px] font-mono self-end sm:self-center">
                        {n.edge.distance !== null && n.edge.distance !== undefined && (
                          <span className="bg-secondary/10 px-2 py-0.5 rounded font-bold text-secondary">
                            Distance: {n.edge.distance}m
                          </span>
                        )}
                        <span className={`px-2 py-0.5 rounded font-bold flex items-center gap-1 ${
                          n.edge.accessibility ? "bg-success/10 text-success" : "bg-error/10 text-error"
                        }`}>
                          {n.edge.accessibility ? <ShieldCheck className="w-3.5 h-3.5" /> : <ShieldAlert className="w-3.5 h-3.5" />}
                          {n.edge.accessibility ? "Accessible" : "Steep/Stairs"}
                        </span>
                        <span className="bg-surface-variant/60 border border-outline-variant/30 px-2 py-0.5 rounded font-black text-on-surface/75 text-[9px]">
                          {n.edge.relationship}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="bg-surface/50 border border-outline-variant/35 rounded-2xl h-[450px] flex flex-col items-center justify-center text-center p-6 text-on-surface/45">
            <Share2 className="w-12 h-12 text-on-surface/30 mb-3" />
            <h4 className="font-extrabold text-sm text-on-surface/65">No Node Selected</h4>
            <p className="text-xs text-on-surface/55 max-w-xs mt-1">
              Select a node from the sidebar registry index to inspect its internal attributes and outgoing graph linkages.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
