import { LayoutGrid, Maximize2, Minimize2, Plus, Search, Table2, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { createResourceApi } from "../../api/resourceApi";
import DataTable from "../../components/common/DataTable";
import ErrorAlert from "../../components/common/ErrorAlert";
import LoadingState from "../../components/common/LoadingState";
import ResourceForm from "../../components/common/ResourceForm";
import TraceabilityLabelPrinter, { BarcodeValue, QrValue } from "../../components/common/TraceabilityLabel";
import { getResourceConfig, resourceConfigs } from "../../constants/resourceConfigs";
import { useAuth } from "../../hooks/useAuth";
import { getApiErrorMessage, normalizeFieldErrors } from "../../utils/apiErrors";
import { normalizePage } from "../../utils/pagination";
import { canWrite } from "../../utils/permissions";
import { buildStatusDateValues } from "../../utils/statusDates";
import styles from "./ResourcePage.module.css";

const perpage = 50;
const AUTO_REFRESH_MS = 10000;
const QUICK_FILTERS = {
  departements: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "true", label: "Actif" },
      { value: "false", label: "Inactif" },
    ],
  },
  directions: {
    label: "Departement",
    field: "id_departement",
    resource: "departements",
  },
  magasins: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "true", label: "Actif" },
      { value: "false", label: "Inactif" },
    ],
  },
  familles: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "true", label: "Actif" },
      { value: "false", label: "Inactif" },
    ],
  },
  categories: {
    label: "Famille",
    field: "id_famille",
    resource: "familles",
  },
  fournisseurs: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "true", label: "Actif" },
      { value: "false", label: "Inactif" },
    ],
  },
  demandes: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "EN_ATTENTE_DEPARTEMENT", label: "En attente" },
      { value: "EN_TRAITEMENT_MAGASIN", label: "Au magasin" },
      { value: "TRAITEE", label: "Traitee" },
      { value: "REJETEE", label: "Rejetee" },
      { value: "ANNULEE", label: "Annulee" },
    ],
  },
  materiels: {
    label: "Situation",
    field: "statut_stock",
    options: [
      { value: "EN_STOCK", label: "En stock" },
      { value: "AFFECTE", label: "Affecte" },
      { value: "HORS_STOCK", label: "Hors stock" },
    ],
  },
  consommables: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "true", label: "Actif" },
      { value: "false", label: "Inactif" },
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
      { value: "AUTRE", label: "Autre" },
    ],
  },
  inventaires: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "EN_COURS", label: "En cours" },
      { value: "TERMINE", label: "Termine" },
      { value: "ANNULE", label: "Annule" },
    ],
  },
  entretiens: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "EN_COURS", label: "En cours" },
      { value: "TERMINE", label: "Termine" },
      { value: "ANNULE", label: "Annule" },
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
  users: {
    label: "Statut",
    field: "is_active",
    options: [
      { value: "true", label: "Actif" },
      { value: "false", label: "Inactif" },
    ],
  },
  roles: {
    label: "Statut",
    field: "statut",
    options: [
      { value: "true", label: "Actif" },
      { value: "false", label: "Inactif" },
    ],
  },
};

function getOptionLabel(resourceKey, item) {
  const config = getResourceConfig(resourceKey);
  if (!config) return String(item.id || item.pk || "");
  const upperCode = (value) => String(value || "").toUpperCase();
  if (resourceKey === "materiels") {
    return [
      upperCode(item.code_materiel),
      [item.marque, item.modele].filter(Boolean).join(" "),
      item.categorie_nom,
      item.etat,
      item.statut_stock,
    ].filter(Boolean).join(" - ");
  }
  if (resourceKey === "departements") {
    return [upperCode(item.code_departement), item.nom_departement].filter(Boolean).join(" - ");
  }
  if (resourceKey === "directions") {
    return [upperCode(item.code_direction), item.nom_direction, item.departement_nom].filter(Boolean).join(" - ");
  }
  if (resourceKey === "magasins") {
    return [upperCode(item.code_magasin), item.nom_magasin, item.direction_nom].filter(Boolean).join(" - ");
  }
  if (resourceKey === "consommables") {
    return [upperCode(item.code_consommable), item.nom_consommable, item.categorie_nom].filter(Boolean).join(" - ");
  }
  const preferred = config.columns.find((column) => column.key.includes("nom_")) || config.columns[0];
  const secondary = config.columns.find((column) => column.key.includes("code_"));
  const label = item[preferred?.key] || item[secondary?.key] || item[config.idField];
  if (!item[preferred?.key] && item[secondary?.key]) return String(label).toUpperCase();
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
  return rows.filter((row) => String(row[quickFilterConfig.field]) === String(quickFilter));
}

