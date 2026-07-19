import React, { useState, useEffect, useRef } from "react";
import { 
  X, Mail, Phone, MapPin, 
  Clock, Globe, Copy, Check,
  Briefcase, GraduationCap, Award, BookOpen
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { FacultyMember } from "./FacultyCard";

interface FacultyProfileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  member: FacultyMember | null;
}

export const FacultyProfileDrawer: React.FC<FacultyProfileDrawerProps> = ({
  isOpen,
  onClose,
  member
}) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const drawerRef = useRef<HTMLDivElement>(null);

  // Focus trap and Esc key listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
      const activeEl = document.activeElement as HTMLElement;
      if (drawerRef.current) {
        const closeBtn = drawerRef.current.querySelector("button");
        if (closeBtn) closeBtn.focus();
      }
      return () => {
        window.removeEventListener("keydown", handleKeyDown);
        if (activeEl) activeEl.focus();
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen || !member) return null;

  const getInitials = (name: string) => {
    const cleanName = name.replace(/^(Dr\.|Dr\s+\(Mrs\.\)|Dr\.\s+\(Mrs\.\)|Dr\.\s+\(Mrs\)|Dr\s+\(Mrs\)|Prof\.|Prof\s+|Mr\.|Mrs\.|Ms\.)\s+/i, "");
    const parts = cleanName.trim().split(/\s+/);
    if (parts.length === 0) return "F";
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  const handleCopy = async (text: string, fieldLabel: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(fieldLabel);
      setToastMessage(`${fieldLabel} copied to clipboard`);
      setTimeout(() => {
        setCopiedField(null);
        setToastMessage(null);
      }, 2000);
    } catch (err) {
      console.error("Failed to copy", err);
    }
  };

  const showPlaceholderAlert = (platform: string) => {
    setToastMessage(`${platform} link is not set for this profile`);
    setTimeout(() => setToastMessage(null), 2000);
  };

  return (
    <>
      {/* Backdrop overlay for drawer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50"
      />

      {/* Drawer Panel */}
      <motion.div
        ref={drawerRef}
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ type: "tween", ease: "easeInOut", duration: 0.3 }}
        role="dialog"
        aria-modal="true"
        aria-label={`${member.name} Details`}
        className="fixed top-0 right-0 h-full w-full sm:max-w-md bg-surface-container-low border-l border-outline-variant/40 shadow-2xl z-50 flex flex-col overflow-hidden text-on-surface font-sans"
      >
        {/* Header toolbar */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-outline-variant/20 select-none shrink-0 bg-surface-container/10">
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-on-surface-variant">Profile Details</span>
          <button
            onClick={onClose}
            aria-label="Close details panel"
            className="p-1 text-on-surface-variant hover:text-primary bg-surface-container hover:bg-surface-variant rounded-lg transition-colors cursor-pointer"
          >
            <X size={16} />
          </button>
        </div>

        {/* Scrollable details body */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
          {/* Main profile block */}
          <div className="flex flex-col items-center text-center pb-6 border-b border-outline-variant/20">
            <div className="w-20 h-20 rounded-full bg-primary/10 border-2 border-primary/20 flex items-center justify-center text-xl font-mono font-extrabold text-primary mb-4 select-none">
              {getInitials(member.name)}
            </div>
            <h3 className="text-sm font-extrabold text-primary uppercase tracking-wide leading-snug">
              {member.name}
            </h3>
            <p className="text-[10px] text-on-surface-variant font-mono-code font-bold mt-1 leading-none uppercase">
              {member.designation || "Faculty Member"}
            </p>
            <p className="text-[9px] text-on-surface-variant/75 mt-1 leading-none font-medium">
              {member.department}
            </p>
          </div>

          {/* Contact Details Group */}
          <div className="space-y-3">
            <h4 className="text-[9px] font-extrabold uppercase tracking-wider text-on-surface-variant/75 border-b border-outline-variant/10 pb-1.5 select-none">Contact Information</h4>
            <div className="space-y-2 text-xs">
              {/* Email */}
              <div className="flex items-center justify-between p-2.5 bg-surface-container/20 rounded-xl border border-outline-variant/10 hover:border-outline-variant transition-colors group">
                <div className="flex items-center gap-3 min-w-0">
                  <Mail size={14} className="text-primary shrink-0" />
                  <a href={`mailto:${member.email}`} className="text-[11px] text-primary hover:underline truncate">{member.email}</a>
                </div>
                <button
                  onClick={() => handleCopy(member.email, "Email")}
                  className="p-1 text-on-surface-variant/60 hover:text-primary rounded hover:bg-surface-container cursor-pointer transition-colors"
                  title="Copy email"
                >
                  {copiedField === "Email" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                </button>
              </div>

              {/* Phone */}
              {member.phone && (
                <div className="flex items-center justify-between p-2.5 bg-surface-container/20 rounded-xl border border-outline-variant/10 hover:border-outline-variant transition-colors group">
                  <div className="flex items-center gap-3 min-w-0">
                    <Phone size={14} className="text-primary shrink-0" />
                    <span className="text-[11px] font-mono-code text-on-surface truncate">{member.phone}</span>
                  </div>
                  <button
                    onClick={() => handleCopy(member.phone || "", "Phone number")}
                    className="p-1 text-on-surface-variant/60 hover:text-primary rounded hover:bg-surface-container cursor-pointer transition-colors"
                    title="Copy phone"
                  >
                    {copiedField === "Phone number" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                  </button>
                </div>
              )}

              {/* Website */}
              {member.website && (
                <div className="flex items-center justify-between p-2.5 bg-surface-container/20 rounded-xl border border-outline-variant/10 hover:border-outline-variant transition-colors group">
                  <div className="flex items-center gap-3 min-w-0">
                    <Globe size={14} className="text-primary shrink-0" />
                    <a href={member.website} target="_blank" rel="noopener noreferrer" className="text-[11px] text-primary hover:underline truncate">{member.website}</a>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Location Group */}
          <div className="space-y-3">
            <h4 className="text-[9px] font-extrabold uppercase tracking-wider text-on-surface-variant/75 border-b border-outline-variant/10 pb-1.5 select-none">Campus Location</h4>
            <div className="space-y-2 text-xs">
              {/* Office / Building */}
              {(member.office || member.building) && (
                <div className="flex items-start justify-between p-2.5 bg-surface-container/20 rounded-xl border border-outline-variant/10">
                  <div className="flex items-center gap-3 min-w-0">
                    <MapPin size={14} className="text-primary shrink-0 mt-0.5" />
                    <div>
                      {member.office && <p className="text-[11px] text-on-surface leading-normal">Office: {member.office}</p>}
                      {member.building && <p className="text-[10px] text-on-surface-variant mt-0.5">Building: {member.building}</p>}
                    </div>
                  </div>
                  {member.office && (
                    <button
                      onClick={() => handleCopy(member.office || "", "Office location")}
                      className="p-1 text-on-surface-variant/60 hover:text-primary rounded hover:bg-surface-container cursor-pointer transition-colors"
                      title="Copy office details"
                    >
                      {copiedField === "Office location" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                    </button>
                  )}
                </div>
              )}

              {/* Office Hours */}
              {member.office_hours && (
                <div className="flex items-center gap-3 p-2.5 bg-surface-container/20 rounded-xl border border-outline-variant/10">
                  <Clock size={14} className="text-primary shrink-0" />
                  <span className="text-[11px] text-on-surface truncate">Consultation: {member.office_hours}</span>
                </div>
              )}
            </div>
          </div>

          {/* Research Interests Group */}
          {member.research_interests && member.research_interests.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-[9px] font-extrabold uppercase tracking-wider text-on-surface-variant/75 border-b border-outline-variant/10 pb-1.5 select-none">Research Fields</h4>
              <div className="flex gap-2 flex-wrap">
                {member.research_interests.map((interest) => (
                  <span
                    key={interest}
                    className="bg-surface-container text-primary text-[8px] font-extrabold uppercase tracking-wide px-3 py-1 rounded-full border border-outline-variant/30 select-none"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Academic Profiles Placeholder */}
          <div className="space-y-3">
            <h4 className="text-[9px] font-extrabold uppercase tracking-wider text-on-surface-variant/75 border-b border-outline-variant/10 pb-1.5 select-none">Academic Networks</h4>
            <div className="flex justify-around items-center py-2 bg-surface-container/10 border border-outline-variant/20 rounded-xl">
              <button
                onClick={() => showPlaceholderAlert("Google Scholar")}
                className="flex flex-col items-center gap-1.5 p-2 text-on-surface-variant/70 hover:text-primary transition-colors cursor-pointer"
                title="Google Scholar Profile"
              >
                <GraduationCap size={18} />
                <span className="text-[8px] font-bold uppercase tracking-wider">Scholar</span>
              </button>
              <button
                onClick={() => showPlaceholderAlert("ResearchGate")}
                className="flex flex-col items-center gap-1.5 p-2 text-on-surface-variant/70 hover:text-primary transition-colors cursor-pointer"
                title="ResearchGate Profile"
              >
                <BookOpen size={18} />
                <span className="text-[8px] font-bold uppercase tracking-wider">RG</span>
              </button>
              <button
                onClick={() => showPlaceholderAlert("LinkedIn")}
                className="flex flex-col items-center gap-1.5 p-2 text-on-surface-variant/70 hover:text-primary transition-colors cursor-pointer"
                title="LinkedIn Profile"
              >
                <Briefcase size={18} />
                <span className="text-[8px] font-bold uppercase tracking-wider">LinkedIn</span>
              </button>
              <button
                onClick={() => showPlaceholderAlert("ORCID")}
                className="flex flex-col items-center gap-1.5 p-2 text-on-surface-variant/70 hover:text-primary transition-colors cursor-pointer"
                title="ORCID ID Record"
              >
                <Award size={18} />
                <span className="text-[8px] font-bold uppercase tracking-wider">ORCID</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-outline-variant/10 bg-surface-container/10 text-[9px] font-bold text-on-surface-variant/60 uppercase tracking-wider text-center select-none shrink-0">
          Birla Institute of Technology, Mesra &bull; 2026
        </div>

        {/* Success Toast */}
        <AnimatePresence>
          {toastMessage && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 30 }}
              className="absolute bottom-12 left-1/2 -translate-x-1/2 bg-primary text-background px-4 py-2 rounded-full shadow-lg z-50 text-[10px] font-extrabold uppercase tracking-wider select-none pointer-events-none"
            >
              {toastMessage}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  );
};
