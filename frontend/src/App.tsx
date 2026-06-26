import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import MainLayout from "./app/layouts/MainLayout";

import ChatPage from "./features/chat/pages/ChatPage";
import DashboardPage from "./features/dashboard/pages/DashboardPage";
import NoticesPage from "./features/notices/pages/NoticesPage";
import AcademicsPage from "./features/academics/pages/AcademicsPage";
import MapPage from "./features/map/pages/MapPage";

// Admin Portal Imports
import { AdminLoginPage } from "./features/admin/pages/AdminLoginPage";
import { AdminLayout } from "./features/admin/components/AdminLayout";
import { AdminDashboardPage } from "./features/admin/pages/AdminDashboardPage";
import { AdminAnalyticsPage } from "./features/admin/pages/AdminAnalyticsPage";
import { AdminDocumentsPage } from "./features/admin/pages/AdminDocumentsPage";
import { AdminKnowledgePage } from "./features/admin/pages/AdminKnowledgePage";
import { AdminActivityPage } from "./features/admin/pages/AdminActivityPage";
import { AdminSettingsPage } from "./features/admin/pages/AdminSettingsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* User Portal Protected under MainLayout */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/notices" element={<NoticesPage />} />
          <Route path="/academics" element={<AcademicsPage />} />
          <Route path="/map" element={<MapPage />} />
        </Route>

        {/* Admin Portal Login */}
        <Route path="/admin/login" element={<AdminLoginPage />} />

        {/* Admin Portal Protected under AdminLayout */}
        <Route element={<AdminLayout />}>
          <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
          <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
          <Route path="/admin/documents" element={<AdminDocumentsPage />} />
          <Route path="/admin/knowledge-base" element={<AdminKnowledgePage />} />
          <Route path="/admin/activity" element={<AdminActivityPage />} />
          <Route path="/admin/settings" element={<AdminSettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
