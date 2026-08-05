import { ROLES } from "../utils/permissions";

export const adminOnlyRoles = [ROLES.ADMIN];
export const businessRoles = [ROLES.ADMIN, ROLES.GESTION, ROLES.MAGASIN];
export const gestionRoles = [ROLES.ADMIN, ROLES.GESTION];
export const magasinRoles = [ROLES.ADMIN, ROLES.MAGASIN];
export const adminOnlyWriteRoles = adminOnlyRoles;
export const businessWriteRoles = gestionRoles;
export const materialActionRoles = adminOnlyRoles;
export const operationWriteRoles = gestionRoles;

function selectedOptionLabel(options, resource, value) {
  if (!value) return "";
  const option = (options[resource] || []).find((entry) => String(entry.value) === String(value));
  return String(option?.label || "").toUpperCase();
}

function selectedRoleIsAdmin({ values, options }) {
  const label = selectedOptionLabel(options, "roles", values.id_role);
  return label.includes("ADMIN") || label.includes("ADMINISTRATEUR");
}

function selectedRoleIsFixedGeneral({ values, options }) {
  const label = selectedOptionLabel(options, "roles", values.id_role);
  return selectedRoleIsAdmin({ values, options }) || label.includes("MAGASIN");
}

function userNeedsManualMatricule({ values }) {
  return !["DEPARTEMENT", "DIRECTION"].includes(values.scope_type);
}

function currentUserIsNotAdmin({ user }) {
  return user?.role !== ROLES.ADMIN;
}

function isDirectionRequester(user) {
  return user?.role === ROLES.GESTION && user?.scope_type === "DIRECTION";
}

function isDepartmentValidator(user) {
  return user?.role === ROLES.GESTION && user?.scope_type === "DEPARTEMENT";
}

function isGeneralStorekeeper(user) {
  return user?.role === ROLES.MAGASIN && user?.scope_type === "GENERAL";
}

function isInventoryOperator(user) {
  return user?.role === ROLES.ADMIN || isGeneralStorekeeper(user);
}

function isGestionCreate({ user, mode }) {
  return mode === "create" && user?.role === ROLES.GESTION;
}

function isNotGestionCreate(context) {
  return !isGestionCreate(context);
}

function fieldHasValue(fieldName) {
  return ({ values }) => values[fieldName] !== undefined && values[fieldName] !== null && values[fieldName] !== "";
}

function fieldMissing(fieldName) {
  return (context) => !fieldHasValue(fieldName)(context);
}

function fieldValueIs(fieldName, expectedValue) {
  return ({ values }) => values[fieldName] === expectedValue;
}

function fieldValueIsNot(fieldName, expectedValue) {
  return ({ values }) => values[fieldName] !== expectedValue;
}

function anyRule(...rules) {
  return (context) => rules.some((rule) => rule(context));
}

function optionBelongsTo(fieldName) {
  return ({ option, values, user }) => {
    const fallbackValue = fieldName === "id_direction_demandeuse"
      ? user?.id_direction
      : user?.[fieldName];
    const selectedValue = values[fieldName] || fallbackValue;
    if (!selectedValue) return true;
    const optionValue = fieldName === "id_direction_demandeuse"
      ? option.item?.id_direction
      : option.item?.[fieldName];
    return String(optionValue) === String(selectedValue);
  };
}

function categoryBelongsToSelectedFamily({ option, values, mode }) {
  if (mode !== "create") return true;
  if (!values.id_famille) return false;
  return String(option.item?.id_famille) === String(values.id_famille);
}

function materialBelongsToSelectedCategory({ option, values, mode }) {
  if (mode !== "create") return true;
  if (!values.id_categorie) return false;
  return String(option.item?.id_categorie) === String(values.id_categorie);
}

function materialIsAvailableForAffectation({ option }) {
  return option.item?.statut_stock === "EN_STOCK" && !["EN_PANNE", "EN_REPARATION", "HORS_SERVICE"].includes(option.item?.etat);
}

function needsSelectedFamily({ values, mode }) {
  return mode === "create" && !values.id_famille;
}

function needsSelectedCategory({ values, mode }) {
  return mode === "create" && !values.id_categorie;
}

function needsSelectedDepartment({ values, mode }) {
  return mode === "create" && !values.id_departement;
}

function isAgentAffectation({ values }) {
  return values.entite_type === "AGENT";
}

function isNotAgentAffectation({ values }) {
  return values.entite_type !== "AGENT";
}

function directionBelongsToAgentDepartment({ option, values }) {
  if (!values.agent_id_departement) return false;
  return String(option.item?.id_departement) === String(values.agent_id_departement);
}

function needsEntiteType({ values }) {
  return !values.entite_type;
}

function needsAgentDepartment({ values }) {
  return values.entite_type === "AGENT" && !values.agent_id_departement;
}

function needsMovementType({ values }) {
  return !values.type_mouvement;
}

function needsMovementArticle({ values }) {
  return !values.id_materiel && !values.id_consommable;
}

function movementNeedsSource({ values }) {
  return ["SORTIE", "TRANSFERT"].includes(values.type_mouvement);
}

function movementNeedsDestination({ values }) {
  return ["ENTREE", "TRANSFERT"].includes(values.type_mouvement);
}

function isConsumptionDirection({ values }) {
  return values.destination_type === "DIRECTION";
}

function needsConsumptionDepartment({ values }) {
  return !values.id_departement;
}

function selectedOption(options, resource, value) {
  return (options[resource] || []).find((entry) => String(entry.value) === String(value));
}

function selectedConsumableStock({ values, options }) {
  const option = selectedOption(options, "consommables", values.id_consommable);
  const stock = Number(option?.item?.quantite_stock);
  return Number.isFinite(stock) ? stock : undefined;
}

function selectedArticleMagasinId({ values, options }) {
  if (values.id_materiel) return selectedOption(options, "materiels", values.id_materiel)?.item?.id_magasin;
  if (values.id_consommable) return selectedOption(options, "consommables", values.id_consommable)?.item?.id_magasin;
  return "";
}

function magasinMatchesSelectedArticle({ option, values, options }) {
  const magasinId = selectedArticleMagasinId({ values, options });
  if (!magasinId) return true;
  return String(option.value) === String(magasinId);
}

function materialCanMove({ option, values }) {
  if (!["SORTIE", "TRANSFERT"].includes(values.type_mouvement)) return true;
  return Boolean(option.item?.id_magasin) && option.item?.statut_stock !== "AFFECTE" && option.item?.etat !== "HORS_SERVICE";
}

function consommableCanLeaveStock({ option, values }) {
  if (!["SORTIE", "TRANSFERT"].includes(values.type_mouvement)) return true;
  return Boolean(option.item?.id_magasin) && Number(option.item?.quantite_stock || 0) > 0;
}

function visibleOnEdit({ mode }) {
  return mode === "edit";
}

function prefilledByAction(fieldName) {
  return ({ item, mode }) => mode === "create" && item?.[fieldName] !== undefined && item?.[fieldName] !== null && item?.[fieldName] !== "";
}

function resourceForEntiteType({ values }) {
  const resources = {
    DEPARTEMENT: "departements",
    DIRECTION: "directions",
    MAGASIN: "magasins",
  };
  return resources[values.entite_type] || null;
}

