import { BrowserRouter, Routes, Route } from "react-router-dom";

import MainLayout from "./app/layouts/MainLayout";

import ChatPage from "./features/chat/pages/ChatPage";
import DashboardPage from "./features/dashboard/pages/DashboardPage";
import NoticesPage from "./features/notices/pages/NoticesPage";
import AcademicsPage from "./features/academics/pages/AcademicsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/notices" element={<NoticesPage />} />
          <Route path="/academics" element={<AcademicsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
