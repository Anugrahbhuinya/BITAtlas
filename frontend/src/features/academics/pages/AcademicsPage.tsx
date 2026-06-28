import { 
  GraduationCap, TrendingUp, BookOpen, Clock, AlertCircle, ArrowRight
} from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export const AcademicsPage = () => {
  const activeCourses = [
    {
      code: "CS 601",
      name: "Advanced Algorithms",
      professor: "Dr. Arpit Bhardwaj",
      nextClass: "Next: Tuesday, 10:00 AM",
      iconColor: "text-emerald-400"
    },
    {
      code: "CS 603",
      name: "Distributed Systems",
      professor: "Prof. S. R. Sharma",
      nextClass: "Next: Today, 02:00 PM",
      iconColor: "text-blue-400"
    },
    {
      code: "CS 605",
      name: "Network Security",
      professor: "Dr. K. K. Sen",
      nextClass: "Next: Wednesday, 09:00 AM",
      iconColor: "text-purple-400"
    },
    {
      code: "CS 607",
      name: "Human Computer Interaction",
      professor: "Dr. P. Mallick",
      nextClass: "Next: Monday, 11:00 AM",
      iconColor: "text-amber-400"
    }
  ];

  return (
    <div className="h-full overflow-y-auto custom-scrollbar bg-background">
      <div className="max-w-[1200px] mx-auto px-6 py-8 space-y-12 text-on-surface font-sans select-text">
        
        {/* Hero Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {/* CGPA */}
          <div className="matte-card rounded-2xl p-6 flex flex-col justify-between h-[130px]">
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Current CGPA</span>
              <span className="text-3xl font-extrabold text-primary block mt-1">8.92</span>
            </div>
            <div className="flex items-center gap-1 text-emerald-400 mt-2">
              <TrendingUp size={14} />
              <span className="text-[10px] font-bold uppercase tracking-wider">+0.15 from last sem</span>
            </div>
          </div>

          {/* Semester */}
          <div className="matte-card rounded-2xl p-6 flex flex-col justify-between h-[130px]">
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Semester</span>
              <span className="text-3xl font-extrabold text-primary block mt-1">VI</span>
            </div>
            <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">B.Tech - CSE</span>
          </div>

          {/* Credits Done */}
          <div className="matte-card rounded-2xl p-6 flex flex-col justify-between h-[130px]">
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Credits Done</span>
              <span className="text-3xl font-extrabold text-primary block mt-1">124</span>
            </div>
            <div className="w-full bg-surface-container-high h-1 rounded-full mt-2">
              <div className="bg-primary h-1 rounded-full" style={{ width: "75%" }}></div>
            </div>
          </div>

          {/* Attendance */}
          <div className="matte-card rounded-2xl p-6 flex flex-col justify-between h-[130px]">
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Attendance</span>
              <span className="text-3xl font-extrabold text-primary block mt-1">91%</span>
            </div>
            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">Safe (Above 75%)</span>
          </div>
        </div>

        {/* Bento Layout Content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Active Courses Section (Large) */}
          <section className="col-span-12 lg:col-span-8 flex flex-col gap-6">
            <div className="flex justify-between items-end border-b border-outline-variant/30 pb-3">
              <h2 className="text-base font-bold text-primary uppercase tracking-wider">Active Courses</h2>
              <Link to="/chat" className="text-[10px] font-bold text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 uppercase tracking-wider">
                <span>View All</span>
                <ArrowRight size={10} />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeCourses.map((course, idx) => (
                <motion.div 
                  key={course.code} 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: idx * 0.05 }}
                  className="matte-card rounded-2xl p-6 group cursor-pointer flex flex-col justify-between h-[160px]"
                >
                  <div className="flex justify-between items-start">
                    <div className="bg-secondary-container p-2 rounded-xl border border-outline-variant">
                      <BookOpen size={16} className="text-primary" />
                    </div>
                    <span className="text-[9px] font-mono-code font-bold bg-surface-container-high border border-outline-variant px-2 py-0.5 rounded text-on-surface-variant">
                      {course.code}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-primary mb-0.5 leading-tight">{course.name}</h3>
                    <p className="text-[11px] text-on-surface-variant">{course.professor}</p>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t border-outline-variant/30 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">
                    <span>{course.nextClass}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </section>

          {/* Sidebar Content (Bento Side) */}
          <aside className="col-span-12 lg:col-span-4 flex flex-col gap-6">
            {/* Calendar / Upcoming Exams */}
            <div className="matte-card rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6 border-b border-outline-variant/30 pb-3">
                <h2 className="text-sm font-bold text-primary uppercase tracking-wider">Examinations</h2>
                <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Mid Semester</span>
              </div>
              
              <div className="space-y-4">
                {[
                  { date: "OCT 12", subject: "Compiler Design", room: "10:00 AM - 12:00 PM • LH-1" },
                  { date: "OCT 14", subject: "Data Warehousing", room: "02:00 PM - 04:00 PM • LH-2" },
                  { date: "OCT 16", subject: "Software Eng.", room: "10:00 AM - 12:00 PM • LH-4" }
                ].map((exam, i) => (
                  <div key={i} className="flex gap-4 items-center pb-4 border-b border-outline-variant/30 last:border-b-0 last:pb-0">
                    <div className="flex flex-col items-center bg-surface-container-high px-2.5 py-1.5 rounded-lg border border-outline-variant shrink-0 min-w-[50px]">
                      <span className="text-[9px] font-bold text-primary leading-none uppercase">{exam.date.split(" ")[0]}</span>
                      <span className="text-sm font-extrabold text-primary leading-none mt-1">{exam.date.split(" ")[1]}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-primary leading-snug">{exam.subject}</span>
                      <span className="text-[10px] text-on-surface-variant font-medium mt-0.5">{exam.room}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Academic Calendar Highlights */}
            <div className="matte-card rounded-2xl p-6 bg-surface-container/60 relative overflow-hidden group">
              <div className="relative z-10">
                <h3 className="text-sm font-bold text-primary uppercase tracking-wider mb-1">Calendar</h3>
                <p className="text-[11px] text-on-surface-variant mb-6">Upcoming campus events & deadlines.</p>
                
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0"></div>
                    <span className="text-xs text-on-surface leading-tight">Autumn Break starts 22nd Oct</span>
                  </div>
                  <div className="flex items-center gap-2 opacity-60">
                    <div className="w-1.5 h-1.5 rounded-full bg-outline shrink-0"></div>
                    <span className="text-xs text-on-surface leading-tight">Registration Open: Winter Sem</span>
                  </div>
                </div>
              </div>
            </div>
          </aside>

        </div>

        {/* Future Sections Placeholder */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-60 border-t border-outline-variant/30 pt-8 select-none">
          <div className="matte-card rounded-2xl p-6 border-dashed flex flex-col items-center justify-center text-center gap-3">
            <div className="w-10 h-10 rounded-full border border-outline-variant flex items-center justify-center">
              <AlertCircle size={18} className="text-on-surface-variant" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-primary uppercase tracking-wider">Assignments</h4>
              <p className="text-[10px] text-on-surface-variant max-w-xs mt-1 leading-relaxed">
                AI-driven assignment tracking and grade prediction coming in next update.
              </p>
            </div>
          </div>

          <div className="matte-card rounded-2xl p-6 border-dashed flex flex-col items-center justify-center text-center gap-3">
            <div className="w-10 h-10 rounded-full border border-outline-variant flex items-center justify-center">
              <AlertCircle size={18} className="text-on-surface-variant" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-primary uppercase tracking-wider">Detailed Attendance</h4>
              <p className="text-[10px] text-on-surface-variant max-w-xs mt-1 leading-relaxed">
                Per-lecture attendance visualization and bunk-planner features coming soon.
              </p>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
};

export default AcademicsPage;
