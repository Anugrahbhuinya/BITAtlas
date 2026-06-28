import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { 
  Calendar as CalendarIcon, Bolt, AlertCircle, 
  Clock, ArrowRight, Sparkles, MapPin, 
  BookOpen, CalendarRange 
} from "lucide-react";
import { useAuth } from "../../auth/hooks/useAuth";

export const DashboardPage = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  const [greeting, setGreeting] = useState("Hello");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning");
    else if (hour < 17) setGreeting("Good Afternoon");
    else setGreeting("Good Evening");
  }, []);

  const handleQuickAction = (promptText: string) => {
    // Navigate to Chat page and pass promptText in location state
    navigate("/chat", { state: { prefilledPrompt: promptText } });
  };

  const getFirstName = (fullName?: string) => {
    if (!fullName) return "Student";
    return fullName.split(" ")[0];
  };

  return (
    <div className="max-w-[1200px] mx-auto px-6 py-8 space-y-8 text-on-surface font-sans">
      {/* Hero Greeting */}
      <section className="mb-6">
        <h2 className="text-3xl md:text-4xl font-extrabold text-primary tracking-tight">
          {greeting}, {getFirstName(currentUser?.name)} 👋
        </h2>
        <p className="text-on-surface-variant mt-1.5 text-sm md:text-base">
          Your personalized AI campus assistant.
        </p>
      </section>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        
        {/* Today's Schedule */}
        <div className="md:col-span-8 matte-card rounded-2xl p-6 flex flex-col min-h-[320px]">
          <div className="flex justify-between items-center mb-6 border-b border-outline-variant/30 pb-3">
            <div className="flex items-center gap-3">
              <CalendarRange className="w-5 h-5 text-primary" />
              <h3 className="text-base font-bold text-primary">Today's Schedule</h3>
            </div>
            <span className="text-xs text-on-surface-variant font-medium">Monday, Oct 23</span>
          </div>

          <div className="space-y-4 flex-1">
            <div className="flex items-center gap-4 p-4 bg-surface-container rounded-xl border border-transparent hover:border-outline-variant transition-all duration-150">
              <div className="text-center min-w-[60px]">
                <span className="block text-xs font-bold text-on-surface">09:00</span>
                <span className="block text-[10px] text-on-surface-variant font-semibold">AM</span>
              </div>
              <div className="w-1 h-10 bg-primary rounded-full"></div>
              <div className="flex-1">
                <h4 className="text-sm font-bold text-primary">Machine Learning (L-302)</h4>
                <p className="text-xs text-on-surface-variant">Prof. K. Sharma &bull; 50 mins left</p>
              </div>
            </div>

            <div className="flex items-center gap-4 p-4 bg-surface-container/50 rounded-xl">
              <div className="text-center min-w-[60px]">
                <span className="block text-xs font-bold text-on-surface">11:30</span>
                <span className="block text-[10px] text-on-surface-variant font-semibold">AM</span>
              </div>
              <div className="w-1 h-10 bg-outline-variant rounded-full"></div>
              <div className="flex-1">
                <h4 className="text-sm font-bold text-primary">Data Structures Lab</h4>
                <p className="text-xs text-on-surface-variant">Dept. IT &bull; Lab 4</p>
              </div>
            </div>

            <div className="flex items-center gap-4 p-4 bg-surface-container/50 rounded-xl opacity-60">
              <div className="text-center min-w-[60px]">
                <span className="block text-xs font-bold text-on-surface">02:30</span>
                <span className="block text-[10px] text-on-surface-variant font-semibold">PM</span>
              </div>
              <div className="w-1 h-10 bg-outline-variant rounded-full"></div>
              <div className="flex-1">
                <h4 className="text-sm font-bold text-primary">Minor Project Review</h4>
                <p className="text-xs text-on-surface-variant">Seminar Hall 1</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick AI Actions */}
        <div className="md:col-span-4 matte-card rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-6 border-b border-outline-variant/30 pb-3">
              <Bolt className="w-5 h-5 text-primary" />
              <h3 className="text-base font-bold text-primary">Quick Actions</h3>
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
                  className="w-full flex items-center justify-between p-4 bg-surface-container hover:bg-primary text-primary hover:text-background rounded-xl transition-all duration-150 group cursor-pointer border border-transparent hover:border-outline-variant"
                >
                  <span className="text-xs font-bold uppercase tracking-wider">{act}</span>
                  <ArrowRight size={14} className="transition-transform group-hover:translate-x-1" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Unread Notices */}
        <div className="md:col-span-5 matte-card rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-6 border-b border-outline-variant/30 pb-3">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-primary" />
                <h3 className="text-base font-bold text-primary">Unread Notices</h3>
              </div>
              <span className="bg-primary text-background text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">3 NEW</span>
            </div>

            <div className="space-y-4">
              <Link to="/notices" className="block group">
                <p className="text-[10px] text-on-surface-variant mb-1 font-mono-code">Office of Registrar &bull; 2h ago</p>
                <h4 className="text-xs font-bold text-primary group-hover:underline leading-snug">Re-registration for Winter Semester 2024</h4>
                <div className="divider mt-4"></div>
              </Link>
              
              <Link to="/notices" className="block group">
                <p className="text-[10px] text-on-surface-variant mb-1 font-mono-code">Hostel Committee &bull; 5h ago</p>
                <h4 className="text-xs font-bold text-primary group-hover:underline leading-snug">Maintenance schedule: Hostel 10 & 11</h4>
                <div className="divider mt-4"></div>
              </Link>

              <Link to="/notices" className="block group">
                <p className="text-[10px] text-on-surface-variant mb-1 font-mono-code">T&P Cell &bull; Yesterday</p>
                <h4 className="text-xs font-bold text-primary group-hover:underline leading-snug">Internship Drive: Google Cloud (2025 batch)</h4>
              </Link>
            </div>
          </div>
        </div>

        {/* Academic Calendar */}
        <div className="md:col-span-4 matte-card rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6 border-b border-outline-variant/30 pb-3">
            <Clock className="w-5 h-5 text-primary" />
            <h3 className="text-base font-bold text-primary">Calendar</h3>
          </div>

          <div className="space-y-5">
            <div className="flex gap-4 items-center">
              <div className="flex flex-col items-center justify-center w-12 h-12 bg-surface-container rounded-lg border border-outline-variant shrink-0">
                <span className="text-[9px] text-on-surface-variant uppercase font-bold leading-none">Nov</span>
                <span className="text-base font-bold text-primary leading-none mt-1">05</span>
              </div>
              <div>
                <h4 className="text-xs font-bold text-primary leading-tight">Mid-Sem Exams Start</h4>
                <p className="text-[10px] text-on-surface-variant mt-0.5">Major Academic Event</p>
              </div>
            </div>

            <div className="flex gap-4 items-center">
              <div className="flex flex-col items-center justify-center w-12 h-12 bg-surface-container rounded-lg border border-outline-variant shrink-0">
                <span className="text-[9px] text-on-surface-variant uppercase font-bold leading-none">Nov</span>
                <span className="text-base font-bold text-primary leading-none mt-1">12</span>
              </div>
              <div>
                <h4 className="text-xs font-bold text-primary leading-tight">Diwali Break Begins</h4>
                <p className="text-[10px] text-on-surface-variant mt-0.5">University Closed</p>
              </div>
            </div>
          </div>
        </div>

        {/* Upcoming Events */}
        <div className="md:col-span-3 matte-card rounded-2xl overflow-hidden group flex flex-col justify-between">
          <div className="h-28 w-full bg-surface-container relative shrink-0">
            <div 
              className="absolute inset-0 bg-cover bg-center" 
              style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuA6jyadCZR1GKdeUoRfOjlvm72Bk2GeRQOuF71hOSO8zMsn14XRRXhTSLG9YsNz3vZVYBwfmxSXPMXOhETm1Qi2HfQJ8ehYPi43gwKD0an1BSh6Jru28pQ4x9KkN1PYdpK141vLNLt3mxsG-kAW9gVrx5lKpGMF7Uyr9uaLK6LdR-nNJnmnI7Bg--dtZhW_9elaxs5Nw-4keF6xKRxlS9pIVtagOs6pBCtE4ltX57co2tbZfceZZ620')" }}
            ></div>
            <div className="absolute inset-0 bg-gradient-to-t from-[#18181B] to-transparent"></div>
          </div>
          <div className="p-4 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1 text-[10px] font-bold text-primary uppercase tracking-wider">
                <Sparkles size={10} />
                <span>Bitotsav '24</span>
              </div>
              <h4 className="text-xs font-bold text-primary mb-1 leading-tight">Volunteer Meetup</h4>
              <p className="text-[10px] text-on-surface-variant mb-4">CAT Hall &bull; 05:30 PM</p>
            </div>
            <button className="w-full py-2 border border-outline-variant hover:border-primary rounded-lg text-[10px] font-bold text-primary uppercase tracking-wider hover:bg-surface-variant transition-colors cursor-pointer active:scale-[0.98]">
              I'm Interested
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DashboardPage;
