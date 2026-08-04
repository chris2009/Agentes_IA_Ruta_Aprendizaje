import { Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar.jsx";
import Footer from "./components/Footer.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ActivitiesPage from "./pages/ActivitiesPage.jsx";
import NewActivityPage from "./pages/NewActivityPage.jsx";
import CalendarPage from "./pages/CalendarPage.jsx";
import PlansPage from "./pages/PlansPage.jsx";
import MaterialsPage from "./pages/MaterialsPage.jsx";
import ChatPage from "./pages/ChatPage.jsx";

export default function App() {
  return (
    <>
      <div className="app-shell">
        <NavBar />
        <main className="app-content">
          <div className="app-content-inner">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/actividades" element={<ActivitiesPage />} />
              <Route path="/actividades/nueva" element={<NewActivityPage />} />
              <Route path="/calendario" element={<CalendarPage />} />
              <Route path="/planes" element={<PlansPage />} />
              <Route path="/materiales" element={<MaterialsPage />} />
              <Route path="/chat" element={<ChatPage />} />
            </Routes>
          </div>
        </main>
      </div>
      <Footer />
    </>
  );
}
