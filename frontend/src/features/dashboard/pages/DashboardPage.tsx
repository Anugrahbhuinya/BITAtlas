import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { 
  Bolt, AlertCircle, 
  Clock, ArrowRight, Sparkles, CalendarRange 
} from "lucide-react";
import { useAuth } from "../../auth/hooks/useAuth";
import { ImportantContactsCard } from "../components/ImportantContactsCard";

export const DashboardPage = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  const [greeting] = useState(() => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 17) return "Good Afternoon";
    return "Good Evening";
  });

  const handleQuickAction = (promptText: string) => {
    // Navigate to Chat page and pass promptText in location state
    navigate("/chat", { state: { prefilledPrompt: promptText } });
  };

  const getFirstName = (fullName?: string) => {
    if (!fullName) return "Student";
    return fullName.split(" ")[0];
  };

  return (
    <div className="h-full overflow-y-auto custom-scrollbar bg-background">
      <div className="max-w-[1200px] mx-auto px-6 py-10 space-y-10 text-on-surface font-sans">
        {/* Hero Greeting */}
        <section className="mb-2">
          <h2 className="text-3xl md:text-4xl font-extrabold text-primary tracking-tight">
            {greeting}, {getFirstName(currentUser?.name)} 👋
          </h2>
          <p className="text-on-surface-variant mt-2 text-xs md:text-sm uppercase tracking-wider font-bold opacity-60">
            Welcome to the BITATLAS student workspace.
          </p>
        </section>

        {/* Bento Grid Layout - Increased whitespace with gap-8 */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          
          {/* Today's Schedule (Styled Timeline Card) */}
          <div className="md:col-span-8 border border-outline-variant/40 bg-surface-container-low rounded-2xl p-6 flex flex-col justify-between min-h-[360px] hover:border-outline transition-colors duration-200">
            <div>
              <div className="flex justify-between items-center mb-6 border-b border-outline-variant/30 pb-4">
                <div className="flex items-center gap-3">
                  <CalendarRange className="w-5 h-5 text-primary" />
                  <h3 className="text-sm font-extrabold text-primary uppercase tracking-wider">Today's Schedule</h3>
                </div>
                <span className="text-[10px] text-on-surface-variant font-mono-code font-bold uppercase tracking-wider">Monday, Oct 23</span>
              </div>

              <div className="relative border-l border-outline-variant/40 pl-6 ml-3 space-y-6">
                {/* Active class */}
                <div className="relative">
                  <div className="absolute -left-[22px] top-1.5 w-3 h-3 rounded-full bg-primary ring-4 ring-primary/20"></div>
                  <div className="flex flex-col md:flex-row md:items-center gap-2 justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-primary uppercase tracking-wider">Machine Learning (L-302)</h4>
                      <p className="text-[11px] text-on-surface-variant mt-0.5">Prof. K. Sharma &bull; 50 mins left</p>
                    </div>
                    <span className="text-[9px] font-mono bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-bold uppercase tracking-wider self-start md:self-auto">Now</span>
                  </div>
                </div>

                {/* Upcoming class */}
                <div className="relative">
                  <div className="absolute -left-[22px] top-1.5 w-3 h-3 rounded-full bg-outline-variant"></div>
                  <div className="flex flex-col md:flex-row md:items-center gap-2 justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Data Structures Lab</h4>
                      <p className="text-[11px] text-on-surface-variant mt-0.5">Dept. IT &bull; Lab 4</p>
                    </div>
                    <span className="text-[9px] font-mono-code text-on-surface-variant uppercase font-medium">11:30 AM</span>
                  </div>
                </div>

                {/* Later class */}
                <div className="relative opacity-60">
                  <div className="absolute -left-[22px] top-1.5 w-3 h-3 rounded-full bg-outline-variant/60"></div>
                  <div className="flex flex-col md:flex-row md:items-center gap-2 justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Minor Project Review</h4>
                      <p className="text-[11px] text-on-surface-variant mt-0.5">Seminar Hall 1</p>
                    </div>
                    <span className="text-[9px] font-mono-code text-on-surface-variant uppercase font-medium">02:30 PM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick AI Actions (Clean Pill Button Card) */}
          <div className="md:col-span-4 matte-card rounded-2xl p-6 flex flex-col justify-between min-h-[360px]">
            <div>
              <div className="flex items-center gap-3 mb-6 border-b border-outline-variant/30 pb-4">
                <Bolt className="w-5 h-5 text-primary" />
                <h3 className="text-sm font-extrabold text-primary uppercase tracking-wider">Quick Actions</h3>
              </div>
              <div className="space-y-3">
                {[
                  "Ask about Syllabus",
                  "Exam Seat Plan",
                  "Library Availability",
                  "Bus Timings"
                ].map((act) => (
                  <button
                    key={act}
                    onClick={() => handleQuickAction(act)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-surface-container hover:bg-primary text-primary hover:text-background rounded-xl transition-all duration-150 group cursor-pointer border border-transparent hover:border-outline-variant"
                  >
                    <span className="text-[10px] font-extrabold uppercase tracking-wider">{act}</span>
                    <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Unread Notices Feed Card */}
          <div className="md:col-span-5 border border-outline-variant/40 bg-surface-container-low rounded-2xl p-6 flex flex-col justify-between hover:border-outline transition-colors duration-200">
            <div>
              <div className="flex justify-between items-center mb-6 border-b border-outline-variant/30 pb-4">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-primary" />
                  <h3 className="text-sm font-extrabold text-primary uppercase tracking-wider">Notices Feed</h3>
                </div>
                <span className="bg-primary text-background text-[9px] px-2 py-0.5 rounded font-extrabold uppercase tracking-wider">3 New</span>
              </div>

              <div className="space-y-6">
                <Link to="/notices" className="block group space-y-1.5">
                  <div className="flex items-center gap-2 text-[9px] text-on-surface-variant font-mono-code font-bold uppercase tracking-wider">
                    <span>Office of Registrar</span>
                    <span>&bull;</span>
                    <span>2h ago</span>
                  </div>
                  <h4 className="text-xs font-bold text-primary group-hover:underline leading-snug">Re-registration for Winter Semester 2024</h4>
                </Link>
                
                <Link to="/notices" className="block group space-y-1.5">
                  <div className="flex items-center gap-2 text-[9px] text-on-surface-variant font-mono-code font-bold uppercase tracking-wider">
                    <span>Hostel Committee</span>
                    <span>&bull;</span>
                    <span>5h ago</span>
                  </div>
                  <h4 className="text-xs font-bold text-primary group-hover:underline leading-snug">Maintenance schedule: Hostel 10 & 11</h4>
                </Link>

                <Link to="/notices" className="block group space-y-1.5">
                  <div className="flex items-center gap-2 text-[9px] text-on-surface-variant font-mono-code font-bold uppercase tracking-wider">
                    <span>T&P Cell</span>
                    <span>&bull;</span>
                    <span>Yesterday</span>
                  </div>
                  <h4 className="text-xs font-bold text-primary group-hover:underline leading-snug">Internship Drive: Google Cloud (2025 batch)</h4>
                </Link>
              </div>
            </div>
          </div>

          {/* Academic Calendar highlights */}
          <div className="md:col-span-4 matte-card rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-3 mb-6 border-b border-outline-variant/30 pb-4">
                <Clock className="w-5 h-5 text-primary" />
                <h3 className="text-sm font-extrabold text-primary uppercase tracking-wider">Key Dates</h3>
              </div>

              <div className="space-y-6">
                <div className="flex gap-4 items-center">
                  <div className="flex flex-col items-center justify-center w-12 h-12 bg-surface-container rounded-lg border border-outline-variant shrink-0 select-none">
                    <span className="text-[9px] text-on-surface-variant uppercase font-extrabold leading-none">Nov</span>
                    <span className="text-sm font-extrabold text-primary leading-none mt-1">05</span>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-primary leading-tight uppercase tracking-wide">Mid-Sem Start</h4>
                    <p className="text-[10px] text-on-surface-variant mt-0.5 font-medium">Major Academic Event</p>
                  </div>
                </div>

                <div className="flex gap-4 items-center">
                  <div className="flex flex-col items-center justify-center w-12 h-12 bg-surface-container rounded-lg border border-outline-variant shrink-0 select-none">
                    <span className="text-[9px] text-on-surface-variant uppercase font-extrabold leading-none">Nov</span>
                    <span className="text-sm font-extrabold text-primary leading-none mt-1">12</span>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-primary leading-tight uppercase tracking-wide">Diwali Break</h4>
                    <p className="text-[10px] text-on-surface-variant mt-0.5 font-medium">University Closed</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Important Contacts Widget */}
          <ImportantContactsCard />

        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
