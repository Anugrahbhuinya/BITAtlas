import React, { useEffect, useRef } from "react";
import { X, Wrench } from "lucide-react";
import { motion } from "framer-motion";

interface PlaceholderModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
}

export const PlaceholderModal: React.FC<PlaceholderModalProps> = ({
  isOpen,
  onClose,
  title
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
      const activeEl = document.activeElement as HTMLElement;
      if (modalRef.current) {
        const btn = modalRef.current.querySelector("button");
        if (btn) btn.focus();
      }
      return () => {
        window.removeEventListener("keydown", handleKeyDown);
        if (activeEl) activeEl.focus();
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-background/80 backdrop-blur-sm"
      />

      {/* Modal Box */}
      <motion.div
        ref={modalRef}
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ type: "spring", duration: 0.3 }}
        role="dialog"
        aria-modal="true"
        aria-label={`${title} Modal`}
        className="relative w-full max-w-md bg-surface-container-low border border-outline-variant/40 rounded-2xl shadow-2xl p-6 text-on-surface font-sans"
      >
        <button
          onClick={onClose}
          aria-label="Close dialog"
          className="absolute top-4 right-4 p-1 text-on-surface-variant hover:text-primary bg-surface-container hover:bg-surface-variant rounded-lg transition-colors cursor-pointer"
        >
          <X size={14} />
        </button>

        <div className="flex flex-col items-center justify-center text-center py-6">
          <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-4 animate-bounce">
            <Wrench size={20} />
          </div>
          <h3 className="text-sm font-extrabold text-primary uppercase tracking-wide mb-2">
            {title}
          </h3>
          <p className="text-xs text-on-surface-variant max-w-xs leading-relaxed font-medium">
            This module is currently in development. Real-time {title.toLowerCase()} directories will be integrated here in future phases.
          </p>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-primary hover:bg-primary-light text-background text-[10px] font-extrabold uppercase tracking-wider rounded-lg transition-colors cursor-pointer active:scale-[0.98]"
          >
            Close
          </button>
        </div>
      </motion.div>
    </div>
  );
};
