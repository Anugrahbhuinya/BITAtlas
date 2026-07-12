import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import BackendStatusGuard from "./shared/components/BackendStatusGuard";

import MainLayout from "./app/layouts/MainLayout";

import ChatPage from "./features/chat/pages/ChatPage";
import DashboardPage from "./features/dashboard/pages/DashboardPage";
import NoticesPage from "./features/notices/pages/NoticesPage";
import { 
  AcademicWorkspace, 
  AcademicDashboardPage, 
  TimetablePage, 
  ImportTimetablePage,
  PreviewTimetablePage,
  AttendancePage,
  AttendanceHistoryPage,
  SubjectAttendancePage,
  PlannerPage,
  TimelinePage,
  TaskDetailsPage
} from "./features/academics";
import MapPage from "./features/map/pages/MapPage";
import NavigationPage from "./features/navigation/pages/NavigationPage";

// Student Auth Imports
import { AuthProvider } from "./features/auth/context/AuthContext";
import { ProtectedRoute } from "./features/auth/guards/ProtectedRoute";
import { LoginPage } from "./features/auth/pages/LoginPage";
import { RegisterPage } from "./features/auth/pages/RegisterPage";

// Student Profile Imports
import { ProfilePage } from "./features/student/pages/ProfilePage";
import { ChangePasswordPage } from "./features/student/pages/ChangePasswordPage";

// Student Preferences Imports
import { PreferencesProvider } from "./features/preferences/context/PreferencesContext";

// Admin Portal Imports
import { AdminLoginPage } from "./features/admin/pages/AdminLoginPage";
import { AdminLayout } from "./features/admin/components/AdminLayout";
import { AdminDashboardPage } from "./features/admin/pages/AdminDashboardPage";
import { AdminAnalyticsPage } from "./features/admin/pages/AdminAnalyticsPage";
import { AdminDocumentsPage } from "./features/admin/pages/AdminDocumentsPage";
import { AdminWebsitesPage } from "./features/admin/pages/AdminWebsitesPage";
import { AdminKnowledgePage } from "./features/admin/pages/AdminKnowledgePage";
import { AdminActivityPage } from "./features/admin/pages/AdminActivityPage";
import { AdminSettingsPage } from "./features/admin/pages/AdminSettingsPage";
import { AdminCrawlHistoryPage } from "./features/admin/pages/AdminCrawlHistoryPage";
import { AdminStudentsPage } from "./features/admin/pages/AdminStudentsPage";
import { AdminKnowledgeEditorPage } from "./features/admin/pages/AdminKnowledgeEditorPage";
import { AdminKnowledgeSearchPage } from "./features/admin/pages/AdminKnowledgeSearchPage";
import { AdminKnowledgeStatsPage } from "./features/admin/pages/AdminKnowledgeStatsPage";
import { AdminVersionHistoryPage } from "./features/admin/pages/AdminVersionHistoryPage";
import { AdminDraftsPage } from "./features/admin/pages/AdminDraftsPage";
import { AdminNavigationPage } from "./features/navigation/pages/AdminNavigationPage";

function App() {
  return (
    <BackendStatusGuard>
      <AuthProvider>
      <PreferencesProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Student Auth Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* User Portal Protected under MainLayout and ProtectedRoute */}
            <Route element={<ProtectedRoute />}>
              <Route element={<MainLayout />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/notices" element={<NoticesPage />} />
                <Route path="/academics" element={<AcademicWorkspace />}>
                  <Route index element={<AcademicDashboardPage />} />
                  <Route path="timetable" element={<TimetablePage />} />
                  <Route path="timetable/import" element={<ImportTimetablePage />} />
                  <Route path="timetable/preview" element={<PreviewTimetablePage />} />
                  <Route path="attendance" element={<AttendancePage />} />
                  <Route path="attendance/history" element={<AttendanceHistoryPage />} />
                  <Route path="attendance/subject/:subjectId" element={<SubjectAttendancePage />} />
                  <Route path="planner" element={<PlannerPage />} />
                  <Route path="timeline" element={<TimelinePage />} />
                  <Route path="planner/task/:taskId" element={<TaskDetailsPage />} />
                </Route>
                <Route path="/map" element={<MapPage />} />
                <Route path="/navigation" element={<NavigationPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/profile/change-password" element={<ChangePasswordPage />} />
              </Route>
            </Route>

          {/* Admin Portal Login */}
          <Route path="/admin/login" element={<AdminLoginPage />} />

          {/* Admin Portal Protected under AdminLayout */}
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
            <Route path="/admin/students" element={<AdminStudentsPage />} />
            <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
            <Route path="/admin/documents" element={<AdminDocumentsPage />} />
            <Route path="/admin/websites" element={<AdminWebsitesPage />} />
            <Route path="/admin/crawl-history" element={<AdminCrawlHistoryPage />} />
            <Route path="/admin/knowledge-base" element={<AdminKnowledgePage />} />
            <Route path="/admin/activity" element={<AdminActivityPage />} />
            <Route path="/admin/settings" element={<AdminSettingsPage />} />
            <Route path="/admin/navigation" element={<AdminNavigationPage />} />
            <Route path="/admin/knowledge/editor" element={<AdminKnowledgeEditorPage />} />
            <Route path="/admin/knowledge/editor/:id" element={<AdminKnowledgeEditorPage />} />
            <Route path="/admin/knowledge/search" element={<AdminKnowledgeSearchPage />} />
            <Route path="/admin/knowledge/stats" element={<AdminKnowledgeStatsPage />} />
            <Route path="/admin/knowledge/drafts" element={<AdminDraftsPage />} />
            <Route path="/admin/knowledge/versions/:id" element={<AdminVersionHistoryPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
      </PreferencesProvider>
    </AuthProvider>
    </BackendStatusGuard>
  );
}

export default App;

