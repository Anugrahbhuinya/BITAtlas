import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, Navigate } from "react-router-dom";
import { useAdminStore } from "../hooks/adminStore";
import adminApi from "../services/api";
import { motion } from "framer-motion";
import { Shield, Lock, User, Eye, EyeOff, Loader2, ArrowRight } from "lucide-react";

export const AdminLoginPage = () => {
  const { isAuthenticated, setLogin, showToast } = useAdminStore();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      username: "",
      password: "",
    },
  });

  // If already logged in, redirect directly to dashboard
  if (isAuthenticated) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      const response = await adminApi.post("/api/admin/login", data);
      const { access_token, username } = response.data;
      
      // Update global Zustand store
      setLogin(access_token, username);
      showToast("Access granted. Welcome back!", "success");
      navigate("/admin/dashboard");
    } catch (e: any) {
      console.error(e);
      const errorMsg = e.response?.data?.detail || "Authentication failed. Check credentials.";
      showToast(errorMsg, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-screen flex items-center justify-center bg-slate-950 text-slate-100 overflow-hidden px-4">
      {/* Background design glow lights */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-[400px] h-[400px] bg-violet-600/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Main glass card panel */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-md glass-panel p-8 rounded-3xl shadow-2xl border border-white/5 relative z-10 overflow-hidden"
      >
        {/* Subtle accent glow bar on top */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-500" />

        {/* Card Header branding */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="p-3 bg-blue-600 rounded-2xl text-white glow-blue shadow-lg mb-4">
            <Shield className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-100 text-glow">
            BIT Operations Center
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Sign in to manage knowledge base and assistant models
          </p>
        </div>

        {/* Form elements */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Username Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Username
            </label>
            <div className="relative flex items-center">
              <User className="absolute left-3.5 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Enter admin username"
                {...register("username", { required: "Username is required" })}
                className={`w-full pl-11 pr-4 py-3 bg-slate-900/60 border rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none transition-all ${
                  errors.username
                    ? "border-rose-500/50 focus:ring-1 focus:ring-rose-500/30"
                    : "border-slate-800 focus:border-blue-500/60 focus:ring-1 focus:ring-blue-500/20"
                }`}
              />
            </div>
            {errors.username && (
              <span className="text-[10px] text-rose-400 font-medium pl-1">
                {errors.username.message}
              </span>
            )}
          </div>

          {/* Password Input */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-300">
                Password
              </label>
            </div>
            <div className="relative flex items-center">
              <Lock className="absolute left-3.5 w-4 h-4 text-slate-500" />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                {...register("password", { required: "Password is required" })}
                className={`w-full pl-11 pr-11 py-3 bg-slate-900/60 border rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none transition-all ${
                  errors.password
                    ? "border-rose-500/50 focus:ring-1 focus:ring-rose-500/30"
                    : "border-slate-800 focus:border-blue-500/60 focus:ring-1 focus:ring-blue-500/20"
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 text-slate-400 hover:text-slate-200 cursor-pointer p-0.5 rounded"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && (
              <span className="text-[10px] text-rose-400 font-medium pl-1">
                {errors.password.message}
              </span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-semibold shadow-lg hover:shadow-blue-500/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:pointer-events-none mt-6 group"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authorizing...</span>
              </>
            ) : (
              <>
                <span>Access Console</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </>
            )}
          </button>
        </form>
      </motion.div>
    </div>
  );
};
