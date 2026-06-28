import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { UserPlus, ArrowRight, ShieldAlert, CheckCircle } from "lucide-react";
import useAuth from "../hooks/useAuth";

export const RegisterPage = () => {
  const { registerStudent } = useAuth();
  const navigate = useNavigate();

  // Field states
  const [rollNumber, setRollNumber] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [department, setDepartment] = useState("");
  const [program, setProgram] = useState("");
  const [year, setYear] = useState(1);
  const [semester, setSemester] = useState(1);
  const [section, setSection] = useState("");

  const [formError, setFormError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccessMsg(null);

    // Validate inputs
    if (
      !rollNumber ||
      !name ||
      !email ||
      !password ||
      !department ||
      !program ||
      !section
    ) {
      setFormError("Please fill in all fields.");
      return;
    }

    if (password.length < 6) {
      setFormError("Password must be at least 6 characters.");
      return;
    }

    const payload = {
      roll_number: rollNumber.trim(),
      name: name.trim(),
      email: email.trim(),
      password,
      department: department.trim(),
      program: program.trim(),
      year: Number(year),
      semester: Number(semester),
      section: section.trim().toUpperCase(),
    };

    setIsSubmitting(true);
    try {
      await registerStudent(payload);
      setSuccessMsg("Registration successful! Redirecting to login...");
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err: any) {
      console.error("Registration failed:", err);
      const msg = err.response?.data?.detail || "Registration failed. Please verify your details.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-background p-4 font-sans text-on-surface select-text overflow-y-auto py-12">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-2xl matte-card rounded-2xl p-8"
      >
        {/* Header */}
        <div className="text-center mb-8 select-none">
          <div className="inline-flex p-3 bg-surface-container border border-outline-variant rounded-xl text-primary mb-4">
            <UserPlus className="w-6 h-6 text-primary" />
          </div>
          <h2 className="text-xl font-bold uppercase tracking-wider text-primary">
            Student Registration
          </h2>
          <p className="text-on-surface-variant mt-1.5 text-xs">
            Create your account to access the AI Portal
          </p>
        </div>

        {/* Error notification */}
        {formError && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-2.5 text-red-400 text-xs font-semibold">
            <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{formError}</span>
          </div>
        )}

        {/* Success notification */}
        {successMsg && (
          <div className="mb-6 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-start gap-2.5 text-emerald-400 text-xs font-semibold">
            <CheckCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Grid Layout for Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Full Name */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                Full Name
              </label>
              <input
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>

            {/* Roll Number */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                Roll Number
              </label>
              <input
                type="text"
                placeholder="BTECH/10001/22"
                value={rollNumber}
                onChange={(e) => setRollNumber(e.target.value)}
                required
                className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                Email Address
              </label>
              <input
                type="email"
                placeholder="john.doe@bitmesra.ac.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                Password
              </label>
              <input
                type="password"
                placeholder="Minimum 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>

            {/* Department */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                Department
              </label>
              <input
                type="text"
                placeholder="Computer Science & Engineering"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                required
                className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>

            {/* Program */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                Program
              </label>
              <input
                type="text"
                placeholder="B.Tech / MCA / M.Tech"
                value={program}
                onChange={(e) => setProgram(e.target.value)}
                required
                className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>

            {/* Year & Semester Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                  Year
                </label>
                <select
                  value={year}
                  onChange={(e) => setYear(Number(e.target.value))}
                  className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface text-xs font-semibold cursor-pointer"
                >
                  <option value={1}>1st Year</option>
                  <option value={2}>2nd Year</option>
                  <option value={3}>3rd Year</option>
                  <option value={4}>4th Year</option>
                  <option value={5}>5th Year</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                  Semester
                </label>
                <select
                  value={semester}
                  onChange={(e) => setSemester(Number(e.target.value))}
                  className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface text-xs font-semibold cursor-pointer"
                >
                  {[...Array(10)].map((_, i) => (
                    <option key={i+1} value={i+1}>Sem {i+1}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Section */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">
                Section
              </label>
              <input
                type="text"
                placeholder="A / B / C"
                value={section}
                onChange={(e) => setSection(e.target.value)}
                required
                className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface placeholder:text-on-surface-variant/20 text-xs font-semibold"
              />
            </div>

          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 px-5 mt-6 bg-primary text-background font-bold text-xs uppercase tracking-wider rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-1.5 group cursor-pointer disabled:opacity-50 disabled:pointer-events-none select-none shadow-md"
          >
            {isSubmitting ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-background border-t-transparent"></div>
            ) : (
              <>
                <span>Register Account</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
              </>
            )}
          </button>
        </form>

        {/* Footer info */}
        <div className="mt-8 text-center border-t border-outline-variant/30 pt-6 select-none">
          <p className="text-xs text-on-surface-variant">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-primary hover:underline font-bold uppercase tracking-wider ml-1"
            >
              Login here
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default RegisterPage;
