import { ArrowUpDown, ChevronLeft, ChevronRight, Eye, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
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
  EN_ATTENTE: "En attente",
  NEUF: "Neuf",
  BON: "Bon",
  EN_STOCK: "En stock",
  AFFECTE: "Affecte",
  HORS_STOCK: "Hors stock",
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
  FACTURE: "Facture",
  BON_LIVRAISON: "Bon livraison",
  GARANTIE: "Garantie",
  FICHE_TECHNIQUE: "Fiche technique",
  DEPARTEMENT: "Departement",
  DIRECTION: "Direction",
  UTILISATEUR: "Utilisateur",
  AGENT: "Agent",
  MAGASIN: "Magasin",
  GENERAL: "General",
  PARTIEL: "Partiel",
  PERIODIQUE: "Periodique",
  EXCEPTIONNEL: "Exceptionnel",
  PREVENTIF: "Preventif",
  CORRECTIF: "Correctif",
  CONTROLE: "Controle",
  AUCUN: "Aucun",
  INTERNE: "Interne",
  PRESTATAIRE: "Prestataire",
  CONSTRUCTEUR: "Constructeur",
  ADMIN: "Administrateur",
  GESTION: "Gestion",
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
  EN_COURS: "info",
  AFFECTE: "info",
  HORS_STOCK: "neutral",
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
  return column.type === "boolean" || [
    "statut",
    "statut_stock",
    "etat",
    "type_mouvement",
    "type_demande",
    "type_document",
    "type_inventaire",
    "type_entretien",
    "type_prestataire",
    "entite_type",
    "scope_type",
    "role",
  ].includes(column.key);
}

function formatLabel(value) {
  const key = String(value);
  if (Object.prototype.hasOwnProperty.call(VALUE_LABELS, key)) return VALUE_LABELS[key];
  return key.replaceAll("_", " ").toLowerCase().replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

function columnClassName(column) {
  return column.highlight ? styles[`${column.highlight}Column`] : "";
}

function resolveColumnField(column, fieldByName) {
  return fieldByName[column.key] || column;
}

function isCodeColumn(column, field) {
  return /^code_/.test(column.key || "") || /^code_/.test(field?.name || "");
}

function getSelectLabel(value, field, options) {
  const fieldOptions = field.options || options[field.resource] || [];
  const match = fieldOptions.find((option) => {
    const optionValue = typeof option === "string" ? option : option.value;
    return String(optionValue) === String(value);
  });
  if (!match) return "";
  return typeof match === "string" ? formatLabel(match) : match.label;
}

function renderValue(row, column, fieldByName, options) {
  const field = resolveColumnField(column, fieldByName);
  const value = row[column.key];
  if (isCodeColumn(column, field) && value !== null && value !== undefined && value !== "") {
    return String(value).toUpperCase();
  }
  if (shouldRenderBadge(column) && value !== null && value !== undefined && value !== "") {
    const variant = BADGE_VARIANTS[String(value)] || "neutral";
    return <span className={`${styles.badge} ${styles[variant]}`}>{formatLabel(value)}</span>;
  }
  if ((column.type === "date" || field.type === "date") && value) return new Intl.DateTimeFormat("fr-CD").format(new Date(value));
  if (field.type === "select" && value !== null && value !== undefined && value !== "") {
    return getSelectLabel(value, field, options) || String(value);
  }
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "string" && (Object.prototype.hasOwnProperty.call(VALUE_LABELS, value) || /^[A-Z_]+$/.test(value))) {
    return formatLabel(value);
  }
  return String(value);
}

function menuActionClassName(action) {
  return [styles.menuItem, action.variant ? styles[`action${action.variant}`] : ""].filter(Boolean).join(" ");
}

function isStatusAction(action) {
  return /panne|reparation|hors service|statut|situation|valider|rejeter|finaliser|retour/i.test(action.label || "");
}

