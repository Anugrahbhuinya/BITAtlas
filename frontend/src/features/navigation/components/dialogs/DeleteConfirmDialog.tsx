// src/features/navigation/components/dialogs/DeleteConfirmDialog.tsx

import React from "react";
import { ShieldAlert, Loader2 } from "lucide-react";
import { AdminDialog } from "./AdminDialog";
import { DialogFooter } from "./DialogPrimitives";

interface DeleteConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  loading?: boolean;
}

export const DeleteConfirmDialog: React.FC<DeleteConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Delete Entity",
  loading = false
}) => {
  return (
    <AdminDialog
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      description="This action requires administrator authorization."
      icon={<ShieldAlert className="w-6 h-6 text-error animate-pulse" />}
      size="sm"
      closeOnOutsideClick={!loading}
    >
      <div className="space-y-4">
        {/* Warning text body */}
        <p className="text-xs text-on-surface/75 leading-relaxed font-semibold">
          {description}
        </p>

        <div className="bg-error/5 border border-error/25 p-3 rounded-2xl flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
          <div className="text-[10px] text-error font-extrabold leading-normal uppercase tracking-wider">
            Warning: This action is permanent and cannot be undone. All child relations will lose this reference.
          </div>
        </div>

        {/* Buttons footer */}
        <DialogFooter>
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 border border-outline-variant/60 hover:bg-surface-variant text-on-surface/75 text-xs font-bold rounded-xl transition duration-200 disabled:opacity-40"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 bg-error hover:bg-error/90 text-on-primary text-xs font-black rounded-xl shadow-lg transition duration-200 disabled:opacity-40"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Deleting...
              </>
            ) : (
              confirmText
            )}
          </button>
        </DialogFooter>
      </div>
    </AdminDialog>
  );
};
export default DeleteConfirmDialog;
