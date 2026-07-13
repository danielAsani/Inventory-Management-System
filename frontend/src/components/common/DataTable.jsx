import { ArrowUpDown, ChevronLeft, ChevronRight, Eye, Pencil, Trash2 } from "lucide-react";
import EmptyState from "./EmptyState";
import styles from "./DataTable.module.css";

const VALUE_LABELS = {
  true: "Actif",
  false: "Inactif",
  EN_ATTENTE_DEPARTEMENT: "En attente departement",
  EN_TRAITEMENT_MAGASIN: "Au magasin",
  TRAITEE: "Traitee",
  REJETEE: "Rejetee",
  ANNULEE: "Annulee",
  ACTIVE: "Active",
  RETOURNEE: "Retournee",
  EN_COURS: "En cours",
  TERMINE: "Termine",
  TERMINEE: "Terminee",
  PLANIFIE: "Planifie",
  EN_ATTENTE: "En attente",
  NEUF: "Neuf",
  BON: "Bon",
  EN_STOCK: "En stock",
  AFFECTE: "Affecte",
  EN_PANNE: "En panne",
  EN_REPARATION: "En reparation",
  HORS_SERVICE: "Hors service",
  ENTREE: "Entree",
  SORTIE: "Sortie",
  TRANSFERT: "Transfert",
  AJUSTEMENT: "Ajustement",
  ACHAT: "Achat",
  REAPPROVISIONNEMENT: "Reappro.",
  REPARATION: "Reparation",
  AUTRE: "Autre",
};

const BADGE_VARIANTS = {
  true: "success",
  false: "danger",
  TRAITEE: "success",
  TERMINE: "success",
  TERMINEE: "success",
  ACTIVE: "success",
  EN_STOCK: "success",
  BON: "success",
  NEUF: "info",
  EN_ATTENTE_DEPARTEMENT: "warning",
  EN_TRAITEMENT_MAGASIN: "info",
  EN_ATTENTE: "warning",
  PLANIFIE: "neutral",
  EN_COURS: "info",
  AFFECTE: "info",
  REJETEE: "danger",
  ANNULEE: "danger",
  ANNULE: "danger",
  HORS_SERVICE: "danger",
  EN_PANNE: "danger",
  EN_REPARATION: "warning",
  RETOURNEE: "neutral",
  ENTREE: "success",
  SORTIE: "danger",
  TRANSFERT: "info",
  AJUSTEMENT: "warning",
  ACHAT: "info",
  REAPPROVISIONNEMENT: "success",
  REPARATION: "warning",
  AUTRE: "neutral",
};

function shouldRenderBadge(column) {
  return column.type === "boolean" || ["statut", "etat", "type_mouvement", "type_demande"].includes(column.key);
}

function formatLabel(value) {
  const key = String(value);
  if (Object.prototype.hasOwnProperty.call(VALUE_LABELS, key)) return VALUE_LABELS[key];
  return key.replaceAll("_", " ").toLowerCase().replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

function renderValue(row, column) {
  const value = row[column.key];
  if (shouldRenderBadge(column) && value !== null && value !== undefined && value !== "") {
    const variant = BADGE_VARIANTS[String(value)] || "neutral";
    return <span className={`${styles.badge} ${styles[variant]}`}>{formatLabel(value)}</span>;
  }
  if (column.type === "date" && value) return new Intl.DateTimeFormat("fr-CD").format(new Date(value));
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

export default function DataTable({
  columns,
  rows,
  page,
  totalPages,
  count,
  viewMode = "table",
  sortKey,
  sortDirection,
  canEdit,
  canDelete,
  canView = true,
  customActions = [],
  onView,
  onEdit,
  onDelete,
  onCustomAction,
  onPageChange,
  onSort,
}) {
  if (!rows.length) return <EmptyState />;
  const showActions = canView || canEdit || canDelete || customActions.length > 0;

  const renderActions = (row) => showActions && (
    <div className={styles.actions}>
      {canView && <button type="button" className={styles.iconAction} onClick={() => onView(row)} aria-label="Voir le detail"><Eye size={16} /></button>}
      {customActions
        .filter((action) => !action.visibleWhen || action.visibleWhen(row))
        .map((action) => (
          <button type="button" className={styles.textAction} onClick={() => onCustomAction(action, row)} key={action.label}>
            {action.label}
          </button>
        ))}
      {canEdit && <button type="button" className={styles.iconAction} onClick={() => onEdit(row)} aria-label="Modifier"><Pencil size={16} /></button>}
      {canDelete && <button type="button" className={styles.iconAction} onClick={() => onDelete(row)} aria-label="Supprimer"><Trash2 size={16} /></button>}
    </div>
  );

  return (
    <div className={styles.wrap}>
      {viewMode === "cards" ? (
        <div className={styles.cardGrid}>
          {rows.map((row) => {
            const [primaryColumn, ...detailColumns] = columns;
            const badgeColumns = detailColumns.filter((column) => shouldRenderBadge(column));
            const plainColumns = detailColumns.filter((column) => !shouldRenderBadge(column));
            return (
              <article className={styles.recordCard} key={row.__rowKey}>
                <header className={styles.cardHeader}>
                  <div>
                    <span>{primaryColumn?.label || "Reference"}</span>
                    <strong>{primaryColumn ? renderValue(row, primaryColumn) : row.__rowKey}</strong>
                  </div>
                  <em>#{row.__rowKey}</em>
                </header>
                {badgeColumns.length > 0 && (
                  <div className={styles.cardBadges}>
                    {badgeColumns.map((column) => <span key={column.key}>{renderValue(row, column)}</span>)}
                  </div>
                )}
                <dl className={styles.cardDetails}>
                  {plainColumns.map((column) => (
                    <div key={column.key}>
                      <dt>{column.label}</dt>
                      <dd>{renderValue(row, column)}</dd>
                    </div>
                  ))}
                </dl>
                {renderActions(row)}
              </article>
            );
          })}
        </div>
      ) : (
        <div className={styles.tableScroller}>
          <table className={styles.table}>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column.key}>
                    {onSort ? (
                      <button type="button" className={styles.sortHeader} onClick={() => onSort(column.key)}>
                        <span>{column.label}</span>
                        <ArrowUpDown size={14} />
                        {sortKey === column.key && <em>{sortDirection === "asc" ? "Asc" : "Desc"}</em>}
                      </button>
                    ) : column.label}
                  </th>
                ))}
                {showActions && <th className={styles.actionsHeader}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.__rowKey}>
                  {columns.map((column) => <td key={column.key}>{renderValue(row, column)}</td>)}
                  {showActions && <td>{renderActions(row)}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className={styles.pagination}>
        <span>{count} enregistrement(s)</span>
        <div>
          <button type="button" onClick={() => onPageChange(page - 1)} disabled={page <= 1}><ChevronLeft size={16} /> Precedent</button>
          <strong>{page} / {totalPages || 1}</strong>
          <button type="button" onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}>Suivant <ChevronRight size={16} /></button>
        </div>
      </div>
    </div>
  );
}
