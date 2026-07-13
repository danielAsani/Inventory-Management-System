export function getApiErrorMessage(error) {
  const data = error?.response?.data;

  if (!data) return "Impossible de contacter le serveur.";
  if (typeof data === "string") return data;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
    return data.non_field_errors[0];
  }

  const firstField = Object.keys(data)[0];
  const firstError = firstField ? data[firstField] : null;
  if (Array.isArray(firstError) && firstError.length > 0) return `${firstField}: ${firstError[0]}`;
  if (typeof firstError === "string") return `${firstField}: ${firstError}`;

  return "Une erreur est survenue.";
}

export function getFieldError(errors, fieldName) {
  const value = errors?.[fieldName];
  if (Array.isArray(value)) return value[0];
  if (typeof value === "string") return value;
  return "";
}

export function normalizeFieldErrors(error) {
  const data = error?.response?.data;
  if (!data || typeof data !== "object" || Array.isArray(data)) return {};
  return data;
}
