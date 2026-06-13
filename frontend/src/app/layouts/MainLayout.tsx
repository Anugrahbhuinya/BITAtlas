import { Outlet } from "react-router-dom";
import Sidebar from "../../shared/components/Sidebar";

interface Props {
  children?: React.ReactNode;
}

function MainLayout({ children }: Props) {
  return (
    <div className="h-screen flex bg-slate-900">
      <Sidebar />

      <main className="flex-1">{children || <Outlet />}</main>
    </div>
  );
}

export default MainLayout;
