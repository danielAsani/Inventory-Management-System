import { ROLES } from "../utils/permissions";

export const adminOnlyRoles = [ROLES.ADMIN];
export const businessRoles = [ROLES.ADMIN, ROLES.GESTION, ROLES.MAGASIN];
export const gestionRoles = [ROLES.ADMIN, ROLES.GESTION];
export const magasinRoles = [ROLES.ADMIN, ROLES.MAGASIN];
export const adminOnlyWriteRoles = adminOnlyRoles;
export const businessWriteRoles = gestionRoles;
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

function fieldHasValue(fieldName) {
  return ({ values }) => values[fieldName] !== undefined && values[fieldName] !== null && values[fieldName] !== "";
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
      { key: "id_departement", label: "Departement" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_direction", label: "Code", required: true },
      { name: "nom_direction", label: "Nom", required: true },
      { name: "abreviation", label: "Abreviation" },
      { name: "id_departement", label: "Departement", type: "select", required: true, resource: "departements" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
  },
  services: {
    title: "Services",
    description: "Services rattaches aux directions.",
    endpoint: "organisation/services/",
    idField: "id_service",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "code_service", label: "Code" },
      { key: "nom_service", label: "Nom" },
      { key: "id_direction", label: "Direction" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_service", label: "Code", required: true },
      { name: "nom_service", label: "Nom", required: true },
      { name: "abreviation", label: "Abreviation" },
      { name: "id_direction", label: "Direction", type: "select", required: true, resource: "directions" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
  },
  magasins: {
    title: "Magasins",
    description: "Magasins et emplacements de stockage.",
    endpoint: "stock/magasins/",
    idField: "id_magasin",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "code_magasin", label: "Code" },
      { key: "nom_magasin", label: "Nom" },
      { key: "id_service", label: "Service" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_magasin", label: "Code", required: true },
      { name: "nom_magasin", label: "Nom", required: true },
      { name: "id_service", label: "Service", type: "select", resource: "services" },
      { name: "description_localisation", label: "Localisation", type: "textarea" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
  },
  familles: {
    title: "Familles",
    description: "Familles d'inventaire.",
    endpoint: "catalogue/familles/",
    idField: "id_famille",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "code_famille", label: "Code" },
      { key: "nom_famille", label: "Nom" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_famille", label: "Code", required: true },
      { name: "nom_famille", label: "Nom", required: true },
      { name: "description", label: "Description", type: "textarea" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
  },
  categories: {
    title: "Categories",
    description: "Categories rattachees aux familles.",
    endpoint: "catalogue/categories/",
    idField: "id_categorie",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "code_categorie", label: "Code" },
      { key: "nom_categorie", label: "Nom" },
      { key: "id_famille", label: "Famille" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "code_categorie", label: "Code", required: true },
      { name: "nom_categorie", label: "Nom", required: true },
      { name: "id_famille", label: "Famille", type: "select", required: true, resource: "familles" },
      { name: "description", label: "Description", type: "textarea" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
    ],
  },
  unites: {
    title: "Unites de mesure",
    description: "Unites utilisees par les consommables.",
    endpoint: "catalogue/unites/",
    idField: "id_unite",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
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
  },
  materiels: {
    title: "Materiels",
    description: "Materiels suivis individuellement.",
    endpoint: "stock/materiels/",
    idField: "id_materiel",
    visibleRoles: businessRoles,
    writeRoles: businessWriteRoles,
    columns: [
      { key: "code_materiel", label: "Code" },
      { key: "marque", label: "Marque" },
      { key: "modele", label: "Modele" },
      { key: "etat", label: "Etat" },
      { key: "id_magasin", label: "Magasin" },
    ],
    fields: [
      { name: "code_materiel", label: "Code", required: true },
      { name: "id_categorie", label: "Categorie", type: "select", required: true, resource: "categories" },
      { name: "id_magasin", label: "Magasin", type: "select", resource: "magasins", disabledWhen: fieldValueIs("etat", "AFFECTE") },
      { name: "id_fournisseur", label: "Fournisseur", type: "select", resource: "fournisseurs" },
      { name: "numero_serie", label: "Numero de serie" },
      { name: "marque", label: "Marque", required: true },
      { name: "modele", label: "Modele" },
      { name: "date_achat", label: "Date d'achat", type: "date", required: true },
      { name: "prix_achat", label: "Prix d'achat", type: "number", required: true, defaultValue: 0 },
      { name: "devise", label: "Devise", defaultValue: "USD" },
      { name: "duree_garantie_mois", label: "Garantie (mois)", type: "number", defaultValue: 0 },
      { name: "garantie_fin", label: "Fin garantie", type: "date" },
      { name: "etat", label: "Etat", type: "select", required: true, options: ["NEUF", "BON", "EN_STOCK", "AFFECTE", "EN_PANNE", "EN_REPARATION", "HORS_SERVICE"], defaultValue: "NEUF" },
      { name: "code_barre", label: "Code-barres", required: true },
      { name: "qr_code", label: "QR code", required: true },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
  },
  consommables: {
    title: "Consommables",
    description: "Stocks consommables avec seuils d'alerte.",
    endpoint: "stock/consommables/",
    idField: "id_consommable",
    visibleRoles: businessRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "code_consommable", label: "Code" },
      { key: "nom_consommable", label: "Nom" },
      { key: "quantite_stock", label: "Stock" },
      { key: "seuil_alerte", label: "Seuil" },
      { key: "id_magasin", label: "Magasin" },
    ],
    fields: [
      { name: "code_consommable", label: "Code", required: true },
      { name: "nom_consommable", label: "Nom", required: true },
      { name: "id_categorie", label: "Categorie", type: "select", required: true, resource: "categories" },
      { name: "id_unite", label: "Unite", type: "select", required: true, resource: "unites" },
      { name: "id_magasin", label: "Magasin", type: "select", resource: "magasins" },
      { name: "quantite_stock", label: "Quantite", type: "number", defaultValue: 0 },
      { name: "seuil_alerte", label: "Seuil d'alerte", type: "number" },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
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
      { key: "quantite", label: "Quantite" },
      { key: "magasin_source", label: "Source" },
      { key: "magasin_destination", label: "Destination" },
      { key: "date_mouvement", label: "Date", type: "date" },
    ],
    fields: [
      { name: "type_mouvement", label: "Type", type: "select", required: true, options: ["ENTREE", "SORTIE", "TRANSFERT", "AJUSTEMENT"] },
      { name: "id_materiel", label: "Materiel", type: "select", resource: "materiels", disabledWhen: fieldHasValue("id_consommable") },
      { name: "id_consommable", label: "Consommable", type: "select", resource: "consommables", disabledWhen: fieldHasValue("id_materiel") },
      { name: "quantite", label: "Quantite", type: "number", required: true, defaultValue: 1, disabledWhen: fieldHasValue("id_materiel"), disabledValue: 1 },
      { name: "magasin_source", label: "Magasin source", type: "select", resource: "magasins", disabledWhen: anyRule(fieldValueIs("type_mouvement", "ENTREE"), fieldValueIs("type_mouvement", "AJUSTEMENT")) },
      { name: "magasin_destination", label: "Magasin destination", type: "select", resource: "magasins", disabledWhen: anyRule(fieldValueIs("type_mouvement", "SORTIE"), fieldValueIs("type_mouvement", "AJUSTEMENT")) },
      { name: "date_mouvement", label: "Date", type: "date" },
      { name: "reference_document", label: "Reference document" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
  },
  affectations: {
    title: "Affectations",
    description: "Affectations et restitutions de materiels.",
    endpoint: "operations/affectations/",
    idField: "id_affectation",
    visibleRoles: gestionRoles,
    writeRoles: businessWriteRoles,
    deleteRoles: [],
    columns: [
      { key: "id_materiel", label: "Materiel" },
      { key: "entite_type", label: "Entite" },
      { key: "entite_id", label: "ID entite" },
      { key: "date_affectation", label: "Date", type: "date" },
      { key: "statut", label: "Statut" },
    ],
    fields: [
      { name: "id_materiel", label: "Materiel", type: "select", required: true, resource: "materiels" },
      { name: "entite_type", label: "Type d'entite", type: "select", required: true, options: ["DEPARTEMENT", "DIRECTION", "SERVICE", "UTILISATEUR"] },
      { name: "entite_id", label: "ID entite", type: "number", required: true },
      { name: "date_affectation", label: "Date d'affectation", type: "date" },
      { name: "date_retour", label: "Date de retour", type: "date", disabledWhen: fieldValueIs("statut", "ACTIVE") },
      { name: "statut", label: "Statut", type: "select", options: ["ACTIVE", "RETOURNEE", "ANNULEE"], defaultValue: "ACTIVE" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
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
      { key: "id_consommable", label: "Consommable" },
      { key: "quantite", label: "Quantite" },
      { key: "date_consommation", label: "Date", type: "date" },
      { key: "demandeur", label: "Demandeur" },
    ],
    fields: [
      { name: "id_consommable", label: "Consommable", type: "select", required: true, resource: "consommables" },
      { name: "quantite", label: "Quantite", type: "number", required: true, defaultValue: 1 },
      { name: "date_consommation", label: "Date", type: "date" },
      { name: "demandeur", label: "Demandeur" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
  },
  inventaires: {
    title: "Inventaires physiques",
    description: "Sessions d'inventaire par perimetre.",
    endpoint: "inventaires/",
    idField: "id_inventaire",
    visibleRoles: gestionRoles,
    writeRoles: businessWriteRoles,
    columns: [
      { key: "code_inventaire", label: "Code" },
      { key: "entite_type", label: "Entite" },
      { key: "type_inventaire", label: "Type" },
      { key: "date_debut", label: "Debut", type: "date" },
      { key: "statut", label: "Statut" },
    ],
    fields: [
      { name: "code_inventaire", label: "Code", required: true },
      { name: "entite_type", label: "Type d'entite", type: "select", required: true, options: ["DEPARTEMENT", "DIRECTION", "SERVICE", "MAGASIN"] },
      { name: "entite_id", label: "ID entite", type: "number", required: true },
      { name: "type_inventaire", label: "Type", type: "select", options: ["GENERAL", "PARTIEL", "PERIODIQUE", "EXCEPTIONNEL"], defaultValue: "GENERAL" },
      { name: "date_debut", label: "Date debut", type: "date" },
      { name: "date_fin", label: "Date fin", type: "date", disabledWhen: fieldValueIs("statut", "EN_COURS") },
      { name: "statut", label: "Statut", type: "select", options: ["EN_COURS", "TERMINE", "ANNULE"], defaultValue: "EN_COURS" },
      { name: "effectue_par", label: "Effectue par", type: "select", resource: "users" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
  },
  inventaireDetails: {
    title: "Details d'inventaire",
    description: "Ecarts entre quantites theoriques et reelles.",
    endpoint: "inventaires/details/",
    idField: "id_detail",
    visibleRoles: gestionRoles,
    writeRoles: businessWriteRoles,
    columns: [
      { key: "id_inventaire", label: "Inventaire" },
      { key: "id_materiel", label: "Materiel" },
      { key: "id_consommable", label: "Consommable" },
      { key: "quantite_theorique", label: "Theorique" },
      { key: "quantite_reelle", label: "Reelle" },
      { key: "ecart", label: "Ecart" },
    ],
    fields: [
      { name: "id_inventaire", label: "Inventaire", type: "select", required: true, resource: "inventaires" },
      { name: "id_materiel", label: "Materiel", type: "select", resource: "materiels", disabledWhen: fieldHasValue("id_consommable") },
      { name: "id_consommable", label: "Consommable", type: "select", resource: "consommables", disabledWhen: fieldHasValue("id_materiel") },
      { name: "quantite_theorique", label: "Quantite theorique", type: "number", defaultValue: 0 },
      { name: "quantite_reelle", label: "Quantite reelle", type: "number", defaultValue: 0 },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
  },
  entretiens: {
    title: "Entretiens",
    description: "Entretiens preventifs, correctifs et controles.",
    endpoint: "maintenance/entretiens/",
    idField: "id_entretien",
    visibleRoles: gestionRoles,
    writeRoles: businessWriteRoles,
    columns: [
      { key: "id_materiel", label: "Materiel" },
      { key: "date_entretien", label: "Date", type: "date" },
      { key: "type_entretien", label: "Type" },
      { key: "cout_entretien", label: "Cout" },
      { key: "statut", label: "Statut" },
    ],
    fields: [
      { name: "id_materiel", label: "Materiel", type: "select", required: true, resource: "materiels" },
      { name: "date_entretien", label: "Date", type: "date" },
      { name: "date_fin_prevue", label: "Fin prevue", type: "date" },
      { name: "date_fin_reelle", label: "Fin reelle", type: "date", disabledWhen: fieldValueIsNot("statut", "TERMINE") },
      { name: "description", label: "Description", type: "textarea" },
      { name: "cout_entretien", label: "Cout", type: "number", defaultValue: 0 },
      { name: "type_entretien", label: "Type", type: "select", options: ["PREVENTIF", "CORRECTIF", "CONTROLE"], defaultValue: "PREVENTIF" },
      { name: "type_prestataire", label: "Prestataire", type: "select", options: ["AUCUN", "INTERNE", "PRESTATAIRE", "CONSTRUCTEUR"], defaultValue: "AUCUN" },
      { name: "nom_prestataire", label: "Nom prestataire" },
      { name: "statut", label: "Statut", type: "select", options: ["PLANIFIE", "EN_COURS", "TERMINE", "ANNULE"], defaultValue: "PLANIFIE" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
  },
  reparations: {
    title: "Reparations",
    description: "Pannes et reparations de materiels.",
    endpoint: "maintenance/reparations/",
    idField: "id_reparation",
    visibleRoles: gestionRoles,
    writeRoles: businessWriteRoles,
    columns: [
      { key: "id_materiel", label: "Materiel" },
      { key: "date_reparation", label: "Date", type: "date" },
      { key: "cout_reparation", label: "Cout" },
      { key: "type_prestataire", label: "Prestataire" },
      { key: "statut", label: "Statut" },
    ],
    fields: [
      { name: "id_materiel", label: "Materiel", type: "select", required: true, resource: "materiels" },
      { name: "date_reparation", label: "Date", type: "date" },
      { name: "date_fin_prevue", label: "Fin prevue", type: "date" },
      { name: "date_fin_reelle", label: "Fin reelle", type: "date", disabledWhen: fieldValueIsNot("statut", "TERMINEE") },
      { name: "description", label: "Description", type: "textarea" },
      { name: "cout_reparation", label: "Cout", type: "number", defaultValue: 0 },
      { name: "type_prestataire", label: "Prestataire", type: "select", options: ["AUCUN", "INTERNE", "PRESTATAIRE", "CONSTRUCTEUR"], defaultValue: "AUCUN" },
      { name: "nom_prestataire", label: "Nom prestataire" },
      { name: "statut", label: "Statut", type: "select", options: ["EN_ATTENTE", "EN_COURS", "TERMINEE", "ANNULEE"], defaultValue: "EN_ATTENTE" },
      { name: "observation", label: "Observation", type: "textarea" },
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
    columns: [
      { key: "code_demande", label: "Code" },
      { key: "id_departement", label: "Departement" },
      { key: "id_direction_demandeuse", label: "Direction" },
      { key: "id_service_destinataire", label: "Service vise" },
      { key: "type_demande", label: "Type" },
      { key: "id_materiel", label: "Materiel" },
      { key: "id_consommable", label: "Consommable" },
      { key: "quantite_demandee", label: "Quantite" },
      { key: "statut", label: "Statut" },
      { key: "date_demande", label: "Date", type: "date" },
    ],
    fields: [
      { name: "code_demande", label: "Code", required: true },
      { name: "id_departement", label: "Departement", type: "select", required: true, resource: "departements", disabledWhen: currentUserIsNotAdmin },
      { name: "id_direction_demandeuse", label: "Direction demandeuse", type: "select", required: true, resource: "directions", disabledWhen: currentUserIsNotAdmin },
      { name: "id_service_destinataire", label: "Service vise", type: "select", resource: "services" },
      { name: "origine_type", label: "Origine", type: "select", options: ["DIRECTION", "DEPARTEMENT", "SERVICE", "MAGASIN"], defaultValue: "DIRECTION", disabledWhen: currentUserIsNotAdmin },
      { name: "origine_id", label: "ID origine", type: "number", disabledWhen: currentUserIsNotAdmin },
      { name: "type_demande", label: "Type", type: "select", required: true, options: ["ACHAT", "REAPPROVISIONNEMENT", "REPARATION", "AUTRE"] },
      { name: "id_materiel", label: "Materiel concerne", type: "select", resource: "materiels", disabledWhen: fieldValueIsNot("type_demande", "REPARATION") },
      { name: "id_consommable", label: "Consommable concerne", type: "select", resource: "consommables", disabledWhen: fieldValueIsNot("type_demande", "REAPPROVISIONNEMENT") },
      { name: "quantite_demandee", label: "Quantite demandee", type: "number", defaultValue: 1, disabledWhen: fieldValueIsNot("type_demande", "REAPPROVISIONNEMENT"), disabledValue: 1 },
      { name: "date_demande", label: "Date", type: "date" },
      { name: "observation", label: "Observation", type: "textarea" },
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
        getPayload: () => {
          const motif = window.prompt("Motif du rejet");
          if (!motif) return null;
          return { motif_rejet: motif };
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
    columns: [
      { key: "titre", label: "Titre" },
      { key: "type_document", label: "Type" },
      { key: "numero_document", label: "Numero" },
      { key: "id_materiel", label: "Materiel" },
      { key: "id_consommable", label: "Consommable" },
    ],
    fields: [
      { name: "titre", label: "Titre", required: true },
      { name: "type_document", label: "Type", type: "select", options: ["FACTURE", "BON_LIVRAISON", "GARANTIE", "FICHE_TECHNIQUE", "PHOTO", "AUTRE"], defaultValue: "AUTRE" },
      { name: "numero_document", label: "Numero" },
      { name: "id_materiel", label: "Materiel", type: "select", resource: "materiels", disabledWhen: fieldHasValue("id_consommable") },
      { name: "id_consommable", label: "Consommable", type: "select", resource: "consommables", disabledWhen: fieldHasValue("id_materiel") },
      { name: "cree_par", label: "Cree par", type: "select", required: true, resource: "users" },
      { name: "chemin_fichier", label: "Chemin fichier" },
      { name: "mime_type", label: "Type MIME" },
      { name: "taille_fichier_octets", label: "Taille octets", type: "number" },
      { name: "observation", label: "Observation", type: "textarea" },
    ],
  },
  users: {
    title: "Utilisateurs",
    description: "Comptes, roles et perimetres.",
    endpoint: "comptes/users/",
    idField: "id_users",
    visibleRoles: adminOnlyRoles,
    writeRoles: adminOnlyWriteRoles,
    columns: [
      { key: "nom_users", label: "Nom" },
      { key: "matricule", label: "Matricule" },
      { key: "email", label: "Email" },
      { key: "id_role", label: "Role" },
      { key: "statut", label: "Actif", type: "boolean" },
    ],
    fields: [
      { name: "nom_users", label: "Nom", required: true },
      { name: "matricule", label: "Matricule", required: true },
      { name: "email", label: "Email", type: "email" },
      { name: "telephone", label: "Telephone" },
      { name: "password", label: "Mot de passe", type: "password", createOnly: true, required: true },
      { name: "id_role", label: "Role", type: "select", required: true, resource: "roles" },
      { name: "scope_type", label: "Perimetre", type: "select", options: ["GENERAL", "DEPARTEMENT", "DIRECTION", "SERVICE", "MAGASIN"], defaultValue: "GENERAL", disabledWhen: selectedRoleIsFixedGeneral, disabledValue: "GENERAL" },
      { name: "id_departement", label: "Departement", type: "select", resource: "departements", disabledWhen: anyRule(selectedRoleIsFixedGeneral, fieldValueIsNot("scope_type", "DEPARTEMENT")) },
      { name: "id_direction", label: "Direction", type: "select", resource: "directions", disabledWhen: anyRule(selectedRoleIsFixedGeneral, fieldValueIsNot("scope_type", "DIRECTION")) },
      { name: "id_service", label: "Service", type: "select", resource: "services", disabledWhen: anyRule(selectedRoleIsFixedGeneral, fieldValueIsNot("scope_type", "SERVICE")) },
      { name: "id_magasin", label: "Magasin", type: "select", resource: "magasins", disabledWhen: anyRule(selectedRoleIsFixedGeneral, fieldValueIsNot("scope_type", "MAGASIN")) },
      { name: "statut", label: "Actif", type: "checkbox", defaultValue: true },
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
