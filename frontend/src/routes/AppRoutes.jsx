import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "../components/Layouts/AppLayout";
import Login from "../pages/auth/Login";
import Dashboard from "../pages/dashboard/Dashboard";
import AccessDenied from "../pages/errors/AccessDenied";
import NotFound from "../pages/errors/NotFound";
import Profile from "../pages/profile/Profile";
import ResourcePage from "../pages/resources/ResourcePage";
import { getResourceConfig } from "../constants/resourceConfigs";
import ProtectedRoute from "./ProtectedRoute";

function ResourceRoute({ resourceKey }) {
  const config = getResourceConfig(resourceKey);
  return (
    <ProtectedRoute roles={config.visibleRoles}>
      <ResourcePage resourceKey={resourceKey} />
    </ProtectedRoute>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/403" element={<AccessDenied />} />

      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/organisation/departements" element={<ResourceRoute resourceKey="departements" />} />
        <Route path="/organisation/directions" element={<ResourceRoute resourceKey="directions" />} />
        <Route path="/catalogue/familles" element={<ResourceRoute resourceKey="familles" />} />
        <Route path="/catalogue/categories" element={<ResourceRoute resourceKey="categories" />} />
        <Route path="/catalogue/unites" element={<Navigate to="/catalogue/categories" replace />} />
        <Route path="/catalogue/fournisseurs" element={<ResourceRoute resourceKey="fournisseurs" />} />
        <Route path="/stock/materiels" element={<ResourceRoute resourceKey="materiels" />} />
        <Route path="/stock/consommables" element={<ResourceRoute resourceKey="consommables" />} />
        <Route path="/operations/mouvements" element={<ResourceRoute resourceKey="mouvements" />} />
        <Route path="/operations/affectations" element={<ResourceRoute resourceKey="affectations" />} />
        <Route path="/operations/consommations" element={<ResourceRoute resourceKey="consommations" />} />
        <Route path="/inventaires" element={<ResourceRoute resourceKey="inventaires" />} />
        <Route path="/inventaires/details" element={<Navigate to="/inventaires" replace />} />
        <Route path="/maintenance/entretiens" element={<ResourceRoute resourceKey="entretiens" />} />
        <Route path="/maintenance/reparations" element={<ResourceRoute resourceKey="reparations" />} />
        <Route path="/demandes" element={<ResourceRoute resourceKey="demandes" />} />
        <Route path="/documents" element={<ResourceRoute resourceKey="documents" />} />
        <Route path="/admin/users" element={<ResourceRoute resourceKey="users" />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
