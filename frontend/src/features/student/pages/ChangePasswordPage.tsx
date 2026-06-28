import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Lock, ArrowLeft, ShieldAlert, CheckCircle2, Loader2, ArrowRight } from "lucide-react";
import studentService from "../services/studentService";

export const ChangePasswordPage = () => {
  const navigate = useNavigate();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!currentPassword || !newPassword || !confirmPassword) {
      setErrorMsg("Please fill in all fields.");
      return;
    }

    if (newPassword.length < 6) {
      setErrorMsg("New password must be at least 6 characters.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMsg("New password and confirm password do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      await studentService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccessMsg("Password changed successfully! Redirecting...");
      setTimeout(() => {
        navigate("/profile");
      }, 2000);
    } catch (err: any) {
      console.error("Change password error:", err);
      const msg = err.response?.data?.detail || "Failed to change password. Verify your current password.";
      setErrorMsg(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto custom-scrollbar bg-background">
      <div className="max-w-[600px] mx-auto px-6 py-8 space-y-8 text-on-surface font-sans select-text">
      
      {/* Back button */}
      <div className="mb-4 select-none">
        <Link to="/profile" className="inline-flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors text-xs font-bold uppercase tracking-wider">
          <ArrowLeft size={14} />
          <span>Back to Profile</span>
        </Link>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="matte-card rounded-2xl p-6 md:p-8"
      >
        <div className="flex items-center gap-3 mb-6 pb-3 border-b border-outline-variant/30 select-none">
          <div className="p-2 bg-surface-container rounded-lg border border-outline-variant text-primary">
            <Lock size={16} />
          </div>
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-primary">Change Password</h2>
            <p className="text-[10px] text-on-surface-variant mt-0.5">Protect your student portal account.</p>
          </div>
        </div>

        {errorMsg && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-2.5 text-red-400 text-xs">
            <ShieldAlert size={14} className="shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-start gap-2.5 text-emerald-400 text-xs">
            <CheckCircle2 size={14} className="shrink-0 mt-0.5" />
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Current Password */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
              Current Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
            />
          </div>

          {/* New Password */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
              New Password
            </label>
            <input
              type="password"
              placeholder="Minimum 6 characters"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
            />
          </div>

          {/* Confirm Password */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
              Confirm New Password
            </label>
            <input
              type="password"
              placeholder="Re-type new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 px-4 mt-6 bg-primary text-background hover:bg-primary/90 font-bold text-xs uppercase tracking-wider rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-1.5 group cursor-pointer disabled:opacity-50 disabled:pointer-events-none select-none"
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <span>Change Password</span>
                <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
              </>
            )}
          </button>
        </form>
      </motion.div>
      </div>
    </div>
  );
};

export default ChangePasswordPage;