export default function DataTable({
  columns,
  fields = [],
  options = {},
  rows,
  page,
  totalPages,
  count,
  viewMode = "table",
  canEdit,
  canDelete,
  canView = true,
  customActions = [],
  onView,
  onEdit,
  onDelete,
  onBulkDelete,
  onCustomAction,
  onPageChange,
  onSort,
  sortableColumns,
}) {
  const [selectedKeys, setSelectedKeys] = useState(() => new Set());
  const [openMenu, setOpenMenu] = useState(null);
  const [openStatusKey, setOpenStatusKey] = useState("");
  const showActions = canView || canEdit || canDelete || customActions.length > 0;
  const sortableKeys = new Set((sortableColumns || columns).map((column) => column.key));
  const fieldByName = Object.fromEntries(fields.map((field) => [field.name, field]));
  const selectedRows = useMemo(
    () => rows.filter((row) => selectedKeys.has(String(row.__rowKey))),
    [rows, selectedKeys],
  );
  const allVisibleSelected = rows.length > 0 && selectedRows.length === rows.length;

  useEffect(() => {
    setSelectedKeys(new Set());
    setOpenMenu(null);
    setOpenStatusKey("");
  }, [rows]);

  if (!rows.length) return <EmptyState />;

  const toggleRow = (row) => {
    const key = String(row.__rowKey);
    setSelectedKeys((current) => {
      const next = new Set(current);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const toggleAllVisible = () => {
    setSelectedKeys((current) => {
      if (rows.every((row) => current.has(String(row.__rowKey)))) return new Set();
      return new Set(rows.map((row) => String(row.__rowKey)));
    });
  };

  const closeMenus = () => {
    setOpenMenu(null);
    setOpenStatusKey("");
  };

  const runAction = (callback) => {
    closeMenus();
    callback();
  };

  const runBulkDelete = () => {
    if (!selectedRows.length) return;
    onBulkDelete?.(selectedRows);
  };

  const toggleMenu = (event, row) => {
    const key = String(row.__rowKey);
    const rect = event.currentTarget.getBoundingClientRect();
    setOpenMenu((current) => {
      if (current?.key === key) return null;
      const menuWidth = 220;
      return {
        key,
        row,
        top: rect.bottom + 8,
        left: Math.max(12, Math.min(rect.right - menuWidth, window.innerWidth - menuWidth - 12)),
      };
    });
  };

  const renderFloatingMenu = () => {
    if (!openMenu) return null;
    const row = openMenu.row;
    const visibleCustomActions = customActions.filter((action) => !action.visibleWhen || action.visibleWhen(row));
    const statusActions = visibleCustomActions.filter(isStatusAction);
    const directActions = visibleCustomActions.filter((action) => !isStatusAction(action));

    return (
      <div className={`${styles.rowMenu} ${styles.floatingMenu}`} style={{ top: openMenu.top, left: openMenu.left }} role="menu">
        {canView && <button type="button" className={styles.menuItem} onClick={() => runAction(() => onView(row))}>Voir</button>}
        {canEdit && <button type="button" className={styles.menuItem} onClick={() => runAction(() => onEdit(row))}>Modifier</button>}
        {statusActions.length > 0 && (
          <div
            className={styles.menuWithSubmenu}
            onMouseEnter={() => setOpenStatusKey(openMenu.key)}
            onMouseLeave={() => setOpenStatusKey("")}
          >
            <button
              type="button"
              className={styles.menuItem}
              onClick={() => setOpenStatusKey((current) => (current === openMenu.key ? "" : openMenu.key))}
            >
              Statut / situation
            </button>
            {openStatusKey === openMenu.key && (
              <div className={styles.rowSubmenu} role="menu">
                {statusActions.map((action) => (
                  <button type="button" className={menuActionClassName(action)} onClick={() => runAction(() => onCustomAction(action, row))} key={action.label}>
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        {directActions.map((action) => (
          <button type="button" className={menuActionClassName(action)} onClick={() => runAction(() => onCustomAction(action, row))} key={action.label}>
            {action.label}
          </button>
        ))}
        {canDelete && (
          <button type="button" className={`${styles.menuItem} ${styles.menuDanger}`} onClick={() => runAction(() => onDelete(row))}>
            Supprimer
          </button>
        )}
      </div>
    );
  };

  const renderActions = (row) => showActions && (
    <div className={styles.actions} data-menu-open={openMenu?.key === String(row.__rowKey) ? "true" : undefined}>
      {canView && (
        <button type="button" className={styles.iconAction} onClick={() => runAction(() => onView(row))} aria-label="Voir le detail" title="Voir">
          <Eye size={16} />
        </button>
      )}
      {canEdit && (
        <button type="button" className={styles.iconAction} onClick={() => runAction(() => onEdit(row))} aria-label="Modifier" title="Modifier">
          <Pencil size={16} />
        </button>
      )}
      <div className={styles.actionMenuWrap}>
        <button
          type="button"
          className={styles.iconAction}
          onClick={(event) => toggleMenu(event, row)}
          aria-label="Plus d'actions"
          aria-expanded={openMenu?.key === String(row.__rowKey)}
          title="Actions"
        >
          <MoreHorizontal size={17} />
        </button>
      </div>
    </div>
  );

  return (
    <div className={styles.wrap}>
      {selectedRows.length > 0 && (
        <div className={styles.bulkBar} role="status">
          <strong>{selectedRows.length} selectionne(s)</strong>
          <div>
            {canDelete && (
              <button type="button" className={styles.bulkDanger} onClick={runBulkDelete}>
                <Trash2 size={16} /> Supprimer
              </button>
            )}
            <button type="button" onClick={() => setSelectedKeys(new Set())}>Deselectionner</button>
          </div>
        </div>
      )}
      {viewMode === "cards" ? (
        <div className={styles.cardGrid}>
          {rows.map((row) => {
            const [primaryColumn, ...detailColumns] = columns;
            const badgeColumns = detailColumns.filter((column) => shouldRenderBadge(column));
            const plainColumns = detailColumns.filter((column) => !shouldRenderBadge(column));
            return (
              <article className={styles.recordCard} key={row.__rowKey}>
                <header className={styles.cardHeader}>
                  <label className={styles.cardSelect} aria-label="Selectionner la ligne">
                    <input type="checkbox" checked={selectedKeys.has(String(row.__rowKey))} onChange={() => toggleRow(row)} />
                  </label>
                  <div>
                    <span>{primaryColumn?.label || "Reference"}</span>
                    <strong>{primaryColumn ? renderValue(row, primaryColumn, fieldByName, options) : row.__rowKey}</strong>
                  </div>
                  <em>#{row.__rowKey}</em>
                </header>
                {badgeColumns.length > 0 && (
                  <div className={styles.cardBadges}>
                    {badgeColumns.map((column) => <span key={column.key}>{renderValue(row, column, fieldByName, options)}</span>)}
                  </div>
                )}
                <dl className={styles.cardDetails}>
                  {plainColumns.map((column) => (
                    <div key={column.key}>
                      <dt>{column.label}</dt>
                      <dd>{renderValue(row, column, fieldByName, options)}</dd>
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
                <th className={styles.selectionHeader}>
                  <input type="checkbox" checked={allVisibleSelected} onChange={toggleAllVisible} aria-label="Selectionner toutes les lignes visibles" />
                </th>
                {columns.map((column) => (
                  <th className={columnClassName(column)} key={column.key}>
                    {onSort && sortableKeys.has(column.key) ? (
                      <button type="button" className={styles.sortHeader} onClick={() => onSort(column.key)}>
                        <span>{column.label}</span>
                        <ArrowUpDown size={14} />
                      </button>
                    ) : column.label}
                  </th>
                ))}
                {showActions && <th className={styles.actionsHeader}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr className={selectedKeys.has(String(row.__rowKey)) ? styles.selectedRow : ""} key={row.__rowKey}>
                  <td className={styles.selectionCell}>
                    <input type="checkbox" checked={selectedKeys.has(String(row.__rowKey))} onChange={() => toggleRow(row)} aria-label="Selectionner la ligne" />
                  </td>
                  {columns.map((column) => <td className={columnClassName(column)} key={column.key}>{renderValue(row, column, fieldByName, options)}</td>)}
                  {showActions && <td>{renderActions(row)}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {renderFloatingMenu()}
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
