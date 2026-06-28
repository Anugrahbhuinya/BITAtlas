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
    <div className="min-h-screen w-screen flex items-center justify-center bg-background px-4 font-sans text-on-surface select-text overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md matte-card rounded-2xl p-8"
      >
        {/* Card Header branding */}
        <div className="flex flex-col items-center text-center mb-8 select-none">
          <div className="p-3 bg-surface-container border border-outline-variant rounded-xl text-primary mb-4">
            <Shield className="w-6 h-6 text-primary" />
          </div>
          <h2 className="text-xl font-bold uppercase tracking-wider text-primary">
            BIT Operations Center
          </h2>
          <p className="text-on-surface-variant mt-1.5 text-xs">
            Sign in to manage knowledge base and assistant models
          </p>
        </div>

        {/* Form elements */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Username Input */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
              Username
            </label>
            <div className="relative flex items-center">
              <User className="absolute left-3.5 w-4 h-4 text-on-surface-variant/50" />
              <input
                type="text"
                placeholder="Enter admin username"
                {...register("username", { required: "Username is required" })}
                className={`w-full pl-11 pr-4 py-3 bg-surface-container border rounded-xl text-xs font-semibold placeholder:text-on-surface-variant/20 focus:outline-none transition-all ${
                  errors.username
                    ? "border-rose-500/50 focus:border-rose-500"
                    : "border-outline-variant focus:border-primary"
                }`}
              />
            </div>
            {errors.username && (
              <span className="text-[10px] text-rose-400 font-bold uppercase tracking-wider pl-1">
                {errors.username.message}
              </span>
            )}
          </div>

          {/* Password Input */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
              Password
            </label>
            <div className="relative flex items-center">
              <Lock className="absolute left-3.5 w-4 h-4 text-on-surface-variant/50" />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                {...register("password", { required: "Password is required" })}
                className={`w-full pl-11 pr-11 py-3 bg-surface-container border rounded-xl text-xs font-semibold placeholder:text-on-surface-variant/20 focus:outline-none transition-all ${
                  errors.password
                    ? "border-rose-500/50 focus:border-rose-500"
                    : "border-outline-variant focus:border-primary"
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 text-on-surface-variant hover:text-primary cursor-pointer p-0.5 rounded select-none"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && (
              <span className="text-[10px] text-rose-400 font-bold uppercase tracking-wider pl-1">
                {errors.password.message}
              </span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-5 mt-6 bg-primary text-background font-bold text-xs uppercase tracking-wider rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50 disabled:pointer-events-none group select-none shadow-md"
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

export default AdminLoginPage;
