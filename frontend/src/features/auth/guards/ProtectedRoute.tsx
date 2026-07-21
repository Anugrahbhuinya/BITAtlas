import { Navigate, Outlet } from "react-router-dom";
import useAuth from "../hooks/useAuth";

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-slate-950 text-white">
        <div className="relative flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <div className="absolute h-8 w-8 rounded-full bg-slate-900 flex items-center justify-center">
            <span className="text-[7px] text-blue-400 font-bold uppercase tracking-wider">BITAtlas</span>
          </div>
        </div>
        <p className="mt-4 text-sm text-slate-400 font-medium animate-pulse">Loading secure portal...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};

export default ProtectedRoute;
