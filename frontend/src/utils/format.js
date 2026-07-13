export function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("fr-CD").format(new Date(value));
}

export function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "0";
  return new Intl.NumberFormat("fr-CD").format(Number(value));
}

export function initials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return (parts[0]?.[0] || "U") + (parts[1]?.[0] || "");
}
