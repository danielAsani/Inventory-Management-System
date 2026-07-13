import { ArrowDown, ArrowUp, LayoutGrid, Plus, Search, Table2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { createResourceApi } from "../../api/resourceApi";
import DataTable from "../../components/common/DataTable";
import ErrorAlert from "../../components/common/ErrorAlert";
import LoadingState from "../../components/common/LoadingState";
import ResourceForm from "../../components/common/ResourceForm";
import { getResourceConfig, resourceConfigs } from "../../constants/resourceConfigs";
import { useAuth } from "../../hooks/useAuth";
import { getApiErrorMessage, normalizeFieldErrors } from "../../utils/apiErrors";
import { normalizePage } from "../../utils/pagination";
import { canWrite } from "../../utils/permissions";
import styles from "./ResourcePage.module.css";

const perpage = 10;
const CARD_FIRST_RESOURCES = new Set(["demandes", "materiels", "consommables", "documents"]);
const QUICK_FILTERS = {
  demandes: {
    label: "Type de demande",
    field: "type_demande",
    options: [
      { value: "ACHAT", label: "Achat" },
      { value: "REAPPROVISIONNEMENT", label: "Reappro" },
      { value: "REPARATION", label: "Reparation" },
      { value: "AUTRE", label: "Autre" },
    ],
  },
  materiels: {
    label: "Etat",
    field: "etat",
    options: [
      { value: "EN_STOCK", label: "En stock" },
      { value: "AFFECTE", label: "Affecte" },
      { value: "EN_PANNE", label: "En panne" },
      { value: "EN_REPARATION", label: "En reparation" },
      { value: "HORS_SERVICE", label: "Hors service" },
    ],
  },
  mouvements: {
    label: "Type de mouvement",
    field: "type_mouvement",
    options: [
      { value: "ENTREE", label: "Entree" },
      { value: "SORTIE", label: "Sortie" },
      { value: "TRANSFERT", label: "Transfert" },
      { value: "AJUSTEMENT", label: "Ajustement" },
    ],
  },
  documents: {
    label: "Type de document",
    field: "type_document",
    options: [
      { value: "FACTURE", label: "Facture" },
      { value: "BON_LIVRAISON", label: "Bon livraison" },
      { value: "GARANTIE", label: "Garantie" },
      { value: "FICHE_TECHNIQUE", label: "Fiche technique" },
      { value: "PHOTO", label: "Photo" },
      { value: "AUTRE", label: "Autre" },
    ],
  },
  inventaires: {
    label: "Type d'inventaire",
    field: "type_inventaire",
    options: [
      { value: "GENERAL", label: "General" },
      { value: "PARTIEL", label: "Partiel" },
      { value: "PERIODIQUE", label: "Periodique" },
      { value: "EXCEPTIONNEL", label: "Exceptionnel" },
    ],
  },
  entretiens: {
    label: "Type d'entretien",
    field: "type_entretien",
    options: [
      { value: "PREVENTIF", label: "Preventif" },
      { value: "CORRECTIF", label: "Correctif" },
      { value: "CONTROLE", label: "Controle" },
    ],
  },
  affectations: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "ACTIVE", label: "Active" },
      { value: "RETOURNEE", label: "Retournee" },
      { value: "ANNULEE", label: "Annulee" },
    ],
  },
  reparations: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "EN_ATTENTE", label: "En attente" },
      { value: "EN_COURS", label: "En cours" },
      { value: "TERMINEE", label: "Terminee" },
      { value: "ANNULEE", label: "Annulee" },
    ],
  },
};

function getOptionLabel(resourceKey, item) {
  const config = getResourceConfig(resourceKey);
  if (!config) return String(item.id || item.pk || "");
  const preferred = config.columns.find((column) => column.key.includes("nom_")) || config.columns[0];
  const secondary = config.columns.find((column) => column.key.includes("code_"));
  const label = item[preferred?.key] || item[secondary?.key] || item[config.idField];
  return String(label);
}

function getRowKey(config, item) {
  return item[config.idField] ?? item.id ?? item.pk;
}

