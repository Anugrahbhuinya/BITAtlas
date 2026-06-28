import { useState } from "react";
import { Search, ChevronLeft, ChevronRight, ArrowRight, Calendar, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

export const NoticesPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const noticesData = [
    {
      title: "Semester End Examination Schedule: Autumn 2023",
      date: "Oct 24, 2023",
      category: "Academic",
      desc: "The detailed schedule for the upcoming semester-end examinations for all UG and PG programs has been released. Students are advised to verify their subjects and timings.",
    },
    {
      title: "Recruitment Drive: Google Engineering Residency 2024",
      date: "Oct 22, 2023",
      category: "Placements",
      desc: "Applications are now open for the Google Engineering Residency. Final year CS/IT students with a CGPA above 8.0 are eligible to apply through the placement portal.",
      timeLeft: "2 days left"
    },
    {
      title: "Pantheon '23: Annual Cultural Fest Registrations",
      date: "Oct 20, 2023",
      category: "Events",
      desc: "Join the extravaganza! Registrations for all club events, guest lectures, and the flagship concert are now live on the BIT events app. Early bird slots available.",
    },
    {
      title: "Network Maintenance: Campus Wi-Fi Downtime",
      date: "Oct 19, 2023",
      category: "Academic",
      desc: "The IT Services department will be conducting routine maintenance on the core backbone router this Sunday between 02:00 AM and 06:00 AM. Internet services will be affected.",
    },
    {
      title: "Mess Rebate Requests for Diwali Vacations",
      date: "Oct 18, 2023",
      category: "Hostels",
      desc: "Hostellers wishing to claim mess rebate for the upcoming Diwali holidays must submit their leave applications at the respective hostel offices before Nov 5th.",
    },
  ];

  const categories = ["All", "Academic", "Events", "Placements", "Hostels"];

  const filteredNotices = noticesData.filter((notice) => {
    const matchesSearch = 
      notice.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      notice.desc.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = 
      activeCategory === "All" || 
      notice.category.toLowerCase() === activeCategory.toLowerCase();

    return matchesSearch && matchesCategory;
  });

  const getTagStyles = (cat: string) => {
    switch (cat.toLowerCase()) {
      case "academic":
        return "bg-primary-container text-on-primary-container";
      case "placements":
        return "bg-zinc-800 text-[#e7e1dd]";
      case "events":
        return "bg-surface-container-highest text-[#FAFAFA]";
      case "hostels":
        return "bg-surface-container-high text-[#A1A1AA]";
      default:
        return "bg-surface-container text-[#A1A1AA]";
    }
  };

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-8 space-y-8 text-on-surface font-sans select-text">
      {/* Search & Filters Section */}
      <section className="space-y-6">
        <div className="relative group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant group-focus-within:text-primary transition-colors w-5 h-5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search notices by keyword, department, or event..."
            className="w-full h-14 pl-12 pr-4 bg-surface-container border border-outline-variant rounded-xl focus:outline-none focus:border-primary text-sm transition-all placeholder:text-on-surface-variant/40"
          />
        </div>

        {/* Categories Chips */}
        <div className="flex flex-wrap gap-3 select-none">
          {categories.map((cat) => {
            const isActive = activeCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`
                  px-5 py-2
                  rounded-full
                  text-xs
                  font-bold
                  uppercase
                  tracking-wider
                  transition-colors
                  cursor-pointer
                  ${isActive
                    ? "bg-primary text-background"
                    : "border border-outline-variant text-on-surface-variant hover:border-primary hover:text-primary"
                  }
                `}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </section>

      {/* Notices Card Grid */}
      <section className="grid grid-cols-1 gap-4 pb-12">
        {filteredNotices.length > 0 ? (
          filteredNotices.map((notice, idx) => (
            <div
              key={idx}
              className="matte-card p-6 rounded-2xl flex flex-col md:flex-row md:items-start gap-6 cursor-pointer group"
            >
              <div className="flex-1 space-y-3">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 text-[9px] font-extrabold tracking-wider uppercase rounded-sm ${getTagStyles(notice.category)}`}>
                    {notice.category}
                  </span>
                  <span className="text-[10px] text-on-surface-variant font-mono-code font-medium">
                    {notice.date}
                  </span>
                </div>
                <h3 className="text-base md:text-lg font-bold text-primary leading-snug group-hover:text-primary transition-colors">
                  {notice.title}
                </h3>
                <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2 max-w-[720px]">
                  {notice.desc}
                </p>
              </div>

              <div className="hidden md:flex flex-col items-end justify-between self-stretch shrink-0">
                <ArrowRight className="text-on-surface-variant group-hover:text-primary group-hover:translate-x-1 transition-all w-5 h-5" />
                {notice.timeLeft && (
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-amber-500">
                    <span>{notice.timeLeft}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 border border-dashed border-outline-variant rounded-2xl bg-surface-container/20">
            <p className="text-sm text-on-surface-variant font-medium">No announcements found matching the criteria.</p>
          </div>
        )}
      </section>

      {/* Pagination Footer */}
      <footer className="h-14 px-6 border-t border-outline-variant/30 flex items-center justify-between bg-surface-container-lowest rounded-xl">
        <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
          Showing {filteredNotices.length} of {noticesData.length} notices
        </span>
        <div className="flex gap-2">
          <button 
            disabled 
            className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant/40 text-on-surface-variant disabled:opacity-30 cursor-not-allowed"
          >
            <ChevronLeft size={16} />
          </button>
          <button 
            disabled={filteredNotices.length === 0}
            className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant text-on-surface-variant hover:border-primary hover:text-primary transition-colors cursor-pointer"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </footer>
    </div>
  );
};

export default NoticesPage;