function getQuickFilterOptions(quickFilterConfig, options) {
  if (!quickFilterConfig) return [];
  if (quickFilterConfig.resource) return options[quickFilterConfig.resource] || [];
  return quickFilterConfig.options || [];
}

function getServerFilterParams(resourceKey, quickFilterConfig, quickFilter) {
  const serverFilteredResources = new Set([
    "affectations",
    "categories",
    "consommables",
    "demandes",
    "departements",
    "directions",
    "documents",
    "entretiens",
    "familles",
    "fournisseurs",
    "inventaires",
    "magasins",
    "materiels",
    "mouvements",
    "reparations",
    "roles",
    "users",
  ]);
  if (!serverFilteredResources.has(resourceKey) || !quickFilterConfig || quickFilter === "all") return {};
  return { [quickFilterConfig.field]: quickFilter };
}

function getSortableColumns(config) {
  if (config.sortColumns) return config.sortColumns;

  const seen = new Set();
  return [...config.fields, ...config.columns]
    .filter((field) => field.type === "date" || field.name?.startsWith("date_") || field.key?.startsWith("date_"))
    .map((field) => ({
      key: field.name || field.key,
      label: field.label,
      type: "date",
    }))
    .filter((field) => {
      if (!field.key || seen.has(field.key)) return false;
      seen.add(field.key);
      return true;
    });
}

function getStatusControls(config) {
  const statusFieldNames = new Set(["statut", "is_active", "etat"]);
  const columnKeys = new Set(config.columns.map((column) => column.key));

  return config.fields
    .filter((field) => {
      const name = field.name || field.key;
      return (
        name
        && statusFieldNames.has(name)
        && columnKeys.has(name)
        && !field.disabled
        && !field.autoGenerated
        && (field.type === "select" || field.type === "checkbox")
      );
    })
    .map((field) => {
      if (field.type === "checkbox") {
        return {
          field: field.name,
          label: field.label,
          type: "boolean",
          options: [
            { value: true, label: "Actif" },
            { value: false, label: "Inactif" },
          ],
        };
      }
      return {
        field: field.name,
        label: field.label,
        type: "select",
        options: field.options || [],
      };
    })
    .filter((control) => control.options.length > 0);
}

