import { Boxes, PackageCheck, PackageSearch, TriangleAlert, Warehouse } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { getDashboardStats } from "../../api/dashboardApi";
import EmptyState from "../../components/common/EmptyState";
import ErrorAlert from "../../components/common/ErrorAlert";
import LoadingState from "../../components/common/LoadingState";
import { formatDate, formatNumber } from "../../utils/format";
import { getApiErrorMessage } from "../../utils/apiErrors";
import styles from "./Dashboard.module.css";

const AUTO_REFRESH_MS = 10000;

function buildMetrics(metrics = {}) {
  return [
    { label: "Materiels", value: metrics.materiels_total, hint: `${metrics.materiels_affectes || 0} affectes`, icon: PackageSearch, tone: "info" },
    { label: "Consommables", value: metrics.consommables_total, hint: "Lignes de stock", icon: Boxes, tone: "neutral" },
    { label: "Magasins", value: metrics.magasins_total, hint: "Emplacements", icon: Warehouse, tone: "neutral" },
    { label: "A reparer", value: metrics.materiels_en_reparation, hint: "En intervention", icon: PackageCheck, tone: "warning" },
    { label: "Stock faible", value: metrics.stock_faible, hint: "A traiter", icon: TriangleAlert, tone: "danger" },
  ];
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async ({ silent = false } = {}) => {
    if (!silent) {
      setIsLoading(true);
      setError("");
    }
    try {
      setDashboard(await getDashboardStats());
    } catch (loadError) {
      if (!silent) setError(getApiErrorMessage(loadError));
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    const refresh = () => {
      if (document.visibilityState === "visible") loadDashboard({ silent: true });
    };

    const intervalId = window.setInterval(refresh, AUTO_REFRESH_MS);
    window.addEventListener("focus", refresh);
    document.addEventListener("visibilitychange", refresh);

    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener("focus", refresh);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [loadDashboard]);

  if (isLoading) return <LoadingState label="Chargement du tableau de bord..." />;

  const metrics = buildMetrics(dashboard?.metrics);
  const movements = dashboard?.recent_movements || [];
  const stockAlerts = dashboard?.stock_alerts || [];

  return (
    <div>
      <section className={styles.pageHeading}>
        <div>
          <h1>Tableau de bord</h1>
          <p className={styles.description}>Les priorites d'inventaire, les alertes et les derniers mouvements.</p>
        </div>
        <div className={styles.dateBadge}>{formatDate(new Date().toISOString())}</div>
      </section>

      <ErrorAlert message={error} onRetry={loadDashboard} />

      <section className={styles.metrics} aria-label="Indicateurs cles">
        {metrics.map(({ label, value, hint, icon: Icon, tone }) => (
          <article className={styles.metricCard} key={label}>
            <div className={`${styles.metricIcon} ${styles[tone]}`}><Icon size={18} /></div>
            <span>{label}</span>
            <strong>{formatNumber(value)}</strong>
            <p>{hint}</p>
          </article>
        ))}
      </section>

      <section className={styles.dashboardGrid}>
        <article className={`${styles.panel} ${styles.alertPanel}`}>
          <div className={styles.panelHeader}>
            <div><h2>Alertes de stock</h2><p>Consommables sous le seuil minimum</p></div>
            <span className={styles.alertCount}>{stockAlerts.length}</span>
          </div>
          {stockAlerts.length ? (
            <div className={styles.alertList}>
              {stockAlerts.map((item) => {
                const stock = Number(item.quantite_stock || 0);
                const threshold = Number(item.seuil_alerte || 1);
                const level = Math.min(100, Math.round((stock / threshold) * 100));
                return (
                  <div className={styles.alertItem} key={item.id_consommable}>
                    <div className={styles.alertText}><strong>{item.nom_consommable}</strong><span>{formatNumber(stock)} / {formatNumber(threshold)}</span></div>
                    <div className={styles.stockLevel}><div><i className={styles[level <= 25 ? "danger" : "warning"]} style={{ width: `${level}%` }} /></div><span>{level}%</span></div>
                  </div>
                );
              })}
            </div>
          ) : <EmptyState title="Aucune alerte" description="Aucun consommable n'est sous son seuil." />}
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeader}>
            <div><h2>Lecture rapide</h2><p>Ce qui demande le plus d'attention</p></div>
          </div>
          <div className={styles.focusList}>
            <div><span>References</span><strong>{formatNumber((dashboard?.metrics?.materiels_total || 0) + (dashboard?.metrics?.consommables_total || 0))}</strong></div>
            <div><span>Materiels affectes</span><strong>{formatNumber(dashboard?.metrics?.materiels_affectes)}</strong></div>
            <div><span>Stock faible</span><strong>{formatNumber(dashboard?.metrics?.stock_faible)}</strong></div>
          </div>
        </article>
      </section>

      <section className={styles.panel}>
        <div className={styles.panelHeader}><div><h2>Mouvements recents</h2><p>Les dernieres operations enregistrees</p></div></div>
        {movements.length ? (
          <div className={styles.tableWrap}>
            <table>
              <thead><tr><th>ID</th><th>Type</th><th>Article</th><th>Quantite</th><th>Source</th><th>Destination</th><th>Date</th></tr></thead>
              <tbody>
                {movements.map((movement) => (
                  <tr key={movement.id_mouvement}>
                    <td className={styles.reference}>{movement.id_mouvement}</td>
                    <td><span className={`${styles.status} ${movement.type_mouvement === "ENTREE" ? styles.success : styles.neutral}`}>{movement.type_mouvement}</span></td>
                    <td>{movement.article || "-"}</td>
                    <td className={styles.quantity}>{movement.quantite}</td>
                    <td>{movement.magasin_source_nom || "-"}</td>
                    <td>{movement.magasin_destination_nom || "-"}</td>
                    <td className={styles.muted}>{formatDate(movement.date_mouvement)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <EmptyState title="Aucun mouvement" description="Aucune operation n'a encore ete enregistree." />}
      </section>
    </div>
  );
}