function normalizeSortValue(value, column) {
  if (value === null || value === undefined) return "";
  if (column?.type === "date" || column?.key?.startsWith("date_")) {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? 0 : date.getTime();
  }
  const numberValue = Number(value);
  if (value !== "" && Number.isFinite(numberValue)) return numberValue;
  return String(value).toLocaleLowerCase("fr-CD");
}

function sortRows(rows, columns, sortKey, sortDirection) {
  if (!sortKey) return rows;
  const column = columns.find((item) => item.key === sortKey);
  const direction = sortDirection === "desc" ? -1 : 1;

  return [...rows].sort((left, right) => {
    const leftValue = normalizeSortValue(left[sortKey], column);
    const rightValue = normalizeSortValue(right[sortKey], column);
    if (leftValue < rightValue) return -1 * direction;
    if (leftValue > rightValue) return 1 * direction;
    return 0;
  });
}

function filterRows(rows, quickFilterConfig, quickFilter) {
  if (!quickFilterConfig || quickFilter === "all") return rows;
  return rows.filter((row) => String(row[quickFilterConfig.field]) === quickFilter);
}

async function loadResourceOptions(optionConfig) {
  const api = createResourceApi(optionConfig.endpoint);
  const firstResponse = await api.list({ page: 1, perpage: 50 });
  const firstPage = normalizePage(firstResponse);
  const results = [...firstPage.results];

  if (firstPage.totalPages > 1) {
    const remaining = Array.from({ length: firstPage.totalPages - 1 }, (_, index) => index + 2);
    const pages = await Promise.all(remaining.map((page) => api.list({ page, perpage: 50 })));
    pages.forEach((response) => {
      results.push(...normalizePage(response).results);
    });
  }

  return results;
}