function getOptionResourceKeys(config) {
  return [
    ...new Set(
      config.fields.flatMap((field) => [
        ...(field.optionResources || []),
        typeof field.resource === "string" ? field.resource : null,
      ]).filter(Boolean),
    ),
  ];
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

async function loadOptionsForConfig(config, user) {
  const resources = getOptionResourceKeys(config);
  if (!resources.length) return {};

  const entries = await Promise.all(
    resources.map(async (key) => {
      const optionConfig = resourceConfigs[key];
      try {
        return [
          key,
          (await loadResourceOptions(optionConfig)).map((item) => ({ value: getRowKey(optionConfig, item), label: getOptionLabel(key, item), item })),
        ];
      } catch {
        if (key === "users" && user?.id_users) {
          return [key, [{ value: user.id_users, label: user.nom_users || user.matricule }]];
        }
        return [key, []];
      }
    }),
  );

  return Object.fromEntries(entries);
}

function resolveFieldResource(field, item, options) {
  if (typeof field?.resource === "function") {
    return field.resource({ values: item, options, item, mode: "detail", user: null });
  }
  return field?.resource;
}

function isCodeField(field) {
  return /^code_/.test(field?.name || field?.key || "");
}

function formatDetailValue(value, field, options, item = {}) {
  if (isCodeField(field) && value !== null && value !== undefined && value !== "") return String(value).toUpperCase();
  if (field?.type === "checkbox") return value ? "Oui" : "Non";
  if ((field?.type === "date" || field?.name?.startsWith("date_")) && value) {
    return new Intl.DateTimeFormat("fr-CD").format(new Date(value));
  }
  if (field?.type === "select") {
    const resource = resolveFieldResource(field, item, options);
    const match = (field.options || options[resource] || []).find((option) => {
      const optionValue = typeof option === "string" ? option : option.value;
      return String(optionValue) === String(value);
    });
    if (match) return typeof match === "string" ? match : match.label;
  }
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

function humanizeFieldName(name) {
  return String(name || "")
    .replace(/^id_/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getDetailFields(config) {
  const groupFieldNames = (config.detailGroups || []).flatMap((group) => group.fields);
  const baseFields = config.detailFields || [
    ...config.fields,
    ...config.columns.map((column) => ({ name: column.key, label: column.label, type: column.type })),
    ...groupFieldNames.map((name) => ({ name, label: humanizeFieldName(name) })),
  ];

  const fieldsByName = new Map();
  baseFields.forEach((field) => {
    const name = field.name || field.key;
    if (!name) return;
    fieldsByName.set(name, { ...fieldsByName.get(name), ...field, name });
  });
  return [...fieldsByName.values()];
}

function getDetailTitle(config, item) {
  const titleField = config.detailTitleField || config.columns[0]?.key || config.idField;
  return item[titleField] || item[config.idField] || item.__rowKey || config.title;
}

function renderArrayValue(value) {
  if (!value.length) return <span className={styles.emptyDetail}>Aucune donnee</span>;
  const objectRows = value.filter((entry) => entry && typeof entry === "object" && !Array.isArray(entry));
  if (objectRows.length === value.length) {
    const keys = [...new Set(objectRows.flatMap((entry) => Object.keys(entry)))];
    return (
      <div className={styles.detailMiniTable}>
        <div className={styles.detailMiniHead}>
          {keys.map((key) => <span key={key}>{humanizeFieldName(key)}</span>)}
        </div>
        {objectRows.map((entry, index) => (
          <div className={styles.detailMiniRow} key={`${index}-${Object.values(entry).join("-")}`}>
            {keys.map((key) => <span key={key}>{formatDetailValue(entry[key], {}, {})}</span>)}
          </div>
        ))}
      </div>
    );
  }
  return (
    <div className={styles.detailList}>
      {value.map((entry, index) => <span key={`${index}-${entry}`}>{String(entry)}</span>)}
    </div>
  );
}

function DetailValue({ value, field, options, item }) {
  if (Array.isArray(value)) return renderArrayValue(value);
  if (field?.name === "code_barre") return <BarcodeValue value={value} />;
  if (field?.name === "qr_code") return <QrValue value={value} />;
  return <span>{formatDetailValue(value, field, options, item)}</span>;
}

function DetailModal({ config, item, options, customActions, onCustomAction, onClose }) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const fields = getDetailFields(config);
  const groups = config.detailGroups || [{ title: "Informations", fields: fields.map((field) => field.name), tone: "blue" }];
  const visibleActions = customActions.filter((action) => !action.visibleWhen || action.visibleWhen(item));
  const detailActionClassName = (action) => [
    styles.detailActionButton,
    action.variant ? styles[`action${action.variant}`] : "",
  ].filter(Boolean).join(" ");

  return (
    <div className={`${styles.modalBackdrop} ${styles.detailBackdrop}`} role="presentation">
      <section
        className={`${styles.modal} ${styles.detailModal} ${isFullscreen ? styles.detailModalFull : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label="Detail"
      >
        <header>
          <div>
            <h2>Detail</h2>
            <p>{config.title}</p>
          </div>
          <div className={styles.detailHeaderActions}>
            <button type="button" onClick={() => setIsFullscreen((current) => !current)} aria-label={isFullscreen ? "Reduire" : "Voir en plein ecran"}>
              {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </button>
            <button type="button" onClick={onClose} aria-label="Fermer"><X size={16} /></button>
          </div>
        </header>
        <div className={styles.detailSummary}>
          <span>{config.title}</span>
          <strong>{getDetailTitle(config, item)}</strong>
          <small>{config.idField}: {item[config.idField] ?? item.__rowKey}</small>
        </div>
        <div className={styles.detailSections}>
          {groups.map((group) => {
            const groupFields = group.fields
              .map((fieldName) => fields.find((field) => field.name === fieldName || field.key === fieldName))
              .filter(Boolean);
            if (!groupFields.length) return null;
            return (
              <section className={`${styles.detailGroup} ${styles[group.tone || "blue"]}`} key={group.title}>
                <h3>{group.title}</h3>
                <div className={styles.detailGrid}>
                  {groupFields.map((field) => (
                    <div className={`${styles.detailItem} ${Array.isArray(item[field.name]) ? styles.detailItemWide : ""}`} key={field.name}>
                      <span>{field.label}</span>
                      <div className={styles.detailValue}>
                        <DetailValue value={item[field.name]} field={field} options={options} item={item} />
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
        {config.traceabilityLabel && (
          <TraceabilityLabelPrinter item={item} config={config} />
        )}
        {visibleActions.length > 0 && (
          <div className={styles.detailActions}>
            {visibleActions.map((action) => (
              <button type="button" className={detailActionClassName(action)} onClick={() => onCustomAction(action, item)} key={action.label}>
                {action.label}
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function ConfirmDialog({ title, message, confirmLabel = "Confirmer", variant = "danger", onConfirm, onCancel }) {
  return (
    <div className={styles.modalBackdrop} role="presentation">
      <section className={`${styles.modal} ${styles.dialogModal}`} role="dialog" aria-modal="true" aria-label={title}>
        <header>
          <div>
            <h2>{title}</h2>
            <p>{message}</p>
          </div>
          <button type="button" onClick={onCancel} aria-label="Fermer"><X size={16} /></button>
        </header>
        <div className={styles.dialogActions}>
          <button type="button" className={styles.dialogSecondary} onClick={onCancel}>Annuler</button>
          <button type="button" className={`${styles.dialogPrimary} ${styles[variant]}`} onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </section>
    </div>
  );
}

function PromptDialog({ title, label, required = false, confirmLabel = "Valider", onConfirm, onCancel }) {
  const [value, setValue] = useState("");
  const [error, setError] = useState("");

  const submit = (event) => {
    event.preventDefault();
    const nextValue = value.trim();
    if (required && !nextValue) {
      setError("Ce champ est obligatoire.");
      return;
    }
    onConfirm(nextValue);
  };

  return (
    <div className={styles.modalBackdrop} role="presentation">
      <section className={`${styles.modal} ${styles.dialogModal}`} role="dialog" aria-modal="true" aria-label={title}>
        <header>
          <div>
            <h2>{title}</h2>
            <p>{label}</p>
          </div>
          <button type="button" onClick={onCancel} aria-label="Fermer"><X size={16} /></button>
        </header>
        <form className={styles.promptForm} onSubmit={submit}>
          <label>
            <span>{label}{required ? " *" : ""}</span>
            <textarea value={value} onChange={(event) => setValue(event.target.value)} rows={4} autoFocus />
          </label>
          {error && <small>{error}</small>}
          <div className={styles.dialogActions}>
            <button type="button" className={styles.dialogSecondary} onClick={onCancel}>Annuler</button>
            <button type="submit" className={styles.dialogPrimary}>{confirmLabel}</button>
          </div>
        </form>
      </section>
    </div>
  );
}

export default function ResourcePage({ resourceKey }) {
  const config = getResourceConfig(resourceKey);
  const api = useMemo(() => createResourceApi(config.endpoint), [config.endpoint]);
  const [searchParams, setSearchParams] = useSearchParams();
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [data, setData] = useState({ count: 0, page: 1, totalPages: 1, results: [] });
  const [options, setOptions] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [editingItem, setEditingItem] = useState(null);
  const [viewingItem, setViewingItem] = useState(null);
  const [actionForm, setActionForm] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState(null);
  const [promptDialog, setPromptDialog] = useState(null);
  const [viewMode, setViewMode] = useState("table");
  const [sortKey, setSortKey] = useState("");
  const [sortDirection, setSortDirection] = useState("asc");
  const [quickFilter, setQuickFilter] = useState("all");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const createRoles = config.createRoles ?? config.writeRoles;
  const updateRoles = config.updateRoles ?? config.writeRoles;
  const deleteRoles = config.deleteRoles ?? config.writeRoles;
  const userCanCreate = canWrite(user, createRoles) && (!config.createWhen || config.createWhen(user));
  const userCanUpdate = canWrite(user, updateRoles) && (!config.updateWhen || config.updateWhen(user));
  const userCanDelete = canWrite(user, deleteRoles) && (!config.deleteWhen || config.deleteWhen(user));
  const customActions = (config.actions || []).filter(
    (action) => canWrite(user, action.roles) && (!action.canUse || action.canUse(user)),
  );
  const quickFilterConfig = QUICK_FILTERS[resourceKey] || null;
  const quickFilterOptions = getQuickFilterOptions(quickFilterConfig, options);
  const sortableColumns = useMemo(() => getSortableColumns(config), [config]);
  const statusControls = useMemo(() => getStatusControls(config), [config]);

  const loadData = useCallback(async ({ silent = false } = {}) => {
    if (!silent) {
      setIsLoading(true);
      setError("");
    }
    try {
      const filterParams = getServerFilterParams(resourceKey, quickFilterConfig, quickFilter);
      const response = await api.list({ page, perpage, search: search || undefined, ...filterParams });
      setData(normalizePage(response));
    } catch (loadError) {
      if (!silent) setError(getApiErrorMessage(loadError));
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, [api, page, quickFilter, quickFilterConfig, resourceKey, search]);

  const refreshOptions = useCallback(async () => {
    setOptions(await loadOptionsForConfig(config, user));
  }, [config, user]);

  const ensureOptionsForConfig = useCallback(async (targetConfig) => {
    const resources = getOptionResourceKeys(targetConfig);
    if (!resources.length) return;

    const missingResources = resources.filter((key) => !options[key]);
    if (!missingResources.length) return;

    const entries = await Promise.all(
      missingResources.map(async (key) => {
        const optionConfig = resourceConfigs[key];
        try {
          return [
            key,
            (await loadResourceOptions(optionConfig)).map((item) => ({ value: getRowKey(optionConfig, item), label: getOptionLabel(key, item), item })),
          ];
        } catch {
          return [key, []];
        }
      }),
    );
    setOptions((current) => ({ ...current, ...Object.fromEntries(entries) }));
  }, [options]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const refresh = () => {
      if (document.visibilityState !== "visible" || isFormOpen || actionForm) return;
      loadData({ silent: true });
      refreshOptions();
    };

    const intervalId = window.setInterval(refresh, AUTO_REFRESH_MS);
    window.addEventListener("focus", refresh);
    document.addEventListener("visibilitychange", refresh);

    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener("focus", refresh);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [actionForm, isFormOpen, loadData, refreshOptions]);

  useEffect(() => {
    setViewMode("table");
    setSortKey(sortableColumns[0]?.key || "");
    setSortDirection("asc");
    setQuickFilter("all");
  }, [resourceKey, sortableColumns]);

  useEffect(() => {
    let isMounted = true;
    loadOptionsForConfig(config, user)
      .then((nextOptions) => {
        if (isMounted) setOptions(nextOptions);
      })
      .catch(() => {
        if (isMounted) setOptions({});
      });

    return () => {
      isMounted = false;
    };
  }, [config, user]);

  const rows = useMemo(
    () => data.results.map((item) => ({ ...item, __rowKey: getRowKey(config, item) })),
    [config, data.results],
  );
  const filteredRows = useMemo(
    () => filterRows(rows, quickFilterConfig, quickFilter),
    [quickFilter, quickFilterConfig, rows],
  );
  const sortedRows = useMemo(
    () => sortRows(filteredRows, sortableColumns, sortKey, sortDirection),
    [filteredRows, sortDirection, sortKey, sortableColumns],
  );
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

  const openCreate = useCallback(() => {
    setEditingItem(null);
    setFieldErrors({});
    setError("");
    setIsFormOpen(true);
  }, []);

  useEffect(() => {
    if (searchParams.get("create") !== "1" || !userCanCreate) return;
    openCreate();
    setSearchParams({}, { replace: true });
  }, [openCreate, searchParams, setSearchParams, userCanCreate]);

  const openEdit = (item) => {
    setEditingItem(item);
    setFieldErrors({});
    setError("");
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

  const closeActionForm = () => {
    setActionForm(null);
    setFieldErrors({});
  };

  const submitForm = async (payload) => {
    setIsSubmitting(true);
    setFieldErrors({});
    setError("");
    setFeedback("");
    try {
      if (editingItem) {
        await api.update(getRowKey(config, editingItem), payload);
        setFeedback(`${config.title} modifie avec succes.`);
      } else {
        await api.create(payload);
        const createdQuantity = resourceKey === "materiels" ? Number(payload.quantite_creation || 1) : 1;
        setFeedback(
          createdQuantity > 1
            ? `${createdQuantity} materiels crees avec succes.`
            : `${config.title} cree avec succes.`,
        );
      }
      closeForm();
      loadData();
      refreshOptions();
    } catch (submitError) {
      setFieldErrors(normalizeFieldErrors(submitError));
      setError(getApiErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  };

  const performDelete = async (item) => {
    try {
      setError("");
      setFeedback("");
      await api.remove(getRowKey(config, item), { cascade: true });
      setFeedback(`${config.title} et elements lies supprimes avec succes.`);
      loadData();
      refreshOptions();
    } catch (deleteError) {
      setError(getApiErrorMessage(deleteError));
    }
  };

  const performBulkDelete = async (items) => {
    try {
      setError("");
      setFeedback("");
      for (const item of items) {
        await api.remove(getRowKey(config, item), { cascade: true });
      }
      setViewingItem(null);
      setFeedback(`${items.length} enregistrement(s) supprime(s) avec succes.`);
      loadData();
      refreshOptions();
    } catch (deleteError) {
      setError(getApiErrorMessage(deleteError));
    }
  };

  const deleteItem = (item) => {
    setConfirmDialog({
      title: "Confirmer la suppression",
      message: "Cette suppression est irreversible et les elements lies seront aussi supprimes.",
      confirmLabel: "Supprimer",
      onConfirm: () => {
        setConfirmDialog(null);
        performDelete(item);
      },
    });
  };

  const deleteItems = (items) => {
    if (!items.length) return;
    setConfirmDialog({
      title: "Confirmer la suppression",
      message: `${items.length} enregistrement(s) seront supprime(s). Les elements lies seront aussi supprimes.`,
      confirmLabel: "Supprimer",
      onConfirm: () => {
        setConfirmDialog(null);
        performBulkDelete(items);
      },
    });
  };

  const executeCustomAction = async (action, item, payload = {}) => {
    try {
      setError("");
      setFeedback("");
      await api.action(getRowKey(config, item), action.endpoint, payload);
      setFeedback("Action effectuee avec succes.");
      setViewingItem(null);
      loadData();
      refreshOptions();
    } catch (actionError) {
      setError(getApiErrorMessage(actionError));
    }
  };

  const changeInlineStatus = async (item, fieldName, value) => {
    try {
      setError("");
      setFeedback("");
      const payload = {
        [fieldName]: value,
        ...buildStatusDateValues({
          fields: config.fields,
          currentValues: item,
          fieldName,
          value,
        }),
      };
      await api.update(getRowKey(config, item), payload);
      setViewingItem(null);
      setFeedback("Statut mis a jour avec succes.");
      loadData();
      refreshOptions();
    } catch (statusError) {
      setError(getApiErrorMessage(statusError));
    }
  };

  const runCustomAction = async (action, item) => {
    if (action.formResource) {
      const targetConfig = resourceConfigs[action.formResource];
      const initialValues = action.getInitialValues ? action.getInitialValues(item) : {};
      setFieldErrors({});
      setError("");
      await ensureOptionsForConfig(targetConfig);
      setActionForm({ action, config: targetConfig, initialValues });
      return;
    }

    if (action.prompt) {
      setPromptDialog({
        ...action.prompt,
        confirmLabel: action.label,
        onConfirm: (value) => {
          setPromptDialog(null);
          executeCustomAction(action, item, { [action.prompt.field]: value });
        },
      });
      return;
    }

    const payload = action.getPayload ? action.getPayload(item) : {};
    if (payload === null) return;

    executeCustomAction(action, item, payload);
  };

  const submitActionForm = async (payload) => {
    const actionConfig = actionForm.config;
    const actionApi = createResourceApi(actionConfig.endpoint);
    setIsSubmitting(true);
    setFieldErrors({});
    setError("");
    setFeedback("");
    try {
      await actionApi.create({ ...actionForm.initialValues, ...payload });
      setFeedback(`${actionConfig.title} cree avec succes.`);
      closeActionForm();
      setViewingItem(null);
      loadData();
      refreshOptions();
    } catch (submitError) {
      setFieldErrors(normalizeFieldErrors(submitError));
      setError(getApiErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  };

  const addOption = (resource, option) => {
    setOptions((current) => ({
      ...current,
      [resource]: [...(current[resource] || []), option],
    }));
  };

  return (
    <div className={styles.page}>
      <section className={styles.heading}>
        <div>
          <p className={styles.eyebrow}>Registre</p>
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
              onClick={() => {
                setPage(1);
                setQuickFilter("all");
              }}
            >
              Tous
            </button>
            {quickFilterOptions.map((option) => (
              <button
                type="button"
                className={quickFilter === option.value ? styles.activeFilter : ""}
                onClick={() => {
                  setPage(1);
                  setQuickFilter(option.value);
                }}
                key={option.value}
              >
                {option.label}
              </button>
            ))}
          </div>
        </section>
      )}

      {feedback && <div className={styles.feedback} role="status">{feedback}</div>}
      {!isFormOpen && !actionForm && <ErrorAlert message={error} onRetry={loadData} />}

      {isLoading ? (
        <LoadingState />
      ) : (
        <DataTable
          columns={config.columns}
          fields={config.fields}
          options={options}
          rows={sortedRows}
          page={data.page}
          totalPages={data.totalPages}
          count={data.count}
          viewMode={viewMode}
          sortKey={sortKey}
          sortDirection={sortDirection}
          canView
          canEdit={userCanUpdate}
          canDelete={userCanDelete}
          customActions={customActions}
          onView={openView}
          onEdit={openEdit}
          onDelete={deleteItem}
          onBulkDelete={deleteItems}
          onCustomAction={runCustomAction}
          onStatusChange={changeInlineStatus}
          onPageChange={setPage}
          onSort={changeSort}
          sortableColumns={sortableColumns}
          statusControls={statusControls}
        />
      )}

      {isFormOpen && (
        <div className={styles.modalBackdrop} role="presentation">
          <section className={`${styles.modal} ${config.formSteps ? styles.wizardModal : ""}`} role="dialog" aria-modal="true" aria-label={editingItem ? "Modifier" : "Creer"}>
            <header>
              <div>
                <h2>{editingItem ? "Modifier" : "Nouvel enregistrement"}</h2>
                <p>{config.title}</p>
              </div>
              <button type="button" onClick={closeForm} aria-label="Fermer"><X size={16} /></button>
            </header>
            <ErrorAlert message={error} />
            <ResourceForm
              config={config}
              item={editingItem}
              mode={editingItem ? "edit" : "create"}
              options={options}
              user={user}
              errors={fieldErrors}
              isSubmitting={isSubmitting}
              onSubmit={submitForm}
              onCancel={closeForm}
              onOptionCreated={addOption}
            />
          </section>
        </div>
      )}

      {viewingItem && (
        <DetailModal
          config={config}
          item={viewingItem}
          options={options}
          customActions={customActions}
          onCustomAction={runCustomAction}
          onClose={() => setViewingItem(null)}
        />
      )}

      {actionForm && (
        <div className={styles.modalBackdrop} role="presentation">
          <section className={styles.modal} role="dialog" aria-modal="true" aria-label={actionForm.action.label}>
            <header>
              <div>
                <h2>{actionForm.action.label}</h2>
                <p>{actionForm.config.title}</p>
              </div>
              <button type="button" onClick={closeActionForm} aria-label="Fermer"><X size={16} /></button>
            </header>
            <ErrorAlert message={error} />
            <ResourceForm
              config={actionForm.config}
              item={actionForm.initialValues}
              mode="create"
              options={options}
              user={user}
              errors={fieldErrors}
              isSubmitting={isSubmitting}
              onSubmit={submitActionForm}
              onCancel={closeActionForm}
              onOptionCreated={addOption}
            />
          </section>
        </div>
      )}

      {confirmDialog && (
        <ConfirmDialog
          title={confirmDialog.title}
          message={confirmDialog.message}
          confirmLabel={confirmDialog.confirmLabel}
          onConfirm={confirmDialog.onConfirm}
          onCancel={() => setConfirmDialog(null)}
        />
      )}

      {promptDialog && (
        <PromptDialog
          title={promptDialog.title}
          label={promptDialog.label}
          required={promptDialog.required}
          confirmLabel={promptDialog.confirmLabel}
          onConfirm={promptDialog.onConfirm}
          onCancel={() => setPromptDialog(null)}
        />
      )}
    </div>
  );
}
