import { ArrowDownRight, ArrowUpRight, Boxes, PackageCheck, TriangleAlert, Wrench } from "lucide-react";
import { useEffect, useState } from "react";
import { getDashboardStats } from "../../api/dashboardApi";
import EmptyState from "../../components/common/EmptyState";
import ErrorAlert from "../../components/common/ErrorAlert";
import LoadingState from "../../components/common/LoadingState";
import { formatDate, formatNumber } from "../../utils/format";
import { getApiErrorMessage } from "../../utils/apiErrors";
import styles from "./Dashboard.module.css";

function buildMetrics(metrics = {}) {
  return [
    { label: "Materiels", value: metrics.materiels_total, change: "Total", icon: Boxes, trend: "up" },
    { label: "Consommables", value: metrics.consommables_total, change: "References", icon: ArrowDownRight, trend: "up" },
    { label: "Stock disponible", value: metrics.stock_disponible, change: "Quantite", icon: PackageCheck, trend: "down" },
    { label: "Stock faible", value: metrics.stock_faible, change: "A traiter", icon: TriangleAlert, trend: "alert" },
    { label: "Affectes", value: metrics.materiels_affectes, change: "Materiels", icon: ArrowUpRight, trend: "down" },
    { label: "En reparation", value: metrics.materiels_en_reparation, change: "Maintenance", icon: Wrench, trend: "alert" },
  ];
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = async () => {
    setIsLoading(true);
    setError("");
    try {
      setDashboard(await getDashboardStats());
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (isLoading) return <LoadingState label="Chargement du tableau de bord..." />;

  const metrics = buildMetrics(dashboard?.metrics);
  const movements = dashboard?.recent_movements || [];
  const stockAlerts = dashboard?.stock_alerts || [];

  return (
    <div>
      <section className={styles.pageHeading}>
        <div>
          <p className={styles.eyebrow}>Vue d'ensemble</p>
          <h1>Tableau de bord</h1>
          <p className={styles.description}>Etat actuel de l'inventaire selon les donnees du backend.</p>
        </div>
        <div className={styles.dateBadge}>{formatDate(new Date().toISOString())}</div>
      </section>

      <ErrorAlert message={error} onRetry={loadDashboard} />

      <section className={styles.metrics} aria-label="Indicateurs cles">
        {metrics.map(({ label, value, change, icon: Icon, trend }) => (
          <article className={styles.metricCard} key={label}>
            <div className={`${styles.metricIcon} ${styles[trend]}`}><Icon size={21} /></div>
            <p>{label}</p>
            <strong>{formatNumber(value)}</strong>
            <span className={`${styles.metricChange} ${styles[trend]}`}>{change}</span>
          </article>
        ))}
      </section>

      <section className={styles.dashboardGrid}>
        <article className={`${styles.panel} ${styles.activityPanel}`}>
          <div className={styles.panelHeader}>
            <div><h2>Activite de l'inventaire</h2><p>Derniers mouvements enregistres</p></div>
          </div>
          {movements.length ? (
            <div className={styles.chart} aria-label="Graphique indicatif des mouvements de stock">
              {movements.slice(0, 6).map((movement, index) => {
                const height = Math.min(95, Math.max(20, Number(movement.quantite || 1) * 12));
                return (
                  <div className={styles.chartColumn} key={movement.id_mouvement || index}>
                    <div className={styles.bars}>
                      <span className={styles.entryBar} style={{ height: `${height}%` }} />
                      <span className={styles.exitBar} style={{ height: `${Math.max(height - 22, 18)}%` }} />
                    </div>
                    <span>{movement.type_mouvement}</span>
                  </div>
                );
              })}
            </div>
          ) : <EmptyState title="Aucun mouvement" description="Les mouvements apparaitront ici apres saisie." />}
        </article>

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
                    <div className={styles.alertText}><strong>{item.nom_consommable}</strong><span>Stock actuel : {formatNumber(stock)}</span></div>
                    <div className={styles.stockLevel}><div><i className={styles[level <= 25 ? "danger" : "warning"]} style={{ width: `${level}%` }} /></div><span>{level}%</span></div>
                  </div>
                );
              })}
            </div>
          ) : <EmptyState title="Aucune alerte" description="Aucun consommable n'est sous son seuil." />}
        </article>
      </section>

      <section className={styles.panel}>
        <div className={styles.panelHeader}><div><h2>Mouvements recents</h2><p>Les dernieres operations enregistrees</p></div></div>
        {movements.length ? (
          <div className={styles.tableWrap}>
            <table>
              <thead><tr><th>ID</th><th>Type</th><th>Quantite</th><th>Source</th><th>Destination</th><th>Date</th></tr></thead>
              <tbody>
                {movements.map((movement) => (
                  <tr key={movement.id_mouvement}>
                    <td className={styles.reference}>{movement.id_mouvement}</td>
                    <td><span className={`${styles.status} ${movement.type_mouvement === "ENTREE" ? styles.success : styles.neutral}`}>{movement.type_mouvement}</span></td>
                    <td className={styles.quantity}>{movement.quantite}</td>
                    <td>{movement.magasin_source || "-"}</td>
                    <td>{movement.magasin_destination || "-"}</td>
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