function formatDetailValue(value, field, options) {
  if (field?.type === "checkbox") return value ? "Oui" : "Non";
  if ((field?.type === "date" || field?.name?.startsWith("date_")) && value) {
    return new Intl.DateTimeFormat("fr-CD").format(new Date(value));
  }
  if (field?.type === "select") {
    const match = (field.options || options[field.resource] || []).find((option) => {
      const optionValue = typeof option === "string" ? option : option.value;
      return String(optionValue) === String(value);
    });
    if (match) return typeof match === "string" ? match : match.label;
  }
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

function DetailModal({ config, item, options, onClose }) {
  const fields = config.fields.length ? config.fields : config.columns.map((column) => ({ name: column.key, label: column.label, type: column.type }));
  return (
    <div className={styles.modalBackdrop} role="presentation">
      <section className={`${styles.modal} ${styles.detailModal}`} role="dialog" aria-modal="true" aria-label="Detail">
        <header>
          <div>
            <h2>Detail</h2>
            <p>{config.title}</p>
          </div>
          <button type="button" onClick={onClose} aria-label="Fermer">x</button>
        </header>
        <div className={styles.detailGrid}>
          <div className={styles.detailHero}>
            <span>{config.idField}</span>
            <strong>{item[config.idField] ?? item.__rowKey}</strong>
          </div>
          {fields.map((field) => (
            <div className={styles.detailItem} key={field.name}>
              <span>{field.label}</span>
              <strong>{formatDetailValue(item[field.name], field, options)}</strong>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default function ResourcePage({ resourceKey }) {
  const config = getResourceConfig(resourceKey);
  const api = useMemo(() => createResourceApi(config.endpoint), [config.endpoint]);
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [data, setData] = useState({ count: 0, page: 1, totalPages: 1, results: [] });
  const [options, setOptions] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [editingItem, setEditingItem] = useState(null);
  const [viewingItem, setViewingItem] = useState(null);
  const [viewMode, setViewMode] = useState(CARD_FIRST_RESOURCES.has(resourceKey) ? "cards" : "table");
  const [sortKey, setSortKey] = useState(config.columns[0]?.key || "");
  const [sortDirection, setSortDirection] = useState("asc");
  const [quickFilter, setQuickFilter] = useState("all");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const createRoles = config.createRoles ?? config.writeRoles;
  const updateRoles = config.updateRoles ?? config.writeRoles;
  const deleteRoles = config.deleteRoles ?? config.writeRoles;
  const userCanCreate = canWrite(user, createRoles) && (!config.createWhen || config.createWhen(user));
  const userCanUpdate = canWrite(user, updateRoles);
  const userCanDelete = canWrite(user, deleteRoles);
  const customActions = (config.actions || []).filter(
    (action) => canWrite(user, action.roles) && (!action.canUse || action.canUse(user)),
  );
  const quickFilterConfig = QUICK_FILTERS[resourceKey] || null;

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const response = await api.list({ page, perpage, search: search || undefined });
      setData(normalizePage(response));
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }, [api, page, search]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    setViewMode(CARD_FIRST_RESOURCES.has(resourceKey) ? "cards" : "table");
    setSortKey(config.columns[0]?.key || "");
    setSortDirection("asc");
    setQuickFilter("all");
  }, [config.columns, resourceKey]);

  useEffect(() => {
    const resources = [...new Set(config.fields.map((field) => field.resource).filter(Boolean))];
    if (!resources.length) return;

    let isMounted = true;
    Promise.all(
      resources.map(async (key) => {
        const optionConfig = resourceConfigs[key];
        try {
          return [
            key,
            (await loadResourceOptions(optionConfig)).map((item) => ({ value: getRowKey(optionConfig, item), label: getOptionLabel(key, item) })),
          ];
        } catch {
          if (key === "users" && user?.id_users) {
            return [key, [{ value: user.id_users, label: user.nom_users || user.matricule }]];
          }
          return [key, []];
        }
      }),
    )
      .then((entries) => {
        if (isMounted) setOptions(Object.fromEntries(entries));
      })
      .catch(() => {
        if (isMounted) setOptions({});
      });

    return () => {
      isMounted = false;
    };
  }, [config.fields, user]);

  const rows = useMemo(
    () => data.results.map((item) => ({ ...item, __rowKey: getRowKey(config, item) })),
    [config, data.results],
  );
  const filteredRows = useMemo(
    () => filterRows(rows, quickFilterConfig, quickFilter),
    [quickFilter, quickFilterConfig, rows],
  );
  const sortedRows = useMemo(
    () => sortRows(filteredRows, config.columns, sortKey, sortDirection),
    [config.columns, filteredRows, sortDirection, sortKey],
  );
  const activeSortColumn = config.columns.find((column) => column.key === sortKey);

  const changeSort = (key) => {
    setSortKey((currentKey) => {
      if (currentKey === key) {
        setSortDirection((currentDirection) => (currentDirection === "asc" ? "desc" : "asc"));
        return currentKey;
      }
      setSortDirection("asc");
      return key;
    });
  };

  const openCreate = () => {
    setEditingItem(null);
    setFieldErrors({});
    setIsFormOpen(true);
  };

  const openEdit = (item) => {
    setEditingItem(item);
    setFieldErrors({});
    setIsFormOpen(true);
  };

  const openView = (item) => {
    setViewingItem(item);
  };

  const closeForm = () => {
    setIsFormOpen(false);
    setEditingItem(null);
    setFieldErrors({});
  };

  const submitForm = async (payload) => {
    setIsSubmitting(true);
    setFieldErrors({});
    setError("");
    try {
      if (editingItem) {
        await api.update(getRowKey(config, editingItem), payload);
      } else {
        await api.create(payload);
      }
      closeForm();
      loadData();
    } catch (submitError) {
      setFieldErrors(normalizeFieldErrors(submitError));
      setError(getApiErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  };

  const deleteItem = async (item) => {
    const confirmed = window.confirm("Confirmer la suppression de cet enregistrement ?");
    if (!confirmed) return;

    try {
      await api.remove(getRowKey(config, item));
      loadData();
    } catch (deleteError) {
      setError(getApiErrorMessage(deleteError));
    }
  };

  const runCustomAction = async (action, item) => {
    const payload = action.getPayload ? action.getPayload(item) : {};
    if (payload === null) return;

    try {
      setError("");
      await api.action(getRowKey(config, item), action.endpoint, payload);
      loadData();
    } catch (actionError) {
      setError(getApiErrorMessage(actionError));
    }
  };

  return (
    <div className={styles.page}>
      <section className={styles.heading}>
        <div>
          <p className={styles.eyebrow}>Donnees backend</p>
          <h1>{config.title}</h1>
          <p>{config.description}</p>
        </div>
        {userCanCreate && (
          <button type="button" className={styles.primaryButton} onClick={openCreate}>
            <Plus size={18} /> Nouveau
          </button>
        )}
      </section>

      <section className={styles.toolbar}>
        <label>
          <Search size={18} />
          <input
            type="search"
            placeholder="Rechercher..."
            value={search}
            onChange={(event) => {
              setPage(1);
              setSearch(event.target.value);
            }}
          />
        </label>
        <div className={styles.viewSwitch} aria-label="Mode d'affichage">
          <button type="button" className={viewMode === "cards" ? styles.activeView : ""} onClick={() => setViewMode("cards")}>
            <LayoutGrid size={16} /> Cartes
          </button>
          <button type="button" className={viewMode === "table" ? styles.activeView : ""} onClick={() => setViewMode("table")}>
            <Table2 size={16} /> Tableau
          </button>
        </div>
      </section>

      <section className={styles.sortPanel} aria-label="Tri des donnees">
        <div className={styles.sortSummary}>
          <span>Trier par</span>
          <small>{activeSortColumn?.label || "Aucun"} - {sortDirection === "asc" ? "Ascendant" : "Descendant"}</small>
        </div>
        <div className={styles.sortChips}>
          {config.columns.map((column) => (
            <button
              type="button"
              className={sortKey === column.key ? styles.activeSort : ""}
              onClick={() => changeSort(column.key)}
              key={column.key}
            >
              {column.label}
              {sortKey === column.key && (
                <span className={styles.sortDirectionIcon}>
                  {sortDirection === "asc" ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                  {sortDirection === "asc" ? "Asc" : "Desc"}
                </span>
              )}
            </button>
          ))}
        </div>
      </section>

      {quickFilterConfig && (
        <section className={styles.quickFilters} aria-label={`Filtrer par ${quickFilterConfig.label}`}>
          <div className={styles.quickFilterSummary}>
            <span>{quickFilterConfig.label}</span>
            <small>{filteredRows.length} resultat(s) sur cette page</small>
          </div>
          <div className={styles.filterChips}>
            <button
              type="button"
              className={quickFilter === "all" ? styles.activeFilter : ""}
              onClick={() => setQuickFilter("all")}
            >
              Tous
            </button>
            {quickFilterConfig.options.map((option) => (
              <button
                type="button"
                className={quickFilter === option.value ? styles.activeFilter : ""}
                onClick={() => setQuickFilter(option.value)}
                key={option.value}
              >
                {option.label}
              </button>
            ))}
          </div>
        </section>
      )}

      <ErrorAlert message={error} onRetry={loadData} />

      {isLoading ? (
        <LoadingState />
      ) : (
        <DataTable
          columns={config.columns}
          rows={sortedRows}
          page={data.page}
          totalPages={data.totalPages}
          count={data.count}
          viewMode={viewMode}
          sortKey={sortKey}
          sortDirection={sortDirection}
          canEdit={userCanUpdate}
          canDelete={userCanDelete}
          customActions={customActions}
          onView={openView}
          onEdit={openEdit}
          onDelete={deleteItem}
          onCustomAction={runCustomAction}
          onPageChange={setPage}
          onSort={changeSort}
        />
      )}

      {isFormOpen && (
        <div className={styles.modalBackdrop} role="presentation">
          <section className={styles.modal} role="dialog" aria-modal="true" aria-label={editingItem ? "Modifier" : "Creer"}>
            <header>
              <div>
                <h2>{editingItem ? "Modifier" : "Nouvel enregistrement"}</h2>
                <p>{config.title}</p>
              </div>
              <button type="button" onClick={closeForm} aria-label="Fermer">x</button>
            </header>
            <ResourceForm
              config={config}
              item={editingItem}
              options={options}
              user={user}
              errors={fieldErrors}
              isSubmitting={isSubmitting}
              onSubmit={submitForm}
              onCancel={closeForm}
            />
          </section>
        </div>
      )}

      {viewingItem && (
        <DetailModal
          config={config}
          item={viewingItem}
          options={options}
          onClose={() => setViewingItem(null)}
        />
      )}
    </div>
  );
}
