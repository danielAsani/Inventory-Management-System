import { useEffect, useRef, useState } from "react";
import { Bell, ChevronDown, LogOut, Menu, PanelLeftClose, Search, Settings, UserRound, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import apiClient from "../../api/apiClient";
import { getApiErrorMessage } from "../../utils/apiErrors";
import { initials } from "../../utils/format";
import { normalizePage } from "../../utils/pagination";
import { ROLES, roleLabel } from "../../utils/permissions";
import styles from "./css/Header.module.css";

const REQUEST_STATUS_LABELS = {
  EN_ATTENTE_DEPARTEMENT: "En attente departement",
  EN_TRAITEMENT_MAGASIN: "Au magasin",
  TRAITEE: "Traitee",
  REJETEE: "Rejetee",
  ANNULEE: "Annulee",
};

const REQUEST_TYPE_LABELS = {
  ACHAT: "Achat",
  REAPPROVISIONNEMENT: "Reapprovisionnement",
  REPARATION: "Reparation",
  AUTRE: "Autre",
};

function requestNeedsAttention(request, user) {
  if (user?.role === ROLES.ADMIN) {
    return ["EN_ATTENTE_DEPARTEMENT", "EN_TRAITEMENT_MAGASIN"].includes(request.statut);
  }

  if (user?.role === ROLES.MAGASIN) {
    return request.statut === "EN_TRAITEMENT_MAGASIN";
  }

  if (user?.role === ROLES.GESTION && user?.scope_type === "DEPARTEMENT") {
    return request.statut === "EN_ATTENTE_DEPARTEMENT";
  }

  if (user?.role === ROLES.GESTION && user?.scope_type === "DIRECTION") {
    return ["EN_ATTENTE_DEPARTEMENT", "EN_TRAITEMENT_MAGASIN", "REJETEE"].includes(request.statut);
  }

  return false;
}

function notificationText(request) {
  const type = REQUEST_TYPE_LABELS[request.type_demande] || request.type_demande || "Demande";
  const status = REQUEST_STATUS_LABELS[request.statut] || request.statut || "Statut inconnu";
  const target = request.id_materiel ? `Materiel #${request.id_materiel}` : request.id_consommable ? `Consommable #${request.id_consommable}` : "Observation";
  return `${type} - ${status} - ${target}`;
}

function getNotificationKey(request) {
  return `${request.id_demande}:${request.statut || ""}`;
}

function getNotificationStorageKey(user) {
  const userKey = user?.id_users || user?.matricule || "anonymous";
  return `dismissed-request-notifications:${userKey}`;
}

async function fetchAllRequests() {
  const firstResponse = await apiClient.get("demandes/", { params: { page: 1, perpage: 50 } });
  const firstPage = normalizePage(firstResponse.data);
  const results = [...firstPage.results];

  if (firstPage.totalPages > 1) {
    const pages = Array.from({ length: firstPage.totalPages - 1 }, (_, index) => index + 2);
    const responses = await Promise.all(pages.map((page) => apiClient.get("demandes/", { params: { page, perpage: 50 } })));
    responses.forEach((response) => {
      results.push(...normalizePage(response.data).results);
    });
  }

  return results;
}

export default function Header({ user, onToggleSidebar, onLogout }) {
  const navigate = useNavigate();
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [requestNotifications, setRequestNotifications] = useState([]);
  const [notificationError, setNotificationError] = useState("");
  const [dismissedNotifications, setDismissedNotifications] = useState(new Set());
  const headerRef = useRef(null);

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(getNotificationStorageKey(user));
      setDismissedNotifications(new Set(stored ? JSON.parse(stored) : []));
    } catch {
      setDismissedNotifications(new Set());
    }
  }, [user]);

  useEffect(() => {
    let isMounted = true;

    const loadNotifications = async () => {
      if (!user?.role) return;
      try {
        const requests = await fetchAllRequests();
        if (!isMounted) return;
        setRequestNotifications(
          requests
            .filter((request) => requestNeedsAttention(request, user))
            .filter((request) => !dismissedNotifications.has(getNotificationKey(request)))
            .sort((left, right) => new Date(right.date_demande || 0) - new Date(left.date_demande || 0)),
        );
        setNotificationError("");
      } catch (error) {
        if (!isMounted) return;
        setNotificationError(getApiErrorMessage(error));
      }
    };

    loadNotifications();
    const intervalId = window.setInterval(loadNotifications, 60000);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, [dismissedNotifications, user]);

  useEffect(() => {
    const closeOnOutsideClick = (event) => {
      if (!headerRef.current?.contains(event.target)) {
        setIsNotificationOpen(false);
        setIsProfileOpen(false);
      }
    };

    document.addEventListener("mousedown", closeOnOutsideClick);
    return () => document.removeEventListener("mousedown", closeOnOutsideClick);
  }, []);

  const dismissNotification = (notification) => {
    const notificationKey = getNotificationKey(notification);
    setDismissedNotifications((current) => {
      const next = new Set(current);
      next.add(notificationKey);
      window.localStorage.setItem(getNotificationStorageKey(user), JSON.stringify([...next]));
      return next;
    });
    setRequestNotifications((current) => current.filter((item) => getNotificationKey(item) !== notificationKey));
  };

  return (
    <header className={styles.header} ref={headerRef}>
      <div className={styles.start}>
        <button type="button" className={styles.iconButton} onClick={onToggleSidebar} aria-label="Reduire ou afficher le menu lateral">
          <PanelLeftClose className={styles.desktopToggle} size={19} />
          <Menu className={styles.mobileToggle} size={20} />
        </button>

        <label className={styles.search}>
          <Search size={18} aria-hidden="true" />
          <input type="search" placeholder="Rechercher dans l'inventaire..." />
          <kbd>Ctrl K</kbd>
        </label>
      </div>

      <div className={styles.actions}>
        <div className={styles.dropdownWrapper}>
          <button
            type="button"
            className={styles.iconButton}
            onClick={() => { setIsNotificationOpen((open) => !open); setIsProfileOpen(false); }}
            aria-expanded={isNotificationOpen}
            aria-label="Afficher les notifications"
          >
            <Bell size={19} />
            {requestNotifications.length > 0 && <span className={styles.notificationDot} />}
            {requestNotifications.length > 0 && <strong className={styles.notificationCount}>{requestNotifications.length > 9 ? "9+" : requestNotifications.length}</strong>}
          </button>

          {isNotificationOpen && (
            <section className={`${styles.dropdown} ${styles.notifications}`} aria-label="Notifications">
              <div className={styles.dropdownHeader}><strong>Notifications</strong><span>{requestNotifications.length}</span></div>
              <div className={styles.notificationList}>
                {notificationError && <div className={styles.notificationMessage}>{notificationError}</div>}
                {!notificationError && requestNotifications.length === 0 && <div className={styles.notificationMessage}>Aucune demande en attente.</div>}
                {requestNotifications.slice(0, 6).map((notification) => (
                  <article className={styles.notification} key={getNotificationKey(notification)}>
                    <button
                      type="button"
                      className={styles.notificationContent}
                      onClick={() => {
                        setIsNotificationOpen(false);
                        navigate("/demandes");
                      }}
                    >
                      <i aria-hidden="true" className={notification.statut === "EN_TRAITEMENT_MAGASIN" ? styles.storeDot : ""} />
                      <span>
                        <strong>{notification.code_demande}</strong>
                        <small>{notificationText(notification)}</small>
                        <time>{notification.date_demande ? new Intl.DateTimeFormat("fr-CD").format(new Date(notification.date_demande)) : "Date non renseignee"}</time>
                      </span>
                    </button>
                    <button
                      type="button"
                      className={styles.dismissNotification}
                      onClick={() => dismissNotification(notification)}
                      aria-label="Retirer cette notification"
                      title="Retirer"
                    >
                      <X size={14} />
                    </button>
                  </article>
                ))}
              </div>
              <button
                type="button"
                className={styles.allNotifications}
                onClick={() => {
                  setIsNotificationOpen(false);
                  navigate("/demandes");
                }}
              >
                Voir les demandes
              </button>
            </section>
          )}
        </div>

        <div className={styles.dropdownWrapper}>
          <button
            type="button"
            className={styles.profileButton}
            onClick={() => { setIsProfileOpen((open) => !open); setIsNotificationOpen(false); }}
            aria-expanded={isProfileOpen}
            aria-label="Ouvrir le menu utilisateur"
          >
            <span className={styles.avatar} aria-hidden="true">{initials(user?.nom_users)}</span>
            <span className={styles.userText}><strong>{user?.nom_users || "Utilisateur"}</strong><small>{roleLabel(user?.role)}</small></span>
            <ChevronDown className={isProfileOpen ? styles.chevronOpen : ""} size={16} />
          </button>

          {isProfileOpen && (
            <section className={`${styles.dropdown} ${styles.profileMenu}`} aria-label="Menu utilisateur">
              <div className={styles.profileSummary}><span className={styles.avatar} aria-hidden="true">{initials(user?.nom_users)}</span><span><strong>{user?.nom_users || "Utilisateur"}</strong><small>{user?.email || user?.matricule}</small></span></div>
              <div className={styles.menuLinks}>
                <button type="button"><UserRound size={16} /> Mon profil</button>
                <button type="button"><Settings size={16} /> Preferences</button>
              </div>
              <button type="button" className={styles.logoutMenuButton} onClick={onLogout}><LogOut size={16} /> Se deconnecter</button>
            </section>
          )}
        </div>
      </div>
    </header>
  );
}
