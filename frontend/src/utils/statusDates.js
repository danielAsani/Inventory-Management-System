export function todayDateInputValue(date = new Date()) {
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 10);
}

function hasField(fields, fieldName) {
  return fields.some((field) => (field.name || field.key) === fieldName);
}

function currentValue(currentValues, fieldName) {
  return currentValues?.[fieldName];
}

function emptyDatePatch(value, fields, fieldName) {
  if (!hasField(fields, fieldName)) return {};
  return { [fieldName]: value };
}

function datedPatch(fields, currentValues, fieldName) {
  if (!hasField(fields, fieldName)) return {};
  return { [fieldName]: currentValue(currentValues, fieldName) || todayDateInputValue() };
}

export function buildStatusDateValues({ fields = [], currentValues = {}, fieldName, value }) {
  if (fieldName !== "statut") return {};
  const patch = {};

  if (value === "RETOURNEE") {
    Object.assign(patch, datedPatch(fields, currentValues, "date_retour"));
  }
  if (value === "ACTIVE" || value === "ANNULEE") {
    Object.assign(patch, emptyDatePatch(null, fields, "date_retour"));
  }

  if (value === "TERMINE" || value === "ANNULE") {
    Object.assign(patch, datedPatch(fields, currentValues, "date_fin"));
  }
  if (value === "EN_COURS") {
    Object.assign(patch, emptyDatePatch(null, fields, "date_fin"));
    Object.assign(patch, emptyDatePatch(null, fields, "date_fin_reelle"));
  }

  if (value === "TERMINEE") {
    Object.assign(patch, datedPatch(fields, currentValues, "date_fin_reelle"));
  }
  if (["EN_ATTENTE", "ANNULEE", "REJETEE", "EN_ATTENTE_DEPARTEMENT", "EN_TRAITEMENT_MAGASIN"].includes(value)) {
    Object.assign(patch, emptyDatePatch(null, fields, "date_fin_reelle"));
  }

  return patch;
}