export const resourceConfigs = {
  departements: {
    title: "Departements",
    description: "Structure de premier niveau de l'organisation.",
    endpoint: "organisation/departements/",
    idField: "id_departement",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "code_departement", label: "Code" },
      { key: "nom_departement", label: "Nom" },
      { key: "abreviation", label: "Abreviation" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_departement", label: "Code", required: true },
      { name: "nom_departement", label: "Nom", required: true },
      { name: "abreviation", label: "Abreviation" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formSteps: [
      { title: "Code", tone: "blue", fields: ["code_departement", "abreviation"] },
      { title: "Departement", tone: "green", fields: ["nom_departement", "statut"] },
    ],
  },
  directions: {
    title: "Directions",
    description: "Directions rattachees aux departements.",
    endpoint: "organisation/directions/",
    idField: "id_direction",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "code_direction", label: "Code" },
      { key: "nom_direction", label: "Nom" },
      { key: "departement_nom", label: "Departement" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_direction", label: "Code", required: true },
      { name: "nom_direction", label: "Nom", required: true },
      { name: "abreviation", label: "Abreviation" },
      { name: "id_departement", label: "Departement", type: "recordPicker", required: true, resource: "departements", searchPlaceholder: "Rechercher un departement..." },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formSteps: [
      { title: "Departement", tone: "blue", fields: ["id_departement"] },
      { title: "Direction", tone: "green", fields: ["code_direction", "nom_direction", "abreviation", "statut"] },
    ],
  },
  magasins: {
    title: "Magasins",
    description: "Magasins et emplacements de stockage.",
    endpoint: "stock/magasins/",
    idField: "id_magasin",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    sortColumns: [
      { key: "date_creation", label: "Date creation", type: "date" },
    ],
    columns: [
      { key: "code_magasin", label: "Code" },
      { key: "nom_magasin", label: "Nom" },
      { key: "direction_nom", label: "Direction" },
      { key: "departement_nom", label: "Departement" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_magasin", label: "Code", required: true },
      { name: "nom_magasin", label: "Nom", required: true },
      { name: "id_departement", label: "Departement", type: "recordPicker", resource: "departements", virtual: true, createOnly: true, clears: ["id_direction"], searchPlaceholder: "Rechercher un departement..." },
      { name: "id_direction", label: "Direction", type: "recordPicker", resource: "directions", required: true, filterOptions: optionBelongsTo("id_departement"), disabledWhen: needsSelectedDepartment, searchPlaceholder: "Rechercher une direction..." },
      { name: "description_localisation", label: "Localisation", type: "textarea" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formSteps: [
      { title: "Departement", tone: "blue", fields: ["id_departement"] },
      { title: "Direction", tone: "green", fields: ["id_direction"] },
      { title: "Magasin", tone: "orange", fields: ["code_magasin", "nom_magasin", "description_localisation", "statut"] },
    ],
  },
  familles: {
    title: "Familles",
    description: "Familles d'inventaire.",
    endpoint: "catalogue/familles/",
    idField: "id_famille",
    visibleRoles: businessRoles,
    writeRoles: adminOnlyWriteRoles,
    sortColumns: [
      { key: "date_creation", label: "Date creation", type: "date" },
    ],
    columns: [
      { key: "code_famille", label: "Code" },
      { key: "nom_famille", label: "Nom" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_famille", label: "Code", autoGenerated: true, disabled: true },
      { name: "nom_famille", label: "Nom", required: true },
      { name: "description", label: "Description", type: "textarea" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formSteps: [
      { title: "Famille", tone: "blue", fields: ["nom_famille", "statut"] },
      { title: "Description", tone: "slate", fields: ["description"] },
    ],
  },
  categories: {
    title: "Categories",
    description: "Categories rattachees aux familles.",
    endpoint: "catalogue/categories/",
    idField: "id_categorie",
    visibleRoles: businessRoles,
    writeRoles: adminOnlyWriteRoles,
    sortColumns: [
      { key: "date_creation", label: "Date creation", type: "date" },
    ],
    columns: [
      { key: "code_categorie", label: "Code" },
      { key: "nom_categorie", label: "Nom" },
      { key: "famille_nom", label: "Famille", highlight: "family" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_categorie", label: "Code", autoGenerated: true, disabled: true },
      { name: "nom_categorie", label: "Nom", required: true },
      { name: "id_famille", label: "Famille", type: "recordPicker", required: true, resource: "familles", searchPlaceholder: "Rechercher une famille..." },
      { name: "description", label: "Description", type: "textarea" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formSteps: [
      { title: "Famille", tone: "blue", fields: ["id_famille"] },
      { title: "Categorie", tone: "green", fields: ["nom_categorie", "statut"] },
      { title: "Description", tone: "slate", fields: ["description"] },
    ],
  },
  unites: {
    title: "Unites systeme",
    description: "Referentiel systeme utilise dans les consommables.",
    endpoint: "catalogue/unites/",
    idField: "id_unite",
    visibleRoles: businessRoles,
    writeRoles: [],
    createRoles: [],
    updateRoles: [],
    deleteRoles: [],
    columns: [
      { key: "code_unite", label: "Code" },
      { key: "nom_unite", label: "Nom" },
      { key: "symbole", label: "Symbole" },
    ],
    fields: [
      { name: "code_unite", label: "Code", required: true },
      { name: "nom_unite", label: "Nom", required: true },
      { name: "symbole", label: "Symbole", required: true },
    ],
  },
  fournisseurs: {
    title: "Fournisseurs",
    description: "Fournisseurs lies aux materiels.",
    endpoint: "catalogue/fournisseurs/",
    idField: "id_fournisseur",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    sortColumns: [
      { key: "date_creation", label: "Date creation", type: "date" },
    ],
    columns: [
      { key: "nom_fournisseur", label: "Nom" },
      { key: "email", label: "Email" },
      { key: "rccm", label: "RCCM" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "nom_fournisseur", label: "Nom", required: true },
      { name: "email", label: "Email", type: "email" },
      { name: "adresse", label: "Adresse" },
      { name: "rccm", label: "RCCM" },
      { name: "nif", label: "NIF" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formSteps: [
      { title: "Identite", tone: "blue", fields: ["nom_fournisseur", "statut"] },
      { title: "Contact", tone: "green", fields: ["email", "adresse"] },
      { title: "Fiscal", tone: "orange", fields: ["rccm", "nif"] },
    ],
    detailGroups: [
      { title: "Identite", tone: "orange", fields: ["nom_fournisseur", "email", "adresse", "rccm", "nif", "statut"] },
      { title: "Materiels fournis", tone: "blue", fields: ["materiels_fournis"] },
    ],
  },
  materiels: {
    title: "Materiels",
    description: "Materiels suivis individuellement.",
    endpoint: "stock/materiels/",
    idField: "id_materiel",
    visibleRoles: businessRoles,
    writeRoles: adminOnlyWriteRoles,
    sortColumns: [
      { key: "date_achat", label: "Date d'achat", type: "date" },
      { key: "date_enregistrement", label: "Date enregistrement", type: "date" },
      { key: "garantie_fin", label: "Fin garantie", type: "date" },
    ],
    columns: [
      { key: "code_materiel", label: "Code" },
      { key: "marque", label: "Marque" },
      { key: "modele", label: "Modele" },
      { key: "categorie_nom", label: "Categorie" },
      { key: "etat", label: "Etat physique" },
      { key: "statut_stock", label: "Situation" },
      { key: "magasin_nom", label: "Magasin" },
    ],
    fields: [
      { name: "code_materiel", label: "Code", autoGenerated: true, disabled: true },
      { name: "id_famille", label: "Famille", type: "recordPicker", required: true, resource: "familles", virtual: true, createOnly: true, clears: ["id_categorie"], searchPlaceholder: "Rechercher une famille..." },
      { name: "id_categorie", label: "Categorie", type: "recordPicker", required: true, resource: "categories", filterOptions: categoryBelongsToSelectedFamily, disabledWhen: needsSelectedFamily, searchPlaceholder: "Rechercher une categorie..." },
      { name: "id_magasin", label: "Magasin", type: "recordPicker", resource: "magasins", searchPlaceholder: "Rechercher un magasin..." },
      {
        name: "id_fournisseur",
        label: "Fournisseur",
        type: "recordPicker",
        resource: "fournisseurs",
        noneLabel: "Aucun fournisseur",
        searchPlaceholder: "Rechercher un fournisseur...",
        quickCreate: {
          label: "Ajouter un fournisseur",
          navigateTo: "/catalogue/fournisseurs?create=1",
          resourceKey: "fournisseurs",
          endpoint: "catalogue/fournisseurs/",
          idField: "id_fournisseur",
          labelField: "nom_fournisseur",
          nameField: "nom_fournisseur",
          defaults: { statut: true },
        },
      },
      { name: "numero_serie", label: "Numero de serie", autoGenerated: true, disabled: true },
      { name: "marque", label: "Marque", required: true },
      { name: "modele", label: "Modele" },
      { name: "date_achat", label: "Date d'achat", type: "date", required: true },
      { name: "prix_achat", label: "Prix total d'achat", type: "number", required: true, defaultValue: 0 },
      { name: "quantite_creation", label: "Quantite a creer", type: "number", createOnly: true, defaultValue: 1, min: 1, max: 100 },
      { name: "devise", label: "Devise", defaultValue: "USD" },
      { name: "duree_garantie_mois", label: "Garantie (mois)", type: "number", defaultValue: 0 },
      { name: "garantie_fin", label: "Fin garantie", type: "date" },
      { name: "etat", label: "Etat physique", type: "select", required: true, options: ["NEUF", "BON", "EN_PANNE", "EN_REPARATION", "HORS_SERVICE"], createOptions: ["NEUF", "BON"], defaultValue: "NEUF" },
      { name: "statut_stock", label: "Situation", type: "select", options: ["EN_STOCK", "AFFECTE", "HORS_STOCK"], disabled: true },
      { name: "code_barre", label: "Code-barres", autoGenerated: true, disabled: true },
      { name: "qr_code", label: "QR code", autoGenerated: true, disabled: true },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Identification", tone: "blue", fields: ["code_materiel", "numero_serie", "marque", "modele", "id_famille", "id_categorie", "id_fournisseur"] },
      { title: "Stock et etat", tone: "green", fields: ["id_magasin", "statut_stock", "etat", "code_barre", "qr_code"] },
      { title: "Achat et garantie", tone: "orange", fields: ["date_achat", "prix_achat", "quantite_creation", "devise", "duree_garantie_mois", "garantie_fin"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Famille", tone: "blue", fields: ["id_famille", "id_categorie"] },
      { title: "Materiel", tone: "green", fields: ["marque", "modele", "id_fournisseur"] },
      { title: "Achat", tone: "orange", fields: ["date_achat", "prix_achat", "quantite_creation", "devise"] },
      { title: "Stock", tone: "slate", fields: ["id_magasin", "statut_stock", "etat", "duree_garantie_mois", "garantie_fin"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    detailGroups: [
      { title: "Identification", tone: "blue", fields: ["code_materiel", "numero_serie", "marque", "modele", "categorie_nom", "famille_nom"] },
      { title: "Stock et fournisseur", tone: "green", fields: ["statut_stock", "etat", "magasin_nom", "fournisseur_nom"] },
      { title: "Achat et garantie", tone: "orange", fields: ["date_achat", "prix_achat", "devise", "duree_garantie_mois", "garantie_fin", "date_enregistrement"] },
      { title: "Tracabilite", tone: "slate", fields: ["code_barre", "qr_code", "observation"] },
    ],
    traceabilityLabel: {
      titleField: "code_materiel",
      subtitleFields: ["marque", "modele"],
      barcodeField: "code_barre",
      qrField: "qr_code",
    },
    actions: [
      {
        label: "En panne",
        formResource: "reparations",
        variant: "danger",
        roles: materialActionRoles,
        visibleWhen: (row) => row.etat !== "EN_PANNE",
        getInitialValues: (row) => ({
          id_materiel: row.id_materiel,
          statut: "EN_ATTENTE",
          date_reparation: new Date().toISOString().slice(0, 10),
        }),
      },
      {
        label: "En reparation",
        formResource: "reparations",
        variant: "warning",
        roles: materialActionRoles,
        visibleWhen: (row) => row.etat !== "EN_REPARATION",
        getInitialValues: (row) => ({
          id_materiel: row.id_materiel,
          statut: "EN_COURS",
          date_reparation: new Date().toISOString().slice(0, 10),
        }),
      },
      {
        label: "Hors service",
        endpoint: "marquer-hors-service",
        variant: "muted",
        roles: materialActionRoles,
        visibleWhen: (row) => row.etat !== "HORS_SERVICE",
      },
    ],
  },
  consommables: {
    title: "Consommables",
    description: "Stocks consommables avec seuils d'alerte.",
    endpoint: "stock/consommables/",
    idField: "id_consommable",
    visibleRoles: businessRoles,
    writeRoles: adminOnlyWriteRoles,
    sortColumns: [
      { key: "date_creation", label: "Date creation", type: "date" },
    ],
    columns: [
      { key: "code_consommable", label: "Code" },
      { key: "nom_consommable", label: "Nom" },
      { key: "categorie_nom", label: "Categorie" },
      { key: "quantite_stock", label: "Stock" },
      { key: "seuil_alerte", label: "Seuil" },
      { key: "magasin_nom", label: "Magasin" },
    ],
    fields: [
      { name: "code_consommable", label: "Code", autoGenerated: true, disabled: true },
      { name: "nom_consommable", label: "Nom", required: true },
      { name: "id_famille", label: "Famille", type: "recordPicker", required: true, resource: "familles", virtual: true, createOnly: true, clears: ["id_categorie"], searchPlaceholder: "Rechercher une famille..." },
      { name: "id_categorie", label: "Categorie", type: "recordPicker", required: true, resource: "categories", filterOptions: categoryBelongsToSelectedFamily, disabledWhen: needsSelectedFamily, searchPlaceholder: "Rechercher une categorie..." },
      { name: "id_unite", label: "Unite", type: "recordPicker", required: true, resource: "unites", searchPlaceholder: "Rechercher une unite..." },
      { name: "id_magasin", label: "Magasin", type: "recordPicker", resource: "magasins", searchPlaceholder: "Rechercher un magasin..." },
      { name: "quantite_stock", label: "Quantite", type: "number", defaultValue: 0, min: 0 },
      { name: "seuil_alerte", label: "Seuil d'alerte", type: "number", min: 0 },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formGroups: [
      { title: "Identification", tone: "blue", fields: ["code_consommable", "nom_consommable", "id_famille", "id_categorie", "id_unite"] },
      { title: "Stock", tone: "green", fields: ["id_magasin", "quantite_stock", "seuil_alerte", "statut"] },
    ],
    formSteps: [
      { title: "Famille", tone: "blue", fields: ["id_famille", "id_categorie"] },
      { title: "Consommable", tone: "green", fields: ["nom_consommable", "id_unite"] },
      { title: "Stock", tone: "orange", fields: ["id_magasin", "quantite_stock", "seuil_alerte", "statut"] },
    ],
    detailGroups: [
      { title: "Identification", tone: "blue", fields: ["code_consommable", "nom_consommable", "categorie_nom", "famille_nom", "unite_nom"] },
      { title: "Stock", tone: "green", fields: ["magasin_nom", "quantite_stock", "seuil_alerte", "statut", "date_creation"] },
    ],
  },
  mouvements: {
    title: "Mouvements",
    description: "Entrees, sorties, transferts et ajustements.",
    endpoint: "operations/mouvements/",
    idField: "id_mouvement",
    visibleRoles: gestionRoles,
    writeRoles: operationWriteRoles,
    updateRoles: [],
    deleteRoles: [],
    columns: [
      { key: "type_mouvement", label: "Type" },
      { key: "article", label: "Article" },
      { key: "quantite", label: "Quantite" },
      { key: "magasin_source_nom", label: "Source" },
      { key: "magasin_destination_nom", label: "Destination" },
      { key: "date_mouvement", label: "Date", type: "date" },
    ],
    fields: [
      { name: "type_mouvement", label: "Type", type: "select", required: true, options: ["ENTREE", "SORTIE", "TRANSFERT", "AJUSTEMENT"] },
      { name: "id_materiel", label: "Materiel", type: "recordPicker", resource: "materiels", requiredWhen: fieldMissing("id_consommable"), availableWhen: materialCanMove, disabledWhen: anyRule(needsMovementType, fieldHasValue("id_consommable")), clears: ["magasin_source"], searchPlaceholder: "Rechercher un materiel..." },
      { name: "id_consommable", label: "Consommable", type: "recordPicker", resource: "consommables", requiredWhen: fieldMissing("id_materiel"), availableWhen: consommableCanLeaveStock, disabledWhen: anyRule(needsMovementType, fieldHasValue("id_materiel")), clears: ["magasin_source"], searchPlaceholder: "Rechercher un consommable..." },
      { name: "quantite", label: "Quantite", type: "number", required: true, defaultValue: 1, min: 1, max: selectedConsumableStock, disabledWhen: anyRule(needsMovementArticle, fieldHasValue("id_materiel")), disabledValue: 1 },
      { name: "magasin_source", label: "Magasin source", type: "recordPicker", resource: "magasins", requiredWhen: movementNeedsSource, filterOptions: magasinMatchesSelectedArticle, disabledWhen: anyRule(needsMovementType, needsMovementArticle, fieldValueIs("type_mouvement", "ENTREE"), fieldValueIs("type_mouvement", "AJUSTEMENT")), searchPlaceholder: "Rechercher le magasin source..." },
      { name: "magasin_destination", label: "Magasin destination", type: "recordPicker", resource: "magasins", requiredWhen: movementNeedsDestination, disabledWhen: anyRule(needsMovementType, needsMovementArticle, fieldValueIs("type_mouvement", "SORTIE"), fieldValueIs("type_mouvement", "AJUSTEMENT")), searchPlaceholder: "Rechercher le magasin destination..." },
      { name: "date_mouvement", label: "Date", type: "date" },
      { name: "reference_document", label: "Reference document" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Operation", tone: "blue", fields: ["type_mouvement", "date_mouvement", "reference_document"] },
      { title: "Article", tone: "green", fields: ["id_materiel", "id_consommable", "quantite"] },
      { title: "Magasins", tone: "orange", fields: ["magasin_source", "magasin_destination"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Operation", tone: "blue", fields: ["type_mouvement", "date_mouvement"] },
      { title: "Article", tone: "green", fields: ["id_materiel", "id_consommable", "quantite"] },
      { title: "Magasins", tone: "orange", fields: ["magasin_source", "magasin_destination"] },
      { title: "Reference", tone: "slate", fields: ["reference_document", "observation"] },
    ],
    detailGroups: [
      { title: "Operation", tone: "blue", fields: ["type_mouvement", "date_mouvement", "reference_document", "fait_par_nom"] },
      { title: "Article", tone: "green", fields: ["article", "article_type", "quantite"] },
      { title: "Magasins", tone: "orange", fields: ["magasin_source_nom", "magasin_destination_nom"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
  },
  affectations: {
    title: "Affectations",
    description: "Affectations et restitutions de materiels.",
    endpoint: "operations/affectations/",
    idField: "id_affectation",
    visibleRoles: magasinRoles,
    writeRoles: magasinRoles,
    deleteRoles: [],
    columns: [
      { key: "code_affectation", label: "Code" },
      { key: "materiel_label", label: "Materiel" },
      { key: "entite_type", label: "Entite" },
      { key: "entite_nom", label: "Destinataire" },
      { key: "date_affectation", label: "Date", type: "date" },
      { key: "statut", label: "Statut entretien" },
    ],
    fields: [
      { name: "code_affectation", label: "Code affectation", autoGenerated: true, disabled: true },
      { name: "id_famille", label: "Famille", type: "recordPicker", required: true, resource: "familles", virtual: true, createOnly: true, clears: ["id_categorie", "id_materiel"], searchPlaceholder: "Rechercher une famille..." },
      { name: "id_categorie", label: "Categorie", type: "recordPicker", required: true, resource: "categories", virtual: true, createOnly: true, filterOptions: categoryBelongsToSelectedFamily, disabledWhen: needsSelectedFamily, clears: ["id_materiel"], searchPlaceholder: "Rechercher une categorie..." },
      { name: "id_materiel", label: "Materiel disponible", type: "recordPicker", required: true, resource: "materiels", filterOptions: materialBelongsToSelectedCategory, availableWhen: materialIsAvailableForAffectation, disabledWhen: needsSelectedCategory, searchPlaceholder: "Rechercher par code, marque, modele, categorie, magasin...", emptyText: "Aucun materiel disponible pour cette categorie." },
      { name: "entite_type", label: "Type d'entite", type: "select", required: true, options: ["DEPARTEMENT", "DIRECTION", "AGENT", "MAGASIN"], clears: ["entite_id", "agent_id_departement", "agent_id_direction", "agent_matricule", "agent_nom_complet", "agent_telephone"] },
      { name: "entite_id", label: "Destinataire", type: "recordPicker", required: true, resource: resourceForEntiteType, optionResources: ["departements", "directions", "magasins"], visibleWhen: isNotAgentAffectation, disabledWhen: needsEntiteType, searchPlaceholder: "Rechercher le destinataire..." },
      { name: "agent_id_departement", label: "Departement de l'agent", type: "recordPicker", resource: "departements", requiredWhen: isAgentAffectation, visibleWhen: isAgentAffectation, clears: ["agent_id_direction"], searchPlaceholder: "Rechercher un departement..." },
      { name: "agent_id_direction", label: "Direction de l'agent", type: "recordPicker", resource: "directions", requiredWhen: isAgentAffectation, visibleWhen: isAgentAffectation, filterOptions: directionBelongsToAgentDepartment, disabledWhen: needsAgentDepartment, searchPlaceholder: "Rechercher une direction..." },
      { name: "agent_matricule", label: "Matricule agent", requiredWhen: isAgentAffectation, visibleWhen: isAgentAffectation },
      { name: "agent_nom_complet", label: "Nom complet agent", requiredWhen: isAgentAffectation, visibleWhen: isAgentAffectation },
      { name: "agent_telephone", label: "Telephone agent", visibleWhen: isAgentAffectation },
      { name: "date_affectation", label: "Date d'affectation", type: "date" },
      { name: "date_retour", label: "Date de retour", type: "date", disabledWhen: fieldValueIs("statut", "ACTIVE") },
      { name: "statut", label: "Statut", type: "select", options: ["ACTIVE", "RETOURNEE", "ANNULEE"], defaultValue: "ACTIVE", visibleWhen: visibleOnEdit },
      { name: "code_barre", label: "Code-barres", autoGenerated: true, disabled: true },
      { name: "qr_code", label: "QR code", autoGenerated: true, disabled: true },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Materiel", tone: "blue", fields: ["code_affectation", "id_famille", "id_categorie", "id_materiel"] },
      { title: "Destinataire", tone: "green", fields: ["entite_type", "entite_id"] },
      { title: "Agent beneficiaire", tone: "green", fields: ["agent_id_departement", "agent_id_direction", "agent_matricule", "agent_nom_complet", "agent_telephone"] },
      { title: "Suivi", tone: "orange", fields: ["date_affectation", "date_retour", "statut"] },
      { title: "Tracabilite", tone: "slate", fields: ["code_barre", "qr_code"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Famille", tone: "blue", fields: ["id_famille", "id_categorie"] },
      { title: "Materiel", tone: "green", fields: ["id_materiel"] },
      { title: "Destinataire", tone: "orange", fields: ["entite_type", "entite_id", "agent_id_departement", "agent_id_direction", "agent_matricule", "agent_nom_complet", "agent_telephone"] },
      { title: "Suivi", tone: "slate", fields: ["date_affectation", "date_retour", "statut", "observation"] },
    ],
    detailGroups: [
      { title: "Materiel", tone: "blue", fields: ["code_affectation", "materiel_label"] },
      { title: "Destinataire", tone: "green", fields: ["entite_type", "entite_nom", "agent_departement_nom", "agent_direction_nom", "agent_matricule", "agent_nom_complet", "agent_telephone"] },
      { title: "Suivi", tone: "orange", fields: ["date_affectation", "date_retour", "statut", "observation"] },
      { title: "Tracabilite", tone: "slate", fields: ["code_barre", "qr_code"] },
    ],
    traceabilityLabel: {
      titleField: "code_affectation",
      subtitleFields: ["materiel_label"],
      barcodeField: "code_barre",
      qrField: "qr_code",
      categoryField: "entite_type",
      locationField: "entite_nom",
      serialField: "date_affectation",
    },
  },
  consommations: {
    title: "Consommations",
    description: "Consommations de stock consommable.",
    endpoint: "operations/consommations/",
    idField: "id_consommation",
    visibleRoles: gestionRoles,
    writeRoles: operationWriteRoles,
    updateRoles: [],
    deleteRoles: [],
    columns: [
      { key: "consommable_label", label: "Consommable" },
      { key: "quantite", label: "Quantite" },
      { key: "destination_type", label: "Destination" },
      { key: "destination_nom", label: "Beneficiaire" },
      { key: "date_consommation", label: "Date", type: "date" },
      { key: "demandeur", label: "Demandeur" },
    ],
    fields: [
      { name: "id_consommable", label: "Consommable", type: "recordPicker", required: true, resource: "consommables", availableWhen: ({ option }) => Number(option.item?.quantite_stock || 0) > 0, searchPlaceholder: "Rechercher un consommable en stock..." },
      { name: "quantite", label: "Quantite", type: "number", required: true, defaultValue: 1, min: 1, max: selectedConsumableStock },
      { name: "destination_type", label: "Niveau de destination", type: "select", required: true, options: ["DEPARTEMENT", "DIRECTION"], defaultValue: "DEPARTEMENT", clears: ["id_departement", "id_direction"] },
      { name: "id_departement", label: "Departement", type: "recordPicker", required: true, resource: "departements", clears: ["id_direction"], searchPlaceholder: "Rechercher un departement..." },
      { name: "id_direction", label: "Direction", type: "recordPicker", resource: "directions", requiredWhen: isConsumptionDirection, visibleWhen: isConsumptionDirection, filterOptions: optionBelongsTo("id_departement"), disabledWhen: needsConsumptionDepartment, searchPlaceholder: "Rechercher une direction..." },
      { name: "date_consommation", label: "Date", type: "date" },
      { name: "demandeur", label: "Demandeur" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Consommable", tone: "blue", fields: ["id_consommable", "quantite"] },
      { title: "Destination", tone: "green", fields: ["destination_type", "id_departement", "id_direction"] },
      { title: "Demande", tone: "orange", fields: ["demandeur", "date_consommation"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Consommable", tone: "blue", fields: ["id_consommable", "quantite"] },
      { title: "Destination", tone: "green", fields: ["destination_type", "id_departement", "id_direction"] },
      { title: "Demandeur", tone: "orange", fields: ["demandeur", "date_consommation"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    detailGroups: [
      { title: "Consommable", tone: "blue", fields: ["consommable_label", "quantite"] },
      { title: "Destination", tone: "green", fields: ["destination_type", "departement_nom", "direction_nom", "destination_nom"] },
      { title: "Demande", tone: "orange", fields: ["demandeur", "date_consommation", "fait_par_nom"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
  },
  inventaires: {
    title: "Inventaires physiques",
    description: "Dossiers de controle physique avec leurs lignes de comptage.",
    endpoint: "inventaires/",
    idField: "id_inventaire",
    visibleRoles: magasinRoles,
    createRoles: magasinRoles,
    updateRoles: magasinRoles,
    deleteRoles: magasinRoles,
    createWhen: isInventoryOperator,
    updateWhen: isInventoryOperator,
    deleteWhen: isInventoryOperator,
    columns: [
      { key: "code_inventaire", label: "Code" },
      { key: "entite_nom", label: "Perimetre" },
      { key: "nombre_lignes", label: "Lignes" },
      { key: "type_inventaire", label: "Type" },
      { key: "date_debut", label: "Debut", type: "date" },
      { key: "statut", label: "Statut" },
    ],
    fields: [
      { name: "code_inventaire", label: "Code", autoGenerated: true, disabled: true },
      { name: "entite_type", label: "Type d'entite", type: "select", required: true, options: ["DEPARTEMENT", "DIRECTION", "MAGASIN"] },
      { name: "entite_id", label: "Perimetre", type: "recordPicker", required: true, resource: resourceForEntiteType, optionResources: ["departements", "directions", "magasins"], disabledWhen: needsEntiteType, searchPlaceholder: "Rechercher le perimetre..." },
      { name: "type_inventaire", label: "Type", type: "select", options: ["GENERAL", "PARTIEL", "PERIODIQUE", "EXCEPTIONNEL"], defaultValue: "GENERAL" },
      { name: "date_debut", label: "Date debut", type: "date" },
      { name: "date_fin", label: "Date fin", type: "date", disabledWhen: fieldValueIs("statut", "EN_COURS") },
      { name: "statut", label: "Statut", type: "select", options: ["EN_COURS", "TERMINE", "ANNULE"], defaultValue: "EN_COURS" },
      { name: "effectue_par_libre", label: "Equipe / personnes ayant compte", type: "textarea" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Perimetre", tone: "blue", fields: ["code_inventaire", "entite_type", "entite_id"] },
      { title: "Responsabilites", tone: "green", fields: ["effectue_par_libre"] },
      { title: "Planning", tone: "orange", fields: ["type_inventaire", "date_debut", "date_fin", "statut"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Perimetre", tone: "blue", fields: ["entite_type", "entite_id"] },
      { title: "Equipe", tone: "green", fields: ["effectue_par_libre"] },
      { title: "Planning", tone: "orange", fields: ["type_inventaire", "date_debut", "date_fin", "statut"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    detailGroups: [
      { title: "Session", tone: "blue", fields: ["code_inventaire", "entite_type", "entite_nom", "cree_par_nom"] },
      { title: "Equipe de comptage", tone: "green", fields: ["effectue_par_libre"] },
      { title: "Resume comptage", tone: "green", fields: ["nombre_lignes", "nombre_ecarts", "ecart_total"] },
      { title: "Lignes de comptage", tone: "orange", fields: ["lignes_comptage"] },
      { title: "Planning", tone: "orange", fields: ["type_inventaire", "date_debut", "date_fin", "statut"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    actions: [
      {
        label: "Ajouter une ligne de comptage",
        roles: magasinRoles,
        canUse: isInventoryOperator,
        formResource: "inventaireDetails",
        visibleWhen: (row) => row.statut === "EN_COURS",
        getInitialValues: (row) => ({
          id_inventaire: row.id_inventaire,
        }),
      },
    ],
  },
  inventaireDetails: {
    title: "Lignes de comptage",
    description: "Articles comptes dans une session d'inventaire.",
    endpoint: "inventaires/details/",
    idField: "id_detail",
    visibleRoles: magasinRoles,
    writeRoles: magasinRoles,
    columns: [
      { key: "inventaire_code", label: "Inventaire" },
      { key: "article_type", label: "Type article" },
      { key: "article_label", label: "Article compte" },
      { key: "categorie_nom", label: "Categorie" },
      { key: "quantite_theorique", label: "Theorique" },
      { key: "quantite_reelle", label: "Reelle" },
      { key: "ecart", label: "Ecart" },
    ],
    fields: [
      { name: "id_inventaire", label: "Inventaire", type: "hidden", required: true },
      { name: "article_search", label: "Article compte", type: "articleSearch", required: true, virtual: true, optionResources: ["materiels", "consommables"] },
      { name: "id_materiel", label: "Materiel", type: "hidden" },
      { name: "id_consommable", label: "Consommable", type: "hidden" },
      { name: "quantite_theorique", label: "Quantite theorique", type: "number", defaultValue: 0 },
      { name: "quantite_reelle", label: "Quantite reelle", type: "number", defaultValue: 0 },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Article compte", tone: "green", fields: ["article_search", "id_inventaire", "id_materiel", "id_consommable"] },
      { title: "Resultat du comptage", tone: "orange", fields: ["quantite_theorique", "quantite_reelle"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Article", tone: "green", fields: ["article_search", "id_inventaire", "id_materiel", "id_consommable"] },
      { title: "Comptage", tone: "orange", fields: ["quantite_theorique", "quantite_reelle"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    detailGroups: [
      { title: "Session parent", tone: "blue", fields: ["inventaire_code", "inventaire_perimetre"] },
      { title: "Article compte", tone: "green", fields: ["article_type", "article_label", "categorie_nom", "famille_nom"] },
      { title: "Resultat du comptage", tone: "orange", fields: ["quantite_theorique", "quantite_reelle", "ecart"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
  },
  entretiens: {
    title: "Entretiens",
    description: "Entretiens preventifs, correctifs et controles.",
    endpoint: "maintenance/entretiens/",
    idField: "id_entretien",
    visibleRoles: businessRoles,
    createRoles: gestionRoles,
    updateRoles: magasinRoles,
    deleteRoles: adminOnlyWriteRoles,
    columns: [
      { key: "materiel_label", label: "Materiel" },
      { key: "materiel_categorie", label: "Categorie" },
      { key: "date_entretien", label: "Date", type: "date" },
      { key: "type_entretien", label: "Type" },
      { key: "cout_entretien", label: "Cout" },
      { key: "statut", label: "Statut" },
    ],
    fields: [
      { name: "id_materiel", label: "Materiel", type: "recordPicker", required: true, resource: "materiels", hiddenWhen: prefilledByAction("id_materiel"), searchPlaceholder: "Rechercher un materiel..." },
      { name: "date_entretien", label: "Date", type: "date", visibleWhen: isNotGestionCreate },
      { name: "date_fin_prevue", label: "Fin prevue", type: "date", visibleWhen: isNotGestionCreate },
      { name: "date_fin_reelle", label: "Fin reelle", type: "date", disabledWhen: fieldValueIsNot("statut", "TERMINE"), visibleWhen: isNotGestionCreate },
      { name: "description", label: "Description", type: "textarea", visibleWhen: isNotGestionCreate },
      { name: "cout_entretien", label: "Cout", type: "number", defaultValue: 0, visibleWhen: isNotGestionCreate },
      { name: "type_entretien", label: "Type", type: "select", options: ["PREVENTIF", "CORRECTIF", "CONTROLE"], defaultValue: "PREVENTIF", visibleWhen: isNotGestionCreate },
      { name: "type_prestataire", label: "Prestataire", type: "select", options: ["AUCUN", "INTERNE", "PRESTATAIRE", "CONSTRUCTEUR"], defaultValue: "AUCUN", visibleWhen: isNotGestionCreate },
      { name: "nom_prestataire", label: "Nom prestataire", disabledWhen: fieldValueIs("type_prestataire", "CONSTRUCTEUR"), clearWhenDisabled: false, visibleWhen: isNotGestionCreate },
      { name: "statut", label: "Statut de l'entretien", type: "select", options: ["EN_COURS", "TERMINE", "ANNULE"], defaultValue: "EN_COURS", visibleWhen: isNotGestionCreate },
      { name: "observation", label: "Observation", type: "textarea", requiredWhen: isGestionCreate },
    ],
    formGroups: [
      { title: "Demande", tone: "blue", fields: ["id_materiel", "observation"] },
      { title: "Execution", tone: "green", fields: ["date_entretien", "date_fin_prevue", "date_fin_reelle", "statut"] },
      { title: "Intervention", tone: "orange", fields: ["type_entretien", "type_prestataire", "nom_prestataire", "cout_entretien"] },
      { title: "Notes", tone: "slate", fields: ["description"] },
    ],
    formSteps: [
      { title: "Materiel", tone: "blue", fields: ["id_materiel", "observation"] },
      { title: "Execution", tone: "green", fields: ["date_entretien", "date_fin_prevue", "date_fin_reelle", "statut"] },
      { title: "Intervention", tone: "orange", fields: ["type_entretien", "type_prestataire", "nom_prestataire", "cout_entretien"] },
      { title: "Notes", tone: "slate", fields: ["description"] },
    ],
    detailGroups: [
      { title: "Materiel", tone: "blue", fields: ["materiel_label", "materiel_categorie", "materiel_famille"] },
      { title: "Execution", tone: "green", fields: ["date_entretien", "date_fin_prevue", "date_fin_reelle", "statut"] },
      { title: "Intervention", tone: "orange", fields: ["type_entretien", "type_prestataire", "nom_prestataire", "cout_entretien"] },
      { title: "Notes", tone: "slate", fields: ["description", "observation"] },
    ],
  },
  reparations: {
    title: "Reparations",
    description: "Pannes et reparations de materiels.",
    endpoint: "maintenance/reparations/",
    idField: "id_reparation",
    visibleRoles: gestionRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "materiel_label", label: "Materiel" },
      { key: "materiel_categorie", label: "Categorie" },
      { key: "materiel_famille", label: "Famille" },
      { key: "date_reparation", label: "Date", type: "date" },
      { key: "cout_reparation", label: "Cout" },
      { key: "type_prestataire", label: "Prestataire" },
      { key: "statut", label: "Statut reparation" },
    ],
    fields: [
      { name: "id_materiel", label: "Materiel", type: "recordPicker", required: true, resource: "materiels", hiddenWhen: prefilledByAction("id_materiel"), searchPlaceholder: "Rechercher un materiel..." },
      { name: "date_reparation", label: "Date", type: "date" },
      { name: "date_fin_prevue", label: "Fin prevue", type: "date" },
      { name: "date_fin_reelle", label: "Fin reelle", type: "date", disabledWhen: fieldValueIsNot("statut", "TERMINEE") },
      { name: "description", label: "Description", type: "textarea" },
      { name: "cout_reparation", label: "Cout", type: "number", defaultValue: 0 },
      { name: "type_prestataire", label: "Prestataire", type: "select", options: ["AUCUN", "INTERNE", "PRESTATAIRE", "CONSTRUCTEUR"], defaultValue: "AUCUN" },
      { name: "nom_prestataire", label: "Nom prestataire", disabledWhen: fieldValueIs("type_prestataire", "CONSTRUCTEUR"), clearWhenDisabled: false },
      { name: "statut", label: "Statut de la reparation", type: "select", options: ["EN_ATTENTE", "EN_COURS", "TERMINEE", "ANNULEE"], defaultValue: "EN_ATTENTE", hiddenWhen: prefilledByAction("statut") },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Materiel", tone: "blue", fields: ["id_materiel"] },
      { title: "Reparation", tone: "green", fields: ["date_reparation", "date_fin_prevue", "date_fin_reelle", "statut"] },
      { title: "Prestataire", tone: "orange", fields: ["type_prestataire", "nom_prestataire", "cout_reparation"] },
      { title: "Notes", tone: "slate", fields: ["description", "observation"] },
    ],
    formSteps: [
      { title: "Materiel", tone: "blue", fields: ["id_materiel"] },
      { title: "Reparation", tone: "green", fields: ["date_reparation", "date_fin_prevue", "date_fin_reelle", "statut"] },
      { title: "Prestataire", tone: "orange", fields: ["type_prestataire", "nom_prestataire", "cout_reparation"] },
      { title: "Notes", tone: "slate", fields: ["description", "observation"] },
    ],
    detailGroups: [
      { title: "Materiel", tone: "blue", fields: ["materiel_label", "materiel_categorie", "materiel_famille"] },
      { title: "Reparation", tone: "green", fields: ["date_reparation", "date_fin_prevue", "date_fin_reelle", "statut"] },
      { title: "Prestataire", tone: "orange", fields: ["type_prestataire", "nom_prestataire", "cout_reparation"] },
      { title: "Notes", tone: "slate", fields: ["description", "observation"] },
    ],
  },
  demandes: {
    title: "Demandes",
    description: "Demandes d'achat, reapprovisionnement ou reparation.",
    endpoint: "demandes/",
    idField: "id_demande",
    visibleRoles: businessRoles,
    createRoles: gestionRoles,
    updateRoles: adminOnlyWriteRoles,
    deleteRoles: adminOnlyWriteRoles,
    createWhen: (user) => user?.role === ROLES.ADMIN || isDirectionRequester(user),
    sortColumns: [
      { key: "date_demande", label: "Date", type: "date" },
    ],
    columns: [
      { key: "code_demande", label: "Code" },
      { key: "departement_nom", label: "Departement" },
      { key: "direction_nom", label: "Direction" },
      { key: "type_demande", label: "Type" },
      { key: "materiel_label", label: "Materiel" },
      { key: "consommable_label", label: "Consommable" },
      { key: "quantite_demandee", label: "Quantite" },
      { key: "statut", label: "Statut" },
      { key: "date_demande", label: "Date", type: "date" },
    ],
    fields: [
      { name: "code_demande", label: "Code", autoGenerated: true, disabled: true },
      { name: "id_departement", label: "Departement", type: "recordPicker", required: true, resource: "departements", disabledWhen: currentUserIsNotAdmin, searchPlaceholder: "Rechercher un departement..." },
      { name: "id_direction_demandeuse", label: "Direction demandeuse", type: "recordPicker", required: true, resource: "directions", disabledWhen: anyRule(currentUserIsNotAdmin, fieldMissing("id_departement")), filterOptions: optionBelongsTo("id_departement"), searchPlaceholder: "Rechercher une direction..." },
      { name: "origine_type", label: "Origine", type: "select", options: ["DIRECTION", "DEPARTEMENT", "MAGASIN"], defaultValue: "DIRECTION", disabledWhen: currentUserIsNotAdmin },
      { name: "origine_id", label: "ID origine", type: "number", disabledWhen: currentUserIsNotAdmin },
      { name: "type_demande", label: "Type", type: "select", required: true, options: ["ACHAT", "REAPPROVISIONNEMENT", "REPARATION", "AUTRE"] },
      { name: "id_materiel", label: "Materiel concerne", type: "recordPicker", resource: "materiels", requiredWhen: fieldValueIs("type_demande", "REPARATION"), disabledWhen: fieldValueIsNot("type_demande", "REPARATION"), searchPlaceholder: "Rechercher un materiel..." },
      { name: "id_consommable", label: "Consommable concerne", type: "recordPicker", resource: "consommables", requiredWhen: fieldValueIs("type_demande", "REAPPROVISIONNEMENT"), disabledWhen: fieldValueIsNot("type_demande", "REAPPROVISIONNEMENT"), searchPlaceholder: "Rechercher un consommable..." },
      { name: "quantite_demandee", label: "Quantite demandee", type: "number", defaultValue: 1, disabledWhen: fieldValueIsNot("type_demande", "REAPPROVISIONNEMENT"), disabledValue: 1 },
      { name: "date_demande", label: "Date", type: "date" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Origine", tone: "blue", fields: ["id_departement", "id_direction_demandeuse"] },
      { title: "Besoin", tone: "green", fields: ["type_demande", "id_materiel", "id_consommable", "quantite_demandee"] },
      { title: "Suivi", tone: "orange", fields: ["date_demande", "origine_type", "origine_id"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Departement", tone: "blue", fields: ["id_departement"] },
      { title: "Direction", tone: "green", fields: ["id_direction_demandeuse"] },
      { title: "Besoin", tone: "orange", fields: ["type_demande", "id_materiel", "id_consommable", "quantite_demandee"] },
      { title: "Suivi", tone: "slate", fields: ["date_demande", "origine_type", "origine_id", "observation"] },
    ],
    detailGroups: [
      { title: "Demande", tone: "blue", fields: ["code_demande", "type_demande", "statut", "date_demande"] },
      { title: "Origine", tone: "green", fields: ["departement_nom", "direction_nom", "demandeur_nom"] },
      { title: "Article", tone: "orange", fields: ["materiel_label", "consommable_label", "quantite_demandee"] },
      { title: "Validation", tone: "slate", fields: ["validateur_departement_nom", "date_validation_departement", "magasinier_finalisateur_nom", "date_finalisation", "motif_rejet", "observation"] },
    ],
    actions: [
      {
        label: "Valider",
        endpoint: "valider-departement",
        roles: gestionRoles,
        canUse: (user) => user?.role === ROLES.ADMIN || isDepartmentValidator(user),
        visibleWhen: (row) => row.statut === "EN_ATTENTE_DEPARTEMENT",
      },
      {
        label: "Rejeter",
        endpoint: "rejeter-departement",
        roles: gestionRoles,
        canUse: (user) => user?.role === ROLES.ADMIN || isDepartmentValidator(user),
        visibleWhen: (row) => row.statut === "EN_ATTENTE_DEPARTEMENT",
        prompt: {
          title: "Motif du rejet",
          label: "Motif",
          field: "motif_rejet",
          required: true,
        },
      },
      {
        label: "Finaliser",
        endpoint: "finaliser-magasin",
        roles: magasinRoles,
        canUse: (user) => user?.role === ROLES.ADMIN || isGeneralStorekeeper(user),
        visibleWhen: (row) => row.statut === "EN_TRAITEMENT_MAGASIN",
      },
    ],
  },
  documents: {
    title: "Documents",
    description: "Pieces liees aux materiels ou consommables.",
    endpoint: "documents/",
    idField: "id_document",
    visibleRoles: magasinRoles,
    createRoles: businessWriteRoles,
    updateRoles: adminOnlyWriteRoles,
    deleteRoles: adminOnlyWriteRoles,
    sortColumns: [
      { key: "date_upload", label: "Date upload", type: "date" },
    ],
    columns: [
      { key: "titre", label: "Titre" },
      { key: "type_document", label: "Type" },
      { key: "numero_document", label: "Numero" },
      { key: "article_type", label: "Article" },
      { key: "article", label: "Element lie" },
    ],
    fields: [
      { name: "titre", label: "Titre", required: true },
      { name: "type_document", label: "Type", type: "select", options: ["FACTURE", "BON_LIVRAISON", "GARANTIE", "FICHE_TECHNIQUE", "AUTRE"], defaultValue: "AUTRE" },
      { name: "numero_document", label: "Numero" },
      { name: "id_materiel", label: "Materiel", type: "recordPicker", resource: "materiels", requiredWhen: fieldMissing("id_consommable"), disabledWhen: fieldHasValue("id_consommable"), searchPlaceholder: "Rechercher un materiel..." },
      { name: "id_consommable", label: "Consommable", type: "recordPicker", resource: "consommables", requiredWhen: fieldMissing("id_materiel"), disabledWhen: fieldHasValue("id_materiel"), searchPlaceholder: "Rechercher un consommable..." },
      { name: "cree_par", label: "Cree par", type: "recordPicker", required: true, resource: "users", searchPlaceholder: "Rechercher un utilisateur..." },
      { name: "chemin_fichier", label: "Document PDF scanne", type: "file", accept: "application/pdf,.pdf", required: true },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
    formGroups: [
      { title: "Document", tone: "blue", fields: ["titre", "type_document", "numero_document"] },
      { title: "Article lie", tone: "green", fields: ["id_materiel", "id_consommable"] },
      { title: "Fichier", tone: "orange", fields: ["chemin_fichier", "cree_par"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    formSteps: [
      { title: "Document", tone: "blue", fields: ["titre", "type_document", "numero_document"] },
      { title: "Article", tone: "green", fields: ["id_materiel", "id_consommable"] },
      { title: "Fichier", tone: "orange", fields: ["chemin_fichier", "cree_par"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
    detailGroups: [
      { title: "Document", tone: "blue", fields: ["titre", "type_document", "numero_document"] },
      { title: "Article lie", tone: "green", fields: ["article_type", "article"] },
      { title: "Fichier", tone: "orange", fields: ["chemin_fichier", "date_upload", "cree_par_nom"] },
      { title: "Notes", tone: "slate", fields: ["observation"] },
    ],
  },
  users: {
    title: "Utilisateurs",
    description: "Comptes, roles et perimetres.",
    endpoint: "comptes/users/",
    idField: "id_users",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    deleteRoles: [],
    sortColumns: [
      { key: "date_joined", label: "Date creation", type: "date" },
      { key: "last_login", label: "Derniere connexion", type: "date" },
    ],
    columns: [
      { key: "nom_users", label: "Nom" },
      { key: "matricule", label: "Matricule" },
      { key: "email", label: "Email" },
      { key: "role_libelle", label: "Role" },
      { key: "perimetre", label: "Perimetre" },
      { key: "is_active", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "nom_users", label: "Nom", required: true },
      { name: "matricule", label: "Matricule", requiredWhen: userNeedsManualMatricule, visibleWhen: userNeedsManualMatricule },
      { name: "email", label: "Email", type: "email" },
      { name: "telephone", label: "Telephone" },
      { name: "password", label: "Mot de passe", type: "password", createOnly: true, required: true },
      { name: "id_role", label: "Role", type: "select", required: true, resource: "roles" },
      { name: "scope_type", label: "Perimetre", type: "select", options: ["GENERAL", "DEPARTEMENT", "DIRECTION", "MAGASIN"], defaultValue: "GENERAL", disabledWhen: selectedRoleIsFixedGeneral, disabledValue: "GENERAL" },
      { name: "id_departement", label: "Departement", type: "recordPicker", resource: "departements", requiredWhen: fieldValueIs("scope_type", "DEPARTEMENT"), disabledWhen: anyRule(selectedRoleIsFixedGeneral, fieldValueIsNot("scope_type", "DEPARTEMENT")), searchPlaceholder: "Rechercher un departement..." },
      { name: "id_direction", label: "Direction", type: "recordPicker", resource: "directions", requiredWhen: fieldValueIs("scope_type", "DIRECTION"), disabledWhen: anyRule(selectedRoleIsFixedGeneral, fieldValueIsNot("scope_type", "DIRECTION")), searchPlaceholder: "Rechercher une direction..." },
      { name: "id_magasin", label: "Magasin", type: "recordPicker", resource: "magasins", requiredWhen: fieldValueIs("scope_type", "MAGASIN"), disabledWhen: anyRule(selectedRoleIsFixedGeneral, fieldValueIsNot("scope_type", "MAGASIN")), searchPlaceholder: "Rechercher un magasin..." },
      { name: "is_active", label: "Actif", type: "checkbox", defaultValue: true },
    ],
    formSteps: [
      { title: "Role", tone: "blue", fields: ["id_role", "scope_type"] },
      { title: "Perimetre", tone: "green", fields: ["id_departement", "id_direction", "id_magasin"] },
      { title: "Identite", tone: "orange", fields: ["nom_users", "matricule", "email", "telephone", "password"] },
      { title: "Statut", tone: "slate", fields: ["is_active"] },
    ],
  },
  roles: {
    title: "Roles",
    description: "Roles applicatifs.",
    endpoint: "comptes/roles/",
    idField: "id_role",
    visibleRoles: adminOnlyRoles,
    writeRoles: [],
    columns: [
      { key: "code_role", label: "Code" },
      { key: "nom_role", label: "Nom" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_role", label: "Code", required: true },
      { name: "nom_role", label: "Nom", required: true },
      { name: "description", label: "Description", type: "textarea" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
  },
};

export function getResourceConfig(key) {
  return resourceConfigs[key];
}
