// src/features/navigation/components/dialogs/DialogPrimitives.tsx

import React from "react";
import { AlertCircle } from "lucide-react";

// --- Form Section wrapper ---
interface DialogSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const DialogSection: React.FC<DialogSectionProps> = ({
  title,
  description,
  children
}) => {
  return (
    <div className="space-y-4">
      <div className="border-b border-outline-variant/35 pb-2">
        <h4 className="text-sm font-extrabold text-on-surface tracking-tight">{title}</h4>
        {description && (
          <p className="text-[11px] text-on-surface/50 mt-0.5 leading-relaxed font-semibold">
            {description}
          </p>
        )}
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
};

// --- Form Grid container (2 columns desktop, 1 column mobile) ---
interface DialogFormGridProps {
  children: React.ReactNode;
}

export const DialogFormGrid: React.FC<DialogFormGridProps> = ({ children }) => {
  return <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{children}</div>;
};

// --- Form Input Wrapper with labels and inline errors ---
interface DialogFormInputProps {
  label: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  children: React.ReactNode;
}

export const DialogFormInput: React.FC<DialogFormInputProps> = ({
  label,
  error,
  helperText,
  required,
  children
}) => {
  return (
    <div className="space-y-1.5 text-left w-full">
      <label className="text-xs font-bold text-on-surface/75 flex items-center gap-1.5">
        {label}
        {required && <span className="text-error font-black">*</span>}
      </label>
      <div className="relative">{children}</div>
      {error ? (
        <p className="text-[10px] text-error font-semibold flex items-center gap-1">
          <AlertCircle className="w-3 h-3 flex-shrink-0" />
          {error}
        </p>
      ) : helperText ? (
        <p className="text-[10px] text-on-surface/45 leading-relaxed font-medium">
          {helperText}
        </p>
      ) : null}
    </div>
  );
};

// --- Dialog Sticky Footer containing buttons ---
interface DialogFooterProps {
  children: React.ReactNode;
}

export const DialogFooter: React.FC<DialogFooterProps> = ({ children }) => {
  return (
    <div className="flex justify-end items-center gap-3 pt-4 border-t border-outline-variant/35 mt-6">
      {children}
    </div>
  );
};

// --- Form Actions styling constants ---
export const inputClasses = (hasError = false) => `
  w-full p-2.5 bg-surface border rounded-xl text-xs text-on-surface placeholder:text-on-surface/35 
  focus:outline-none focus:ring-2 transition duration-200
  ${
    hasError
      ? "border-error focus:border-error focus:ring-error/25 bg-error/5"
      : "border-outline-variant hover:border-on-surface/30 focus:border-primary focus:ring-primary/20"
  }
`;

export const selectClasses = (hasError = false) => `
  w-full p-2.5 bg-surface border rounded-xl text-xs text-on-surface/85 focus:outline-none focus:ring-2 transition duration-200
  ${
    hasError
      ? "border-error focus:border-error focus:ring-error/25 bg-error/5"
      : "border-outline-variant hover:border-on-surface/30 focus:border-primary focus:ring-primary/20"
  }
`;

export const checkboxClasses = `
  w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary bg-surface/50 transition duration-150
`;
