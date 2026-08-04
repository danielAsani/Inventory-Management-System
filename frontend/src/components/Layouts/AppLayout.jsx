import { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import Header from "./Header";
import Sidebar from "./Sidebar";
import styles from "./css/AppLayout.module.css";

export default function AppLayout() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className={styles.layout} style={{ "--sidebar-width-current": isSidebarCollapsed ? "4.75rem" : "16rem" }}>
      <Sidebar isCollapsed={isSidebarCollapsed} user={user} />
      <div className={styles.main}>
        <Header user={user} onToggleSidebar={() => setIsSidebarCollapsed((current) => !current)} onLogout={handleLogout} />
        <main className={styles.content}><Outlet /></main>
      </div>
    </div>
  );
}
