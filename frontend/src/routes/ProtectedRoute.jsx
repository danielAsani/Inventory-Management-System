import { Navigate, useLocation } from "react-router-dom";
import LoadingState from "../components/common/LoadingState";
import { useAuth } from "../hooks/useAuth";
import { canAccessRoute } from "../utils/permissions";

function ProtectedRoute({ children, roles }) {
  const { user, isAuthenticated, isBootstrapping } = useAuth();
  const location = useLocation();

  if (isBootstrapping) {
    return <LoadingState label="Verification de la session..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!canAccessRoute(user, roles)) {
    return <Navigate to="/403" replace />;
  }

  return children;
}

export default ProtectedRoute;
