import {
  MessageSquare,
  Bell,
  GraduationCap,
  MapPin,
} from "lucide-react";
import { Link } from "react-router-dom";

function DashboardPage() {
  return (
    <div className="p-8 text-white max-w-6xl mx-auto">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          Welcome to BIT Mesra AI Portal
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          Your intelligent assistant for campus information, notices, and
          academic tools.
        </p>
      </header>

      {/* Main Search/Chat Banner */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-2xl p-6 mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
        <div className="max-w-xl">
          <h2 className="text-xl font-bold text-white mb-2">
            Need quick answers?
          </h2>
          <p className="text-slate-300">
            Ask our AI Assistant about hostels, departments, maps, academic
            calendars, and student FAQs.
          </p>
        </div>
        <Link
          to="/chat"
          className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-3 rounded-xl transition-all shadow-lg shadow-blue-500/20 active:scale-95 whitespace-nowrap"
        >
          <MessageSquare size={18} />
          Start Chatting
        </Link>
      </div>

      {/* Grid of features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Quick Links Card */}
        <div className="bg-slate-800/40 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition duration-300">
          <div className="bg-blue-500/10 text-blue-400 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
            <Bell size={24} />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">
            Notices & Updates
          </h3>
          <p className="text-slate-400 mb-4 text-sm leading-relaxed">
            Stay up to date with official announcements, exam notifications, and
            student club activities.
          </p>
          <Link
            to="/notices"
            className="text-blue-400 hover:text-blue-300 text-sm font-semibold inline-flex items-center gap-1 group"
          >
            View Notices
            <span className="transform group-hover:translate-x-1 transition-transform">
              →
            </span>
          </Link>
        </div>

        {/* Academics Card */}
        <div className="bg-slate-800/40 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition duration-300">
          <div className="bg-emerald-500/10 text-emerald-400 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
            <GraduationCap size={24} />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Academics</h3>
          <p className="text-slate-400 mb-4 text-sm leading-relaxed">
            Access department information, course details, academic calendar,
            and faculty lists.
          </p>
          <Link
            to="/academics"
            className="text-emerald-400 hover:text-emerald-300 text-sm font-semibold inline-flex items-center gap-1 group"
          >
            Academic Portal
            <span className="transform group-hover:translate-x-1 transition-transform">
              →
            </span>
          </Link>
        </div>

        {/* Map Card */}
        <div className="bg-slate-800/40 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition duration-300">
          <div className="bg-violet-500/10 text-violet-400 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
            <MapPin size={24} />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Campus Map</h3>
          <p className="text-slate-400 mb-4 text-sm leading-relaxed">
            Explore the campus layout, find hostels, academic buildings,
            departments, and sports facilities.
          </p>
          <Link
            to="/chat"
            className="text-violet-400 hover:text-violet-300 text-sm font-semibold inline-flex items-center gap-1 group"
          >
            Find Locations
            <span className="transform group-hover:translate-x-1 transition-transform">
              →
            </span>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
