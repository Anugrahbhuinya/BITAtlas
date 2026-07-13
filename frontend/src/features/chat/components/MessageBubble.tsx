import { Volume2, VolumeX, MapPinned, Bot, Navigation, Clock, Coffee, BookOpen, Building2, Terminal, Activity } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import type { ChatMessage } from "../types";
import { useMapStore } from "../../map/store/useMapStore";
import { navigationApi } from "../../navigation/services/navigationApi";
import type { GraphNode } from "../../navigation/types";
import Markdown from "../../../shared/components/Markdown";
import NavigationCard from "../../navigation/components/NavigationCard";

interface Props {
  message: ChatMessage;
  onSpeak: (text: string) => void;
  onStopSpeaking: () => void;
  isSpeaking: boolean;
}

const locationMapping: Record<string, string> = {
  "cat hall": "CAT Hall",
  "central lecture hall": "CAT Hall",
  "central library": "Library",
  library: "Library",
  "administrative building": "Main Building",
  "main building": "Main Building",
  "administrative block": "Main Building",
  "institute administration offices": "Main Building",
};

const navPatterns = [
  { pattern: /walking\s*time|walk.*?(\d+)\s*min/i, action: "view_route", label: "View Route", icon: "navigation" },
  { pattern: /leave\s*(in|now|immediately)|depart(ure)?|should leave/i, action: "departure", label: "Departure Plan", icon: "clock" },
  { pattern: /nearest\s*(atm|cafeteria|xerox|printer|library|washroom|cafe)/i, action: "nearby", label: "Show Nearby", icon: "building" },
  { pattern: /grab\s*a?\s*(coffee|snack)|cafeteria|canteen|food/i, action: "cafeteria", label: "Find Cafeteria", icon: "coffee" },
  { pattern: /study|library|reading\s*room|study\s*area/i, action: "study", label: "Find Study Spot", icon: "book" },
];

