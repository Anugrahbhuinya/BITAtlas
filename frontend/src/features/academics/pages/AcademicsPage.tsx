import { GraduationCap, BookOpen, Award, Layers, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

function AcademicsPage() {
  const departments = [
    {
      name: "Computer Science & Engineering",
      code: "CSE",
      programs: ["B.Tech", "M.Tech", "MCA", "Ph.D"],
    },
    {
      name: "Electronics & Communication Engineering",
      code: "ECE",
      programs: ["B.Tech", "M.Tech", "Ph.D"],
    },
    {
      name: "Mechanical Engineering",
      code: "MECH",
      programs: ["B.Tech", "M.Tech", "Ph.D"],
    },
    {
      name: "Electrical & Electronics Engineering",
      code: "EEE",
      programs: ["B.Tech", "M.Tech", "Ph.D"],
    },
  ];

  return (
    <div className="p-8 text-white max-w-5xl mx-auto">
      <header className="mb-8">
        <Link to="/" className="flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-3 transition">
          <ArrowLeft size={16} />
          Back to Dashboard
        </Link>
        <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-3">
          <GraduationCap className="text-emerald-500" size={32} />
          Academics at BIT Mesra
        </h1>
        <p className="text-slate-400 mt-2">
          Explore departments, course offerings, and structural program details.
        </p>
      </header>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <div className="bg-slate-800/35 border border-slate-800 p-5 rounded-2xl flex items-center gap-4">
          <div className="bg-emerald-500/10 text-emerald-400 p-3 rounded-xl">
            <BookOpen size={20} />
          </div>
          <div>
            <div className="text-2xl font-bold">15+</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider">Departments</div>
          </div>
        </div>
        <div className="bg-slate-800/35 border border-slate-800 p-5 rounded-2xl flex items-center gap-4">
          <div className="bg-blue-500/10 text-blue-400 p-3 rounded-xl">
            <Award size={20} />
          </div>
          <div>
            <div className="text-2xl font-bold">Ranked 50-70</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider">NIRF Ranking</div>
          </div>
        </div>
        <div className="bg-slate-800/35 border border-slate-800 p-5 rounded-2xl flex items-center gap-4">
          <div className="bg-violet-500/10 text-violet-400 p-3 rounded-xl">
            <Layers size={20} />
          </div>
          <div>
            <div className="text-2xl font-bold">10,000+</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider">Active Students</div>
          </div>
        </div>
      </div>

      {/* Departments Grid */}
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <BookOpen size={22} className="text-slate-400" />
        Prominent Departments
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {departments.map((dept, index) => (
          <div
            key={index}
            className="bg-slate-800/40 border border-slate-800 hover:border-slate-700 transition duration-300 rounded-2xl p-6"
          >
            <div className="flex items-start justify-between gap-4 mb-3">
              <h3 className="text-lg font-bold text-white leading-snug">{dept.name}</h3>
              <span className="bg-emerald-500/15 text-emerald-400 px-2 py-0.5 rounded text-xs font-mono font-bold">
                {dept.code}
              </span>
            </div>
            <div className="flex flex-wrap gap-2 mt-4">
              {dept.programs.map((prog, pIndex) => (
                <span
                  key={pIndex}
                  className="bg-slate-700/50 text-slate-300 px-2.5 py-1 rounded-md text-xs"
                >
                  {prog}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AcademicsPage;
