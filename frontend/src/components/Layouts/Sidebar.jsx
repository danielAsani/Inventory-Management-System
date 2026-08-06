import { Archive, Boxes, Building2, ClipboardList, FileText, LayoutDashboard, PackageSearch, Repeat2, Tags, UserCheck, Users, Wrench } from "lucide-react";
import { NavLink } from "react-router-dom";
import logo from "../../../public/logo.png";
import { ROLES } from "../../utils/permissions";
import styles from "./css/Sidebar.module.css";

const adminOnly = [ROLES.ADMIN];
const businessRoles = [ROLES.ADMIN, ROLES.GESTION, ROLES.MAGASIN];
const gestionRoles = [ROLES.ADMIN, ROLES.GESTION];
const magasinRoles = [ROLES.ADMIN, ROLES.MAGASIN];

const mainNavigation = [
  { label: "Tableau de bord", icon: LayoutDashboard, to: "/dashboard", roles: businessRoles },
  { label: "Materiels", icon: PackageSearch, to: "/stock/materiels", roles: businessRoles },
  { label: "Consommables", icon: Boxes, to: "/stock/consommables", roles: businessRoles },
  { label: "Mouvements", icon: ClipboardList, to: "/operations/mouvements", roles: gestionRoles },
  { label: "Affectations", icon: UserCheck, to: "/operations/affectations", roles: magasinRoles },
  { label: "Consommations", icon: Repeat2, to: "/operations/consommations", roles: gestionRoles },
];

const organizationNavigation = [
  { label: "Departements", icon: Building2, to: "/organisation/departements", roles: adminOnly },
  { label: "Directions", icon: Building2, to: "/organisation/directions", roles: adminOnly },
];

const catalogueNavigation = [
  { label: "Familles", icon: Archive, to: "/catalogue/familles", roles: businessRoles },
  { label: "Categories", icon: Tags, to: "/catalogue/categories", roles: businessRoles },
  { label: "Fournisseurs", icon: Users, to: "/catalogue/fournisseurs", roles: adminOnly },
];

const processNavigation = [
  { label: "Inventaires", icon: ClipboardList, to: "/inventaires", roles: gestionRoles },
  { label: "Entretiens", icon: Wrench, to: "/maintenance/entretiens", roles: businessRoles },
  { label: "Reparations", icon: Wrench, to: "/maintenance/reparations", roles: gestionRoles },
  { label: "Demandes", icon: FileText, to: "/demandes", roles: businessRoles },
  { label: "Documents", icon: FileText, to: "/documents", roles: magasinRoles },
];

const adminNavigation = [
  { label: "Utilisateurs", icon: Users, to: "/admin/users", roles: adminOnly },
];

function NavigationList({ items, isCollapsed }) {
  return (
    <ul className={styles.navigationList}>
      {items.map(({ label, icon: Icon, to }) => (
        <li key={label}>
          <NavLink to={to} className={({ isActive }) => `${styles.navigationItem} ${isActive ? styles.active : ""}`} title={isCollapsed ? label : undefined}>
            <Icon size={19} strokeWidth={1.8} /><span>{label}</span>
          </NavLink>
        </li>
      ))}
    </ul>
  );
}

function visibleItems(items, user) {
  return items.filter((item) => !item.roles || item.roles.includes(user?.role));
}

export default function Sidebar({ isCollapsed, user }) {
  const mainItems = visibleItems(mainNavigation, user);
  const organizationItems = visibleItems(organizationNavigation, user);
  const catalogueItems = visibleItems(catalogueNavigation, user);
  const processItems = visibleItems(processNavigation, user);
  const adminItems = visibleItems(adminNavigation, user);

  return (
    <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ""}`}>
      <div className={styles.brand}>
        <img className={styles.logo} src={logo} alt="Gestion Inventaire" />
        <div className={styles.brandText}><strong>Gestion</strong><span>Inventaire</span></div>
      </div>
      <nav className={styles.navigation} aria-label="Navigation principale">
        {mainItems.length > 0 && (
          <>
            <p className={styles.sectionTitle}>Exploitation</p>
            <NavigationList items={mainItems} isCollapsed={isCollapsed} />
          </>
        )}
        {organizationItems.length > 0 && (
          <>
            <p className={styles.sectionTitle}>Organisation</p>
            <NavigationList items={organizationItems} isCollapsed={isCollapsed} />
          </>
        )}
        {catalogueItems.length > 0 && (
          <>
            <p className={styles.sectionTitle}>Catalogue</p>
            <NavigationList items={catalogueItems} isCollapsed={isCollapsed} />
          </>
        )}
        {processItems.length > 0 && (
          <>
            <p className={styles.sectionTitle}>Suivi</p>
            <NavigationList items={processItems} isCollapsed={isCollapsed} />
          </>
        )}
        {adminItems.length > 0 && (
          <>
            <p className={styles.sectionTitle}>Administration</p>
            <NavigationList items={adminItems} isCollapsed={isCollapsed} />
          </>
        )}
      </nav>
      <div className={styles.footerCard}><div className={styles.footerIcon}><Boxes size={18} /></div><div><strong>Gestion Inventaire</strong><span>Version 1.0</span></div></div>
    </aside>
  );
}
