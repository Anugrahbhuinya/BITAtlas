import {
  LayoutDashboard,
  MessageSquare,
  Bell,
  GraduationCap,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const navItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "/",
  },
  {
    label: "Chat",
    icon: MessageSquare,
    path: "/chat",
  },
  {
    label: "Notices",
    icon: Bell,
    path: "/notices",
  },
  {
    label: "Academics",
    icon: GraduationCap,
    path: "/academics",
  },
];

const Sidebar = () => {
  return (
    <aside className="w-64 bg-zinc-900 border-r border-zinc-800 flex flex-col">
      <div className="p-5 border-b border-zinc-800">
        <h1 className="text-xl font-bold">BIT Mesra AI</h1>

        <p className="text-xs text-zinc-400 mt-1">Campus Assistant</p>
      </div>

      <nav className="flex-1 p-3">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? "bg-blue-600 text-white"
                        : "text-zinc-400 hover:bg-zinc-800 hover:text-white"
                    }`
                  }
                >
                  <Icon size={20} />

                  <span>{item.label}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-zinc-800">
        <p className="text-xs text-zinc-500">BIT Mesra AI v1.0</p>
      </div>
    </aside>
  );
};

export default Sidebar;
