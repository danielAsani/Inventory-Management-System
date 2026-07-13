export const ROLES = {
  ADMIN: "ADMIN",
  GESTION: "GESTION",
  MAGASIN: "MAGASIN",
};

export const ROLE_LABELS = {
  [ROLES.ADMIN]: "Administrateur",
  [ROLES.GESTION]: "Gestion",
  [ROLES.MAGASIN]: "Magasin",
};

export function roleLabel(role) {
  return ROLE_LABELS[role] || role || "Session";
}

export function canWrite(user, writeRoles = []) {
  if (!user?.role) return false;
  return writeRoles.includes(user.role);
}

export function canAccessRoute(user, allowedRoles) {
  if (!allowedRoles?.length) return true;
  return allowedRoles.includes(user?.role);
}
