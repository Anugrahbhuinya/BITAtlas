import React, { useState, Suspense } from "react";
import { 
  Users, Building, HeartPulse, 
  BookOpen, Laptop, Phone, 
  ArrowRight, Contact 
} from "lucide-react";
import { AnimatePresence } from "framer-motion";
import { PlaceholderModal } from "./PlaceholderModal";

// Lazy-load FacultyDirectoryModal to optimize bundle size
const FacultyDirectoryModal = React.lazy(() => 
  import("./FacultyDirectoryModal").then(module => ({ default: module.FacultyDirectoryModal }))
);

interface ContactItem {
  name: string;
  icon: React.ReactNode;
  actionType: "faculty" | "placeholder";
}

export const ImportantContactsCard: React.FC = () => {
  const [isFacultyOpen, setIsFacultyOpen] = useState(false);
  const [isPlaceholderOpen, setIsPlaceholderOpen] = useState(false);
  const [placeholderTitle, setPlaceholderTitle] = useState("");

  const contacts: ContactItem[] = [
    { name: "Faculty Directory", icon: <Users size={14} />, actionType: "faculty" },
    { name: "Department Offices", icon: <Building size={14} />, actionType: "placeholder" },
    { name: "Health Centre", icon: <HeartPulse size={14} />, actionType: "placeholder" },
    { name: "Central Library", icon: <BookOpen size={14} />, actionType: "placeholder" },
    { name: "IT Help Desk", icon: <Laptop size={14} />, actionType: "placeholder" },
    { name: "Emergency Contacts", icon: <Phone size={14} />, actionType: "placeholder" },
  ];

  const handleContactClick = (item: ContactItem) => {
    if (item.actionType === "faculty") {
      setIsFacultyOpen(true);
    } else {
      setPlaceholderTitle(item.name);
      setIsPlaceholderOpen(true);
    }
  };

  return (
    <div className="md:col-span-3 border border-outline-variant/40 bg-surface-container-low rounded-2xl p-6 flex flex-col justify-between hover:border-outline transition-colors duration-200">
      <div>
        <div className="flex items-center gap-3 mb-2 border-b border-outline-variant/30 pb-3 select-none">
          <Contact className="w-5 h-5 text-primary" />
          <div>
            <h3 className="text-sm font-extrabold text-primary uppercase tracking-wider leading-none">Important Contacts</h3>
            <p className="text-[10px] text-on-surface-variant mt-1.5 font-medium leading-tight">Quick access to faculty and campus services.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-2.5 mt-4">
          {contacts.map((c) => (
            <button
              key={c.name}
              onClick={() => handleContactClick(c)}
              className="w-full flex items-center gap-3 px-3 py-2 bg-surface-container hover:bg-primary/10 text-primary rounded-xl transition-all duration-150 group cursor-pointer border border-transparent hover:border-outline-variant text-left"
            >
              <div className="text-primary shrink-0 transition-transform group-hover:scale-110">
                {c.icon}
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="text-[10px] font-extrabold uppercase tracking-wider text-primary truncate">
                  {c.name}
                </h4>
              </div>
              <ArrowRight size={12} className="text-on-surface-variant/60 transition-transform group-hover:translate-x-0.5 group-hover:text-primary shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* Modal Containers */}
      <AnimatePresence>
        {isFacultyOpen && (
          <Suspense fallback={null}>
            <FacultyDirectoryModal 
              isOpen={isFacultyOpen} 
              onClose={() => setIsFacultyOpen(false)} 
            />
          </Suspense>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isPlaceholderOpen && (
          <PlaceholderModal 
            isOpen={isPlaceholderOpen} 
            onClose={() => setIsPlaceholderOpen(false)} 
            title={placeholderTitle} 
          />
        )}
      </AnimatePresence>
    </div>
  );
};
