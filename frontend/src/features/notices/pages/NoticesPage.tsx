import { Bell, Calendar, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

function NoticesPage() {
  const dummyNotices = [
    {
      title: "End Semester Examinations Schedule",
      date: "June 10, 2026",
      category: "Academic",
      desc: "Detailed schedule for the upcoming End Semester examinations has been released. Exams start on June 22, 2026. Please check the official board for seating plans.",
    },
    {
      title: "Registration for Summer Semester 2026",
      date: "June 08, 2026",
      category: "Registration",
      desc: "Registration portal for the Summer Semester will open on June 15. Students carrying backlogs are advised to register before the deadline of June 20.",
    },
    {
      title: "NATS Club: Annual Hackathon Registration Open",
      date: "June 05, 2026",
      category: "Clubs & Events",
      desc: "The annual campus-wide hackathon 'BIT-Hacks 2026' is now open for registrations. Teams of 2-4 can register online. Exciting prizes up for grabs!",
    },
    {
      title: "Hostel Mess Timings Updated",
      date: "June 02, 2026",
      category: "Hostel",
      desc: "Mess dinner timings for all hostels have been revised to 7:30 PM - 9:30 PM starting this Monday. Cooperate with the mess committee for smooth operations.",
    },
  ];

  return (
    <div className="p-8 text-white max-w-4xl mx-auto">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <Link to="/" className="flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-3 transition">
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-3">
            <Bell className="text-blue-500 animate-pulse" size={28} />
            Campus Notices
          </h1>
        </div>
      </header>

      <div className="space-y-6">
        {dummyNotices.map((notice, index) => (
          <div
            key={index}
            className="bg-slate-800/40 border border-slate-800 hover:border-slate-700 transition duration-300 rounded-2xl p-6 shadow-lg"
          >
            <div className="flex items-center justify-between gap-4 mb-3">
              <span className="bg-slate-700/60 text-slate-300 px-3 py-1 rounded-full text-xs font-semibold">
                {notice.category}
              </span>
              <span className="text-slate-400 text-xs flex items-center gap-1.5">
                <Calendar size={14} />
                {notice.date}
              </span>
            </div>
            <h2 className="text-xl font-bold text-white mb-2 hover:text-blue-400 transition cursor-pointer">
              {notice.title}
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed">
              {notice.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default NoticesPage;