export const MessageBubble = ({
  message,
  onSpeak,
  onStopSpeaking,
  isSpeaking,
}: Props) => {
  const isUser = message.sender === "user";
  const navigate = useNavigate();
  const setSelectedLocation = useMapStore((state) => state.setSelectedLocation);
  
  const [allNodes, setAllNodes] = useState<GraphNode[]>([]);
  const [showDebug, setShowDebug] = useState(false);
  useEffect(() => {
    const loadNodes = async () => {
      try {
        const nodes = await navigationApi.fetchGraphNodes();
        setAllNodes(nodes);
      } catch (e) {
        console.error("Failed to load graph nodes in MessageBubble:", e);
      }
    };
    loadNodes();
  }, []);

  const detectedKey = Object.keys(locationMapping).find((key) =>
    message.text.toLowerCase().includes(key)
  );

  const detectedLocation = detectedKey
    ? locationMapping[detectedKey]
    : undefined;

  const detectedActions = !isUser
    ? navPatterns.filter((p) => p.pattern.test(message.text))
    : [];
  const uniqueActions = detectedActions.filter(
    (a, idx, arr) => arr.findIndex((b) => b.action === a.action) === idx
  );

  const handleOpenMap = () => {
    if (!detectedLocation) return;
    setSelectedLocation(detectedLocation);
    navigate("/map");
  };

  const handleQuickAction = () => {
    navigate("/map");
  };

  const getActionIcon = (icon: string) => {
    switch (icon) {
      case "navigation": return <Navigation size={11} />;
      case "clock": return <Clock size={11} />;
      case "coffee": return <Coffee size={11} />;
      case "book": return <BookOpen size={11} />;
      case "building": return <Building2 size={11} />;
      default: return <MapPinned size={11} />;
    }
  };

  const showNavigationCard = !isUser && (message.messageType === "navigation" || !!message.navigation_context);
  const cleanText = (text: string) => {
    if (showNavigationCard && text.includes("### Destination")) {
      return text.split("### Destination")[0].trim();
    }
    return text;
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={`flex mb-4 w-full ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div className={`flex gap-3 max-w-[85%] md:max-w-[850px] w-full ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        {!isUser ? (
          <div className="w-7 h-7 rounded-lg bg-surface-container border border-outline-variant flex items-center justify-center shrink-0 self-start mt-1 shadow-sm select-none">
            <Bot size={14} className="text-primary" />
          </div>
        ) : null}

        <div className="flex-1 min-w-0 flex flex-col">
          <div
            className={`
              break-words
              text-xs md:text-sm
              leading-relaxed
              w-full
              ${isUser 
                ? "bg-surface-container/60 border border-outline-variant/50 text-on-surface font-medium rounded-2xl rounded-tr-sm px-4 py-2.5 self-end max-w-[85%] shadow-xs" 
                : "bg-transparent border-none shadow-none text-on-surface px-0 py-1"
              }
            `}
          >
            <Markdown text={cleanText(message.text)} />

            {showNavigationCard && message.navigation_context && (
              <div className="mt-3 pt-3 border-t border-outline-variant/30">
                <NavigationCard
                  navigationContext={message.navigation_context}
                  allNodes={allNodes}
                />
              </div>
            )}

            {!isUser && !message.navigation_context && uniqueActions.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-outline-variant/30">
                {uniqueActions.map((action) => (
                  <button
                    key={action.action}
                    onClick={handleQuickAction}
                    className="flex items-center gap-1.5 bg-primary/5 border border-primary/20 hover:bg-primary/10 hover:border-primary/40 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider text-primary transition-all active:scale-[0.97] cursor-pointer"
                  >
                    {getActionIcon(action.icon)}
                    <span>{action.label}</span>
                  </button>
                ))}
              </div>
            )}

            {!isUser && !message.navigation_context && detectedLocation && uniqueActions.length === 0 && (
              <button
                onClick={handleOpenMap}
                className="mt-3 flex items-center gap-1.5 bg-surface-container-high border border-outline-variant hover:border-primary px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider text-primary transition-all active:scale-[0.98] cursor-pointer"
              >
                <MapPinned size={12} />
                <span>Open on Map</span>
              </button>
            )}

            {/* Developer Observability Panel Toggle Button */}
            {!isUser && message.diagnostics?.debug_rag && (
              <div className="mt-4 pt-3 border-t border-outline-variant/30 select-none">
                <button
                  onClick={() => setShowDebug(!showDebug)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/70 border border-outline-variant bg-transparent hover:bg-surface-container-high hover:border-outline hover:text-primary transition-all cursor-pointer"
                >
                  <Terminal size={12} />
                  <span>{showDebug ? "▲ Diagnostics" : "▼ Diagnostics"}</span>
                </button>
              </div>
            )}

          {/* Collapsible Developer Observability Panel */}
          {!isUser && showDebug && message.diagnostics?.debug_rag && (
            <div className="mt-4 p-4 rounded-xl bg-surface-container-high border border-outline-variant text-[11px] text-on-surface-variant font-sans space-y-4 animate-in fade-in slide-in-from-top-1 duration-200">
              {/* Header / Performance Metrics Dashboard */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-outline-variant/40 pb-2.5">
                <div className="flex items-center gap-1.5">
                  <Activity size={14} className="text-primary animate-pulse" />
                  <span className="font-bold text-xs text-primary uppercase tracking-wider">Pipeline Performance</span>
                </div>
                <div className="flex items-center gap-4">
                  <div>
                    <span className="text-[10px] uppercase text-on-surface-variant/60 block font-semibold">Total Latency</span>
                    <span className="font-bold text-xs text-green-500">{message.diagnostics.debug_rag.latencies_ms.total} ms</span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-on-surface-variant/60 block font-semibold">LLM Gen Time</span>
                    <span className="font-bold text-xs text-cyan-400">{message.diagnostics.debug_rag.latencies_ms.llm} ms</span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-on-surface-variant/60 block font-semibold">RAG Retrieval</span>
                    <span className="font-bold text-xs text-yellow-400">{message.diagnostics.debug_rag.latencies_ms.total_retrieval} ms</span>
                  </div>
                </div>
              </div>

              {/* Grid Section for Query Info & LLM details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Query Classification */}
                <div className="space-y-1.5 p-3 rounded-lg bg-surface-container/60 border border-outline-variant/30">
                  <span className="font-bold text-[10px] uppercase text-primary tracking-wide block mb-1">Query Intent Analysis</span>
                  <div><span className="font-semibold text-on-surface-variant/70">Original Query:</span> <code className="px-1 py-0.5 rounded bg-surface-container-lowest text-primary">{message.diagnostics.debug_rag.query_info.original_query}</code></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Normalized Query:</span> <code className="px-1 py-0.5 rounded bg-surface-container-lowest">{message.diagnostics.debug_rag.query_info.normalized_query}</code></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Detected Intent:</span> <span className="font-bold text-on-surface">{message.diagnostics.debug_rag.query_info.detected_intent}</span></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Query Category:</span> <span className="text-on-surface">{message.diagnostics.debug_rag.query_info.query_category}</span></div>
                  {message.diagnostics.debug_rag.query_info.synonyms_expanded?.length > 0 && (
                    <div>
                      <span className="font-semibold text-on-surface-variant/70">Synonyms Expanded:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {message.diagnostics.debug_rag.query_info.synonyms_expanded.map((syn: string, idx: number) => (
                          <span key={idx} className="px-1.5 py-0.5 text-[9px] font-mono rounded-md bg-primary/5 text-primary border border-primary/10">{syn}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* LLM & Model Usage */}
                <div className="space-y-1.5 p-3 rounded-lg bg-surface-container/60 border border-outline-variant/30">
                  <span className="font-bold text-[10px] uppercase text-primary tracking-wide block mb-1">LLM / Token Telemetry</span>
                  <div><span className="font-semibold text-on-surface-variant/70">LLM Model:</span> <span className="font-bold text-on-surface text-xs">{message.diagnostics.debug_rag.llm.model || "Gemini-2.5-flash"}</span></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Prompt Tokens:</span> <span className="text-on-surface">{message.diagnostics.debug_rag.llm.prompt_tokens}</span></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Completion Tokens:</span> <span className="text-on-surface">{message.diagnostics.debug_rag.llm.completion_tokens}</span></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Total Tokens:</span> <span className="font-bold text-primary">{message.diagnostics.debug_rag.llm.total_tokens}</span></div>
                  <div className="flex items-center gap-1.5 mt-1">
                    <span className="font-semibold text-on-surface-variant/70">Response Confidence:</span> 
                    <span className={`px-1.5 py-0.5 rounded-full text-[9px] font-bold ${message.diagnostics.debug_rag.response.confidence > 0.6 ? "bg-green-500/10 text-green-500" : "bg-yellow-500/10 text-yellow-500"}`}>
                      {(message.diagnostics.debug_rag.response.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Latency Stages Chart */}
              <div className="space-y-2 p-3 rounded-lg bg-surface-container/60 border border-outline-variant/30">
                <span className="font-bold text-[10px] uppercase text-primary tracking-wide block">Latency Stage Breakdown</span>
                <div className="space-y-1.5">
                  {[
                    { label: "Embedding Gen", val: message.diagnostics.debug_rag.latencies_ms.embedding, color: "bg-purple-500" },
                    { label: "Vector Store Search", val: message.diagnostics.debug_rag.latencies_ms.vector_search, color: "bg-blue-500" },
                    { label: "Metadata Filtering", val: message.diagnostics.debug_rag.latencies_ms.metadata_filtering, color: "bg-amber-500" },
                    { label: "Cross Encoder Rerank", val: message.diagnostics.debug_rag.latencies_ms.cross_encoder, color: "bg-orange-500" },
                    { label: "Prompt Orchestration", val: message.diagnostics.debug_rag.latencies_ms.prompt_builder, color: "bg-pink-500" },
                    { label: "LLM Inference API", val: message.diagnostics.debug_rag.latencies_ms.llm, color: "bg-cyan-500" },
                  ].map((stage, idx) => {
                    const pct = message.diagnostics.debug_rag.latencies_ms.total > 0
                      ? Math.min(100, Math.round((stage.val / message.diagnostics.debug_rag.latencies_ms.total) * 100))
                      : 0;
                    return (
                      <div key={idx} className="space-y-0.5">
                        <div className="flex justify-between text-[9px] font-semibold">
                          <span className="text-on-surface-variant/70">{stage.label}</span>
                          <span className="text-on-surface">{stage.val} ms ({pct}%)</span>
                        </div>
                        <div className="h-1.5 rounded-full bg-surface-container-lowest overflow-hidden">
                          <div className={`h-full ${stage.color} rounded-full`} style={{ width: `${pct}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* RAG Candidates Rankings */}
              {message.diagnostics.debug_rag.candidates?.length > 0 && (
                <div className="space-y-2 p-3 rounded-lg bg-surface-container/60 border border-outline-variant/30">
                  <span className="font-bold text-[10px] uppercase text-primary tracking-wide block">RAG Candidate Document Retrieval</span>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-[10px]">
                      <thead>
                        <tr className="border-b border-outline-variant/40 text-on-surface-variant/60 font-bold uppercase tracking-wider text-left">
                          <th className="py-1.5 px-2">Rank</th>
                          <th className="py-1.5 px-2">Source / Title</th>
                          <th className="py-1.5 px-2 font-mono">Sim</th>
                          <th className="py-1.5 px-2 font-mono">Final</th>
                          <th className="py-1.5 px-2">Decision Reason / Explanation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {message.diagnostics.debug_rag.candidates.slice(0, 5).map((cand: { rank: number; source_type: string; title: string; raw_score: number; combined_score: number; explanation: string }, idx: number) => (
                          <tr key={idx} className="border-b border-outline-variant/20 hover:bg-surface-container-high transition-colors">
                            <td className="py-2 px-2 font-bold text-primary">#{cand.rank}</td>
                            <td className="py-2 px-2 max-w-[150px] truncate">
                              <span className="px-1 py-0.5 text-[8px] font-bold uppercase tracking-wide rounded bg-primary/10 text-primary mr-1.5">{cand.source_type}</span>
                              <span className="font-semibold text-on-surface" title={cand.title}>{cand.title}</span>
                            </td>
                            <td className="py-2 px-2 font-mono text-on-surface-variant/80">{cand.raw_score.toFixed(3)}</td>
                            <td className="py-2 px-2 font-mono text-on-surface-variant/80">{cand.combined_score.toFixed(3)}</td>
                            <td className="py-2 px-2 italic text-on-surface-variant/70 text-[9px] max-w-[200px] truncate" title={cand.explanation}>{cand.explanation}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Context / Prompt Builder Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5 p-3 rounded-lg bg-surface-container/60 border border-outline-variant/30">
                  <span className="font-bold text-[10px] uppercase text-primary tracking-wide block mb-1">Context Chunks</span>
                  <div><span className="font-semibold text-on-surface-variant/70">Selected Chunks:</span> <span className="font-bold text-green-500">{message.diagnostics.debug_rag.context_builder.selected_chunks_count}</span></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Rejected Chunks:</span> <span className="font-semibold text-red-400">{message.diagnostics.debug_rag.context_builder.rejected_chunks_count}</span></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Duplicates Removed:</span> <span className="text-on-surface">{message.diagnostics.debug_rag.context_builder.duplicate_removal_count}</span></div>
                  <div><span className="font-semibold text-on-surface-variant/70">Metadata Filters:</span> <code className="text-[9px] block p-1 mt-1 rounded bg-surface-container-lowest border border-outline-variant/30 overflow-x-auto select-all max-h-12 font-mono">{message.diagnostics.debug_rag.context_builder.metadata_filtering_details || "None"}</code></div>
                </div>

                <div className="space-y-1.5 p-3 rounded-lg bg-surface-container/60 border border-outline-variant/30">
                  <span className="font-bold text-[10px] uppercase text-primary tracking-wide block mb-1">System Guard & Response Check</span>
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-on-surface-variant/70">Fallback Strategy used:</span>
                    <span className={`px-1.5 py-0.5 rounded-full text-[9px] font-bold ${message.diagnostics.debug_rag.response.fallback_used ? "bg-amber-500/10 text-amber-500" : "bg-green-500/10 text-green-500"}`}>
                      {message.diagnostics.debug_rag.response.fallback_used ? "YES" : "NO"}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-on-surface-variant/70">Hallucination Risk Warning:</span>
                    <span className={`px-1.5 py-0.5 rounded-full text-[9px] font-bold ${message.diagnostics.debug_rag.response.hallucination_warning ? "bg-red-500/10 text-red-500 animate-pulse" : "bg-green-500/10 text-green-500"}`}>
                      {message.diagnostics.debug_rag.response.hallucination_warning ? "WARN" : "SAFE"}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-on-surface-variant/70">Knowledge Sources:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {message.diagnostics.debug_rag.prompt_builder.knowledge_sources?.length > 0 ? (
                        message.diagnostics.debug_rag.prompt_builder.knowledge_sources.map((src: string, idx: number) => (
                          <span key={idx} className="px-1.5 py-0.5 text-[9px] font-bold rounded-md bg-secondary/10 text-secondary border border-secondary/20">{src}</span>
                        ))
                      ) : (
                        <span className="text-on-surface-variant/50">None</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Speak Toggle Button */}
        {!isUser && (
          <button
            onClick={isSpeaking ? onStopSpeaking : () => onSpeak(message.text)}
            aria-label={isSpeaking ? "Stop listening to response" : "Listen to response"}
            className={`
              p-2
              rounded-lg
              border
              transition-all
              duration-150
              cursor-pointer
              mt-1.5
              self-start
              ${
                isSpeaking
                  ? "bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/20 scale-105"
                  : "bg-surface-container border-outline-variant text-on-surface-variant hover:text-primary hover:border-primary"
              }
            `}
            title={isSpeaking ? "Stop listening" : "Listen to answer"}
          >
            {isSpeaking ? <VolumeX size={13} /> : <Volume2 size={13} />}
          </button>
        )}
      </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;
