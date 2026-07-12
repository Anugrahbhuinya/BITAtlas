// src/features/navigation/components/dialogs/AdminDialog.tsx

import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

interface AdminDialogProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "2xl";
  closeOnOutsideClick?: boolean;
}

const sizeClasses = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
  "2xl": "max-w-5xl"
};

export const AdminDialog: React.FC<AdminDialogProps> = ({
  isOpen,
  onClose,
  title,
  description,
  icon,
  children,
  size = "lg",
  closeOnOutsideClick = true
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  // Close on ESC key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (closeOnOutsideClick && dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 overflow-y-auto">
          {/* Backdrop Animation */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            onClick={handleBackdropClick}
            className="fixed inset-0 bg-background/80 backdrop-blur-md"
          />

          {/* Dialog Container Animation */}
          <motion.div
            ref={dialogRef}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className={`w-full ${sizeClasses[size]} bg-surface border border-outline-variant/60 rounded-3xl shadow-2xl relative z-10 flex flex-col max-h-[90vh] overflow-hidden`}
          >
            {/* Header Area */}
            {(title || icon) && (
              <div className="flex justify-between items-start p-6 border-b border-outline-variant/35 bg-surface">
                <div className="flex gap-4">
                  {icon && (
                    <div className="p-3 bg-primary/10 rounded-2xl text-primary flex-shrink-0">
                      {icon}
                    </div>
                  )}
                  <div className="space-y-1">
                    <h3 className="text-lg font-black text-on-surface tracking-tight">{title}</h3>
                    {description && (
                      <p className="text-xs text-on-surface/60 font-medium leading-relaxed">{description}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-full hover:bg-surface-variant text-on-surface/40 hover:text-on-surface transition duration-200"
                  aria-label="Close dialog"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            )}

            {/* Content Area with custom scrollbar */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 text-on-surface select-text">
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
export default AdminDialog;
