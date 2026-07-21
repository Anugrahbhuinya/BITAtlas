import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock, ArrowRight, ShieldAlert, GraduationCap, Eye, EyeOff } from "lucide-react";
import useAuth from "../hooks/useAuth";

export const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!email || !password) {
      setFormError("Please fill in all fields.");
      return;
    }

    setIsSubmitting(true);
    try {
      await login({ email, password }, rememberMe);
      navigate("/");
    } catch (err: unknown) {
      console.error("Login failed:", err);
      const errorDetails = err as { response?: { data?: { detail?: string } } };
      const msg = errorDetails.response?.data?.detail || "Invalid email or password. Please try again.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-background p-4 font-sans text-on-surface select-text overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md matte-card rounded-2xl p-8"
      >
        {/* Brand Header */}
        <div className="text-center mb-8 select-none">
          <div className="inline-flex p-3 bg-surface-container border border-outline-variant rounded-xl text-primary mb-4">
            <GraduationCap className="w-6 h-6 text-primary" />
          </div>
          <h2 className="text-xl font-bold uppercase tracking-wider text-primary">
            Student Login
          </h2>
          <p className="text-on-surface-variant mt-1.5 text-xs">
            Access the BITATLAS Campus Assistant
          </p>
        </div>

        {/* Error notification */}
        {formError && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-2.5 text-red-400 text-xs font-semibold">
            <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{formError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email field */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant/50" />
              <input
                type="email"
                placeholder="student@bitmesra.ac.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-11 pr-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>
          </div>

          {/* Password field */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant/50" />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-11 pr-12 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-on-surface-variant/50 hover:text-primary transition-colors cursor-pointer p-1 rounded-lg focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary flex items-center justify-center"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Remember session checkbox */}
          <div className="flex items-center justify-between text-xs py-2 select-none">
            <label className="flex items-center gap-2 cursor-pointer text-on-surface-variant hover:text-primary">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 accent-primary bg-surface-container border-outline-variant rounded focus:ring-0 cursor-pointer"
              />
              <span>Remember session</span>
            </label>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 px-5 mt-4 bg-primary text-background font-bold text-xs uppercase tracking-wider rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-1.5 group cursor-pointer disabled:opacity-50 disabled:pointer-events-none select-none shadow-md"
          >
            {isSubmitting ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-background border-t-transparent"></div>
            ) : (
              <>
                <span>Login</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
              </>
            )}
          </button>
        </form>

        {/* Footer info */}
        <div className="mt-8 text-center border-t border-outline-variant/30 pt-6 select-none">
          <p className="text-xs text-on-surface-variant">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="text-primary hover:underline font-bold uppercase tracking-wider ml-1"
            >
              Register here
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
