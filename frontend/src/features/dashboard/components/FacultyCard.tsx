import React, { useState } from "react";
import { Mail, Copy, Check, Phone } from "lucide-react";

export interface FacultyMember {
  id: string;
  name: string;
  designation: string | null;
  department: string;
  email: string;
  phone: string | null;
  research_interests: string[];
  office: string | null;
  building: string | null;
  office_hours: string | null;
  website: string | null;
  photo: string | null;
}

interface FacultyCardProps {
  member: FacultyMember;
  onClick?: () => void;
}

export const FacultyCard: React.FC<FacultyCardProps> = ({ member, onClick }) => {
  const [copied, setCopied] = useState(false);

  const getInitials = (name: string) => {
    const cleanName = name.replace(/^(Dr\.|Dr\s+\(Mrs\.\)|Dr\.\s+\(Mrs\.\)|Dr\.\s+\(Mrs\)|Dr\s+\(Mrs\)|Prof\.|Prof\s+|Mr\.|Mrs\.|Ms\.)\s+/i, "");
    const parts = cleanName.trim().split(/\s+/);
    if (parts.length === 0) return "F";
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  const handleCopyEmail = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(member.email);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy email: ", err);
    }
  };

  return (
    <div 
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`View profile of ${member.name}`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (onClick) onClick();
        }
      }}
      className="border border-outline-variant/40 bg-surface-container-low rounded-2xl p-5 hover:border-outline hover:bg-surface-container/30 transition-all duration-200 flex flex-col justify-between h-full cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40 select-none group/card"
    >
      <div className="space-y-4">
        {/* Profile Avatar & Title */}
        <div className="flex gap-4 items-start">
          <div className="w-11 h-11 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-xs font-mono font-extrabold text-primary shrink-0 select-none group-hover/card:scale-105 transition-transform">
            {getInitials(member.name)}
          </div>
          <div className="min-w-0">
            <h4 className="text-xs font-bold text-primary leading-snug uppercase tracking-wide truncate group-hover/card:text-primary-light">
              {member.name}
            </h4>
            <p className="text-[10px] text-on-surface-variant font-mono-code font-bold mt-0.5 leading-none uppercase">
              {member.designation || "Faculty Member"}
            </p>
            <p className="text-[9px] text-on-surface-variant/75 mt-1 leading-none font-medium">
              {member.department}
            </p>
          </div>
        </div>

        {/* Contact info list */}
        <div className="space-y-2 pt-3 border-t border-outline-variant/20 text-[10px] text-on-surface-variant font-medium">
          <div className="flex items-center gap-2 group/link">
            <Mail size={12} className="text-primary shrink-0" />
            <span className="text-primary hover:underline truncate">
              {member.email}
            </span>
          </div>
          {member.phone && (
            <div className="flex items-center gap-2">
              <Phone size={12} className="text-primary shrink-0" />
              <span className="font-mono-code">{member.phone}</span>
            </div>
          )}
        </div>

        {/* Research interests tags */}
        {member.research_interests && member.research_interests.length > 0 && (
          <div className="flex gap-1.5 flex-wrap pt-2">
            {member.research_interests.map((interest) => (
              <span
                key={interest}
                className="bg-surface-container text-primary text-[8px] font-extrabold uppercase tracking-wide px-2 py-0.5 rounded-full border border-outline-variant/30 select-none"
              >
                {interest}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Copy Actions Footer */}
      <div className="flex gap-2 mt-4 pt-3 border-t border-outline-variant/10">
        <a
          href={`mailto:${member.email}`}
          onClick={(e) => e.stopPropagation()}
          className="flex-1 flex items-center justify-center gap-1.5 py-1.5 border border-outline-variant hover:border-primary rounded-lg text-[9px] font-extrabold text-primary uppercase tracking-wider hover:bg-primary/5 transition-colors cursor-pointer text-center"
        >
          <Mail size={10} />
          <span>Email</span>
        </a>
        <button
          onClick={handleCopyEmail}
          className="flex-1 flex items-center justify-center gap-1.5 py-1.5 border border-outline-variant hover:border-primary rounded-lg text-[9px] font-extrabold text-primary uppercase tracking-wider hover:bg-primary/5 transition-colors cursor-pointer active:scale-[0.98]"
          title="Copy email to clipboard"
        >
          {copied ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
          <span>{copied ? "Copied" : "Copy Email"}</span>
        </button>
      </div>
    </div>
  );
};
