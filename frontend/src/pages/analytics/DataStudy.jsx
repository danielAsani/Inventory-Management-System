import {
  Activity,
  BarChart3,
  Brain,
  CheckCircle2,
  Clock3,
  Database,
  LineChart,
  RefreshCw,
  Search,
  ShieldAlert,
  SlidersHorizontal,
  TrendingUp,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getDataStudySnapshot } from "../../api/dataStudyApi";
import EmptyState from "../../components/common/EmptyState";
import ErrorAlert from "../../components/common/ErrorAlert";
import LoadingState from "../../components/common/LoadingState";
import { getApiErrorMessage } from "../../utils/apiErrors";
import { formatNumber } from "../../utils/format";
import styles from "./DataStudy.module.css";

const HORIZONS = [30, 90, 180, 365, 730];
const FORECAST_MONTHS = 12;
const VIEWS = [
  { key: "overview", label: "Vue globale" },
  { key: "risks", label: "Risques stock" },
  { key: "forecast", label: "Previsions" },
  { key: "audit", label: "Verification" },
  { key: "flow", label: "Flux" },
];
const SCENARIOS = [
  { key: "normal", label: "Normal", multiplier: 1 },
  { key: "tension", label: "Tension +20%", multiplier: 1.2 },
  { key: "hausse", label: "Forte hausse +40%", multiplier: 1.4 },
  { key: "baisse", label: "Baisse -15%", multiplier: 0.85 },
];
const SEVERITIES = [
  { key: "all", label: "Tout" },
  { key: "critique", label: "Critique" },
  { key: "alerte", label: "Alerte" },
  { key: "maintenance", label: "Maintenance" },
  { key: "attente", label: "Attente" },
];
const DEMANDE_LABELS = {
  EN_ATTENTE_DEPARTEMENT: "Attente departement",
  EN_TRAITEMENT_MAGASIN: "Traitement magasin",
  TRAITEE: "Traitee",
  REJETEE: "Rejetee",
  ANNULEE: "Annulee",
};
const AUDIT_CHECKS = {
  stock: [
    "Verifier les stocks sous seuil et les ruptures probables",
    "Comparer la couverture restante avec l'horizon choisi",
    "Confirmer les quantites a recommander avant reapprovisionnement",
  ],
  materiels: [
    "Verifier les materiels sans magasin alors qu'ils sont en stock",
    "Controler les materiels affectes encore rattaches a un magasin",
    "Suivre les materiels en panne ou en reparation",
  ],
  demandes: [
    "Verifier les demandes bloquees dans le workflow",
    "Controler les demandes traitees sans date de finalisation",
    "Completer les demandes rejetees sans motif",
  ],
  mouvements: [
    "Verifier les mouvements avec date future",
    "Controler les entrees/sorties sans magasin source ou destination",
    "Corriger les transferts dont la source egale la destination",
  ],
  maintenance: [
    "Verifier les reparations en retard",
    "Mettre a jour les dossiers ouverts",
    "Prioriser les materiels indisponibles",
  ],
  inventaires: [
    "Verifier les inventaires ouverts depuis longtemps",
    "Cloturer les sessions terminees",
    "Analyser les ecarts avant validation finale",
  ],
  qualite: [
    "Traiter les anomalies critiques en premier",
    "Corriger les doublons et les rattachements manquants",
    "Recalculer l'etude apres correction",
  ],
};

function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function getId(value) {
  if (value && typeof value === "object") {
    return value.id_consommable || value.id_materiel || value.id;
  }
  return value;
}

function dateValue(value) {
  const date = value ? new Date(value) : null;
  return date && !Number.isNaN(date.getTime()) ? date : null;
}

function daysBetween(date, reference = new Date()) {
  const parsed = dateValue(date);
  if (!parsed) return 0;
  return Math.max(0, Math.round((reference - parsed) / 86400000));
}

function monthKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function monthLabel(date) {
  return new Intl.DateTimeFormat("fr-CD", { month: "short", year: "2-digit" }).format(date);
}

function buildPastMonths(size = 12) {
  const now = new Date();
  return Array.from({ length: size }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (size - 1 - index), 1);
    return { key: monthKey(date), label: monthLabel(date), date };
  });
}

function buildFutureMonths(size = FORECAST_MONTHS) {
  const now = new Date();
  return Array.from({ length: size }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() + index + 1, 1);
    return { key: monthKey(date), label: monthLabel(date), date };
  });
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function standardDeviation(values) {
  if (values.length < 2) return 0;
  const mean = average(values);
  const variance = average(values.map((value) => (value - mean) ** 2));
  return Math.sqrt(variance);
}

function trendForecast(values, periods = FORECAST_MONTHS, multiplier = 1) {
  const recent = values.slice(-6);
  const previous = values.slice(-12, -6);
  const base = average(recent.length ? recent : values);
  const monthlyTrend = recent.length && previous.length ? (average(recent) - average(previous)) / 6 : 0;
  return Array.from({ length: periods }, (_, index) => Math.max(0, Math.round((base + monthlyTrend * (index + 1)) * multiplier)));
}

function confidenceFrom(values) {
  const nonZero = values.filter((value) => value > 0);
  if (nonZero.length < 3) return "Faible";
  const mean = average(nonZero);
  const volatility = mean ? standardDeviation(nonZero) / mean : 0;
  if (nonZero.length >= 9 && volatility < 0.45) return "Elevee";
  if (nonZero.length >= 5 && volatility < 0.8) return "Moyenne";
  return "Faible";
}

function countBy(items, field) {
  return items.reduce((acc, item) => {
    const key = item[field] || "NON_RENSEIGNE";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
}

function issue({ title, detail, type = "alerte", domain = "General", action = "Verifier" }) {
  return { title, detail, type, domain, action };
}

function duplicateValues(items, field, label, domain) {
  const occurrences = new Map();
  items.forEach((item) => {
    const value = item[field];
    if (!value) return;
    occurrences.set(value, (occurrences.get(value) || 0) + 1);
  });
  return Array.from(occurrences.entries())
    .filter(([, count]) => count > 1)
    .map(([value, count]) => issue({
      title: `${label} duplique`,
      detail: `${value} apparait ${count} fois`,
      type: "critique",
      domain,
      action: "Fusionner ou corriger le code",
    }));
}

function buildDataIssues({ materiels, consommables, mouvements, demandes, reparations, inventaires }) {
  const now = new Date();
  return [
    ...duplicateValues(materiels, "code_materiel", "Code materiel", "Materiels"),
    ...duplicateValues(consommables, "code_consommable", "Code consommable", "Stock"),
    ...duplicateValues(demandes, "code_demande", "Code demande", "Demandes"),
    ...consommables
      .filter((item) => toNumber(item.quantite_stock) < 0)
      .map((item) => issue({ title: item.nom_consommable || item.code_consommable, detail: "Stock negatif", type: "critique", domain: "Stock", action: "Corriger par mouvement d'ajustement" })),
    ...consommables
      .filter((item) => toNumber(item.seuil_alerte) <= 0)
      .map((item) => issue({ title: item.nom_consommable || item.code_consommable, detail: "Seuil d'alerte non renseigne", domain: "Stock", action: "Definir un seuil minimum" })),
    ...materiels
      .filter((item) => item.etat === "AFFECTE" && item.id_magasin)
      .map((item) => issue({ title: item.code_materiel, detail: "Materiel affecte encore lie a un magasin", type: "alerte", domain: "Materiels", action: "Verifier affectation et magasin" })),
    ...materiels
      .filter((item) => item.etat === "EN_STOCK" && !item.id_magasin)
      .map((item) => issue({ title: item.code_materiel, detail: "Materiel en stock sans magasin", type: "alerte", domain: "Materiels", action: "Rattacher au magasin reel" })),
    ...materiels
      .filter((item) => ["EN_PANNE", "EN_REPARATION"].includes(item.etat))
      .map((item) => issue({ title: item.code_materiel, detail: `Etat ${item.etat}`, type: "maintenance", domain: "Materiels", action: "Verifier le dossier maintenance" })),
    ...demandes
      .filter((item) => !item.id_departement || !item.id_direction_demandeuse)
      .map((item) => issue({ title: item.code_demande || `Demande ${item.id_demande}`, detail: "Departement ou direction manquant", type: "critique", domain: "Demandes", action: "Completer le rattachement" })),
    ...demandes
      .filter((item) => item.statut === "TRAITEE" && !item.date_finalisation)
      .map((item) => issue({ title: item.code_demande || `Demande ${item.id_demande}`, detail: "Traitee sans date de finalisation", type: "alerte", domain: "Demandes", action: "Renseigner la finalisation" })),
    ...demandes
      .filter((item) => item.statut === "REJETEE" && !item.motif_rejet)
      .map((item) => issue({ title: item.code_demande || `Demande ${item.id_demande}`, detail: "Rejetee sans motif", type: "alerte", domain: "Demandes", action: "Ajouter le motif" })),
    ...demandes
      .filter((item) => ["EN_ATTENTE_DEPARTEMENT", "EN_TRAITEMENT_MAGASIN"].includes(item.statut) && daysBetween(item.date_demande, now) >= 14)
      .map((item) => issue({ title: item.code_demande || `Demande ${item.id_demande}`, detail: `Bloquee depuis ${daysBetween(item.date_demande, now)} jours`, type: "attente", domain: "Demandes", action: "Relancer le validateur" })),
    ...mouvements
      .filter((item) => dateValue(item.date_mouvement) > now)
      .map((item) => issue({ title: `Mouvement ${item.id_mouvement}`, detail: "Date de mouvement future", type: "critique", domain: "Mouvements", action: "Corriger la date" })),
    ...mouvements
      .filter((item) => toNumber(item.quantite) <= 0)
      .map((item) => issue({ title: `Mouvement ${item.id_mouvement}`, detail: "Quantite nulle ou negative", type: "critique", domain: "Mouvements", action: "Verifier la saisie" })),
    ...mouvements
      .filter((item) => item.type_mouvement === "ENTREE" && !item.magasin_destination)
      .map((item) => issue({ title: `Mouvement ${item.id_mouvement}`, detail: "Entree sans magasin destination", type: "critique", domain: "Mouvements", action: "Renseigner destination" })),
    ...mouvements
      .filter((item) => item.type_mouvement === "SORTIE" && !item.magasin_source)
      .map((item) => issue({ title: `Mouvement ${item.id_mouvement}`, detail: "Sortie sans magasin source", type: "critique", domain: "Mouvements", action: "Renseigner source" })),
    ...mouvements
      .filter((item) => item.type_mouvement === "TRANSFERT" && item.magasin_source && item.magasin_source === item.magasin_destination)
      .map((item) => issue({ title: `Mouvement ${item.id_mouvement}`, detail: "Transfert source = destination", type: "critique", domain: "Mouvements", action: "Corriger le transfert" })),
    ...inventaires
      .filter((item) => item.statut === "EN_COURS" && daysBetween(item.date_debut, now) >= 30)
      .map((item) => issue({ title: item.code_inventaire || `Inventaire ${item.id_inventaire}`, detail: `Inventaire ouvert depuis ${daysBetween(item.date_debut, now)} jours`, type: "attente", domain: "Inventaires", action: "Cloturer ou annuler" })),
    ...reparations
      .filter((item) => ["EN_ATTENTE", "EN_COURS"].includes(item.statut) && item.date_fin_prevue && dateValue(item.date_fin_prevue) < now)
      .map((item) => issue({ title: `Reparation ${item.id_reparation}`, detail: "Date de fin prevue depassee", type: "maintenance", domain: "Maintenance", action: "Mettre a jour la reparation" })),
  ];
}

function buildAuditGroups({ dataIssues, stockRisk, openDemandes, inventaires, reparations }) {
  const now = new Date();
  const domainIssues = (domain) => dataIssues.filter((item) => item.domain === domain);
  const typeIssues = (type) => dataIssues.filter((item) => item.type === type);
  const statusFor = (items, fallback = "OK") => {
    if (items.some((item) => item.type === "critique")) return "Critique";
    if (items.length) return fallback;
    return "OK";
  };
  const stockItems = [
    ...stockRisk
      .filter((item) => item.level !== "stable")
      .map((item) => issue({
        title: item.name,
        detail: item.daysRemaining === null ? "Stock sous seuil" : `${item.daysRemaining} jours de couverture`,
        type: item.level === "critique" ? "critique" : "alerte",
        domain: "Stock",
        action: item.recommendedOrder ? `Prevoir ${formatNumber(item.recommendedOrder)} unite(s)` : "Verifier le seuil",
      })),
    ...domainIssues("Stock"),
  ];
  const demandeItems = [
    ...domainIssues("Demandes"),
    ...openDemandes.map((item) => issue({
      title: item.code_demande || `Demande ${item.id_demande}`,
      detail: `${DEMANDE_LABELS[item.statut] || item.statut} depuis ${daysBetween(item.date_demande, now)} jours`,
      type: daysBetween(item.date_demande, now) >= 14 ? "attente" : "alerte",
      domain: "Demandes",
      action: "Verifier l'etape actuelle du workflow",
    })),
  ];
  const maintenanceItems = [
    ...domainIssues("Maintenance"),
    ...reparations
      .filter((item) => ["EN_ATTENTE", "EN_COURS"].includes(item.statut))
      .map((item) => issue({
        title: `Reparation ${item.id_reparation}`,
        detail: item.date_fin_prevue ? `Fin prevue ${item.date_fin_prevue}` : "Reparation ouverte sans date de fin prevue",
        type: "maintenance",
        domain: "Maintenance",
        action: "Mettre a jour ou finaliser le dossier",
      })),
  ];
  const inventaireItems = [
    ...domainIssues("Inventaires"),
    ...inventaires
      .filter((item) => item.statut === "EN_COURS")
      .map((item) => issue({
        title: item.code_inventaire || `Inventaire ${item.id_inventaire}`,
        detail: `Session ouverte depuis ${daysBetween(item.date_debut, now)} jours`,
        type: daysBetween(item.date_debut, now) >= 30 ? "attente" : "alerte",
        domain: "Inventaires",
        action: "Verifier l'avancement et cloturer si termine",
      })),
  ];
  const groups = {
    stock: stockItems,
    materiels: domainIssues("Materiels"),
    demandes: demandeItems,
    mouvements: domainIssues("Mouvements"),
    maintenance: maintenanceItems,
    inventaires: inventaireItems,
    qualite: typeIssues("critique"),
  };
  return [
    { key: "stock", label: "Stock", value: groups.stock.length, detail: "Seuils, ruptures, quantites", status: statusFor(groups.stock), checks: AUDIT_CHECKS.stock, items: groups.stock },
    { key: "materiels", label: "Materiels", value: groups.materiels.length, detail: "Etats, magasin, doublons", status: statusFor(groups.materiels), checks: AUDIT_CHECKS.materiels, items: groups.materiels },
    { key: "demandes", label: "Demandes", value: groups.demandes.length, detail: "Workflow, retards, finalisation", status: statusFor(groups.demandes, "En cours"), checks: AUDIT_CHECKS.demandes, items: groups.demandes },
    { key: "mouvements", label: "Mouvements", value: groups.mouvements.length, detail: "Dates, sources, destinations", status: statusFor(groups.mouvements), checks: AUDIT_CHECKS.mouvements, items: groups.mouvements },
    { key: "maintenance", label: "Maintenance", value: groups.maintenance.length, detail: "Reparations et delais", status: statusFor(groups.maintenance), checks: AUDIT_CHECKS.maintenance, items: groups.maintenance },
    { key: "inventaires", label: "Inventaires", value: groups.inventaires.length, detail: "Sessions ouvertes", status: statusFor(groups.inventaires, "En cours"), checks: AUDIT_CHECKS.inventaires, items: groups.inventaires },
    { key: "qualite", label: "Qualite globale", value: groups.qualite.length, detail: "Critiques bloquants", status: statusFor(groups.qualite, "Critique"), checks: AUDIT_CHECKS.qualite, items: groups.qualite },
  ];
}

function normalizeText(value) {
  return String(value || "").toLowerCase();
}

function buildAnalysis(snapshot, horizon, scenarioMultiplier) {
  const materiels = snapshot.materiels || [];
  const consommables = snapshot.consommables || [];
  const mouvements = snapshot.mouvements || [];
  const consommations = snapshot.consommations || [];
  const demandes = snapshot.demandes || [];
  const inventaires = snapshot.inventaires || [];
  const entretiens = snapshot.entretiens || [];
  const reparations = snapshot.reparations || [];
  const months = buildPastMonths(12);
  const futureMonths = buildFutureMonths();
  const monthIndex = new Map(months.map((month, index) => [month.key, index]));
  const monthlySeries = months.map((month) => ({ ...month, entrees: 0, sorties: 0, consommations: 0, demandes: 0 }));
  const referenceDate = new Date();
  const oneYearAgo = new Date();
  const ninetyDaysAgo = new Date();
  const oneEightyDaysAgo = new Date();
  oneYearAgo.setDate(oneYearAgo.getDate() - 365);
  ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
  oneEightyDaysAgo.setDate(oneEightyDaysAgo.getDate() - 180);

  mouvements.forEach((movement) => {
    const date = dateValue(movement.date_mouvement);
    const index = date ? monthIndex.get(monthKey(date)) : undefined;
    if (index === undefined) return;
    if (movement.type_mouvement === "ENTREE") monthlySeries[index].entrees += toNumber(movement.quantite);
    if (movement.type_mouvement === "SORTIE") monthlySeries[index].sorties += toNumber(movement.quantite);
  });

  demandes.forEach((demande) => {
    const date = dateValue(demande.date_demande);
    const index = date ? monthIndex.get(monthKey(date)) : undefined;
    if (index !== undefined) monthlySeries[index].demandes += 1;
  });

  const consumptionByItem = new Map();
  const monthlyConsumptionByItem = new Map();
  consommations.forEach((consommation) => {
    const date = dateValue(consommation.date_consommation);
    const quantity = toNumber(consommation.quantite);
    const id = getId(consommation.id_consommable);
    const index = date ? monthIndex.get(monthKey(date)) : undefined;
    if (index !== undefined) monthlySeries[index].consommations += quantity;
    if (!date || !id) return;

    const stats = consumptionByItem.get(id) || { year: 0, recent90: 0, previous90: 0 };
    if (date >= oneYearAgo) stats.year += quantity;
    if (date >= ninetyDaysAgo) stats.recent90 += quantity;
    if (date >= oneEightyDaysAgo && date < ninetyDaysAgo) stats.previous90 += quantity;
    consumptionByItem.set(id, stats);

    const series = monthlyConsumptionByItem.get(id) || Array.from({ length: 12 }, () => 0);
    if (index !== undefined) series[index] += quantity;
    monthlyConsumptionByItem.set(id, series);
  });

  const totalStock = consommables.reduce((sum, item) => sum + toNumber(item.quantite_stock), 0);
  const totalConsumptionYear = Array.from(consumptionByItem.values()).reduce((sum, value) => sum + value.year, 0);
  const avgDailyConsumption = (totalConsumptionYear / 365) * scenarioMultiplier;
  const demandeStatus = countBy(demandes, "statut");
  const materielStatus = countBy(materiels, "etat");
  const openDemandes = demandes.filter((demande) => ["EN_ATTENTE_DEPARTEMENT", "EN_TRAITEMENT_MAGASIN"].includes(demande.statut));
  const serviceRate = demandes.length ? Math.round((toNumber(demandeStatus.TRAITEE) / demandes.length) * 100) : 0;

  const stockRisk = consommables
    .map((item) => {
      const id = getId(item.id_consommable);
      const stock = toNumber(item.quantite_stock);
      const threshold = toNumber(item.seuil_alerte);
      const stats = consumptionByItem.get(id) || { year: 0, recent90: 0, previous90: 0 };
      const yearDaily = (stats.year / 365) * scenarioMultiplier;
      const recentDaily = (stats.recent90 / 90) * scenarioMultiplier;
      const previousDaily = stats.previous90 / 90;
      const dailyConsumption = Math.max(yearDaily, recentDaily ? recentDaily * 0.65 + yearDaily * 0.35 : yearDaily);
      const trend = previousDaily ? Math.round(((recentDaily / scenarioMultiplier - previousDaily) / previousDaily) * 100) : 0;
      const daysRemaining = dailyConsumption > 0 ? Math.floor(stock / dailyConsumption) : null;
      const forecastNeed = Math.ceil(dailyConsumption * horizon);
      const recommendedOrder = Math.max(0, forecastNeed + threshold - stock);
      const monthlyValues = monthlyConsumptionByItem.get(id) || [];
      let level = "stable";
      if (threshold > 0 && stock <= threshold) level = "alerte";
      if (daysRemaining !== null && daysRemaining <= horizon) level = "critique";
      return {
        id,
        name: item.nom_consommable || item.code_consommable || `Consommable ${id}`,
        code: item.code_consommable,
        stock,
        threshold,
        dailyConsumption,
        daysRemaining,
        forecastNeed,
        recommendedOrder,
        trend,
        confidence: confidenceFrom(monthlyValues),
        level,
      };
    })
    .sort((a, b) => (a.daysRemaining ?? 99999) - (b.daysRemaining ?? 99999));

  const monthlyConsumptionValues = monthlySeries.map((item) => item.consommations);
  const monthlyDemandValues = monthlySeries.map((item) => item.demandes);
  const consumptionForecast = trendForecast(monthlyConsumptionValues, FORECAST_MONTHS, scenarioMultiplier);
  const demandForecast = trendForecast(monthlyDemandValues, FORECAST_MONTHS, scenarioMultiplier);
  const dataIssues = buildDataIssues({ materiels, consommables, mouvements, demandes, reparations, inventaires });
  const auditGroups = buildAuditGroups({ dataIssues, stockRisk, openDemandes, inventaires, reparations });

  const anomalies = [
    ...stockRisk
      .filter((item) => item.level !== "stable")
      .slice(0, 8)
      .map((item) => issue({
        title: item.name,
        detail: item.daysRemaining === null ? "Sous le seuil d'alerte" : `${item.daysRemaining} jours de couverture`,
        type: item.level,
        domain: "Stock",
        action: item.recommendedOrder ? `Commander ${formatNumber(item.recommendedOrder)}` : "Verifier le seuil",
      })),
    ...openDemandes
      .filter((demande) => daysBetween(demande.date_demande, referenceDate) >= 7)
      .map((demande) => issue({
        title: demande.code_demande || `Demande ${demande.id_demande}`,
        detail: `${DEMANDE_LABELS[demande.statut] || demande.statut} depuis ${daysBetween(demande.date_demande, referenceDate)} jours`,
        type: "attente",
        domain: "Demandes",
        action: "Relancer le flux",
      })),
    ...dataIssues,
  ];
  const criticalCount = anomalies.filter((item) => item.type === "critique").length;
  const qualityScore = Math.max(0, Math.min(100, 100 - criticalCount * 5 - dataIssues.filter((item) => item.type !== "critique").length * 2));

  return {
    metrics: [
      { label: "Score qualite", value: `${qualityScore}%`, detail: "Audit global", icon: CheckCircle2, tone: qualityScore >= 80 ? "green" : "amber" },
      { label: "Risque rupture", value: stockRisk.filter((item) => item.level === "critique").length, detail: `${horizon} prochains jours`, icon: TriangleAlert, tone: "red" },
      { label: "Incoherences", value: dataIssues.length, detail: "Verification complete", icon: Database, tone: "amber" },
      { label: "Taux traite", value: `${serviceRate}%`, detail: "Historique demandes", icon: TrendingUp, tone: "blue" },
    ],
    totals: {
      materiels: materiels.length,
      consommables: consommables.length,
      mouvements: mouvements.length,
      consommations: consommations.length,
      demandes: demandes.length,
      stock: totalStock,
    },
    monthlySeries,
    demandeStatus,
    materielStatus,
    stockRisk,
    anomalies,
    dataIssues,
    auditGroups,
    forecastMonths: futureMonths.map((month, index) => ({
      ...month,
      consommations: consumptionForecast[index],
      demandes: demandForecast[index],
    })),
    forecast: {
      horizon,
      need: Math.ceil(avgDailyConsumption * horizon),
      daily: avgDailyConsumption,
      confidence: confidenceFrom(monthlyConsumptionValues),
      annualNeed: consumptionForecast.reduce((sum, value) => sum + value, 0),
      annualDemandes: demandForecast.reduce((sum, value) => sum + value, 0),
      inventairesOuverts: inventaires.filter((item) => item.statut === "EN_COURS").length,
      maintenancesOuvertes: entretiens.filter((item) => ["PLANIFIE", "EN_COURS"].includes(item.statut)).length + reparations.filter((item) => ["EN_ATTENTE", "EN_COURS"].includes(item.statut)).length,
    },
  };
}

function matchesFilters(item, query, severity) {
  const matchesSeverity = severity === "all" || item.type === severity || item.level === severity;
  const haystack = normalizeText(`${item.title || ""} ${item.detail || ""} ${item.name || ""} ${item.code || ""} ${item.domain || ""}`);
  return matchesSeverity && (!query || haystack.includes(normalizeText(query)));
}

export default function DataStudy() {
  const [snapshot, setSnapshot] = useState(null);
  const [horizon, setHorizon] = useState(365);
  const [scenarioKey, setScenarioKey] = useState("normal");
  const [activeView, setActiveView] = useState("overview");
  const [selectedAuditKey, setSelectedAuditKey] = useState("stock");
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const scenario = SCENARIOS.find((item) => item.key === scenarioKey) || SCENARIOS[0];

  const loadSnapshot = async () => {
    setIsLoading(true);
    setError("");
    try {
      setSnapshot(await getDataStudySnapshot());
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSnapshot();
  }, []);

  const analysis = useMemo(() => (snapshot ? buildAnalysis(snapshot, horizon, scenario.multiplier) : null), [snapshot, horizon, scenario.multiplier]);
  const filteredIssues = useMemo(() => (analysis ? analysis.anomalies.filter((item) => matchesFilters(item, query, severity)) : []), [analysis, query, severity]);
  const filteredStock = useMemo(() => (analysis ? analysis.stockRisk.filter((item) => matchesFilters(item, query, severity)).slice(0, 30) : []), [analysis, query, severity]);
  const selectedAuditGroup = useMemo(
    () => analysis?.auditGroups.find((group) => group.key === selectedAuditKey) || analysis?.auditGroups[0],
    [analysis, selectedAuditKey],
  );

  if (isLoading) return <LoadingState label="Analyse des donnees..." />;

  return (
    <div className={styles.studyPage}>
      <section className={styles.commandCenter}>
        <div className={styles.commandText}>
          <span><Brain size={16} /> Etude donnees</span>
          <h1>Poste analytique magasinier</h1>
          <p>Stocks, demandes, consommations, incoherences, previsions et besoins de reapprovisionnement.</p>
        </div>
        <button type="button" className={styles.refreshButton} onClick={loadSnapshot}><RefreshCw size={17} /> Recalculer</button>
      </section>

      <ErrorAlert message={error} onRetry={loadSnapshot} />

      {analysis ? (
        <>
          <section className={styles.controlPanel} aria-label="Pilotage analytique">
            <div className={styles.viewTabs}>
              {VIEWS.map((view) => (
                <button key={view.key} type="button" className={activeView === view.key ? styles.activeTab : ""} onClick={() => setActiveView(view.key)}>
                  {view.label}
                </button>
              ))}
            </div>
            <label className={styles.searchBox}>
              <Search size={16} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher code, statut, anomalie..." />
            </label>
            <div className={styles.filterGroup}>
              <SlidersHorizontal size={16} />
              <select value={severity} onChange={(event) => setSeverity(event.target.value)}>
                {SEVERITIES.map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}
              </select>
              <select value={scenarioKey} onChange={(event) => setScenarioKey(event.target.value)}>
                {SCENARIOS.map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}
              </select>
            </div>
            <div className={styles.horizonControl} aria-label="Horizon de prevision">
              {HORIZONS.map((value) => (
                <button key={value} type="button" className={horizon === value ? styles.activeHorizon : ""} onClick={() => setHorizon(value)}>
                  {value >= 365 ? `${Math.round(value / 365)} an${value > 365 ? "s" : ""}` : `${value} j`}
                </button>
              ))}
            </div>
          </section>

          <section className={styles.metrics} aria-label="Indicateurs analytiques">
            {analysis.metrics.map(({ label, value, detail, icon: Icon, tone }) => (
              <article className={`${styles.metricCard} ${styles[tone]}`} key={label}>
                <div className={styles.metricHeader}><Icon size={19} /><span>{detail}</span></div>
                <strong>{typeof value === "number" ? formatNumber(value) : value}</strong>
                <p>{label}</p>
              </article>
            ))}
          </section>

          {activeView === "overview" && (
            <>
              <section className={styles.auditStrip}>
                {analysis.auditGroups.map((group) => (
                  <button
                    type="button"
                    key={group.key}
                    className={`${styles.auditCard} ${selectedAuditKey === group.key ? styles.activeAuditCard : ""}`}
                    onClick={() => {
                      setSelectedAuditKey(group.key);
                      setActiveView("audit");
                    }}
                  >
                    <strong>{formatNumber(group.value)}</strong>
                    <span>{group.label}</span>
                    <p>{group.detail}</p>
                    <em className={group.status === "OK" ? styles.okStatus : styles.warnStatus}>{group.status}</em>
                  </button>
                ))}
              </section>
              <section className={styles.analysisGrid}>
                <TrendPanel analysis={analysis} />
                <ProjectionPanel analysis={analysis} />
              </section>
            </>
          )}

          {activeView === "risks" && (
            <section className={styles.panel}>
              <div className={styles.panelHeader}><div><h2>Risque et reapprovisionnement</h2><p>{filteredStock.length} lignes selon les filtres actifs</p></div><ShieldAlert size={20} /></div>
              <StockRiskTable rows={filteredStock} />
            </section>
          )}

          {activeView === "forecast" && (
            <section className={styles.analysisGrid}>
              <ForecastPanel analysis={analysis} />
              <ProjectionPanel analysis={analysis} />
            </section>
          )}

          {activeView === "audit" && (
            <section className={styles.analysisGrid}>
              <article className={styles.panel}>
                <div className={styles.panelHeader}><div><h2>Verification complete</h2><p>{filteredIssues.length} signaux selon les filtres actifs</p></div><Database size={20} /></div>
                <IssueList items={filteredIssues} />
              </article>
              <article className={styles.panel}>
                <div className={styles.panelHeader}><div><h2>Domaines controles</h2><p>Couverture des controles</p></div><CheckCircle2 size={20} /></div>
                <div className={styles.auditList}>
                  {analysis.auditGroups.map((group) => (
                    <button
                      type="button"
                      key={group.key}
                      className={`${styles.auditRow} ${selectedAuditKey === group.key ? styles.activeAuditRow : ""}`}
                      onClick={() => setSelectedAuditKey(group.key)}
                    >
                      <div><strong>{group.label}</strong><span>{group.detail}</span></div>
                      <em className={group.status === "OK" ? styles.okStatus : styles.warnStatus}>{group.status}</em>
                      <b>{formatNumber(group.value)}</b>
                    </button>
                  ))}
                </div>
                <AuditDetailPanel group={selectedAuditGroup} />
              </article>
            </section>
          )}

          {activeView === "flow" && (
            <section className={styles.splitPanel}>
              <DemandPanel analysis={analysis} />
              <MaterialPanel analysis={analysis} />
            </section>
          )}
        </>
      ) : (
        <EmptyState title="Analyse indisponible" description="Aucune donnee exploitable n'a ete retournee." />
      )}
    </div>
  );
}

function AuditDetailPanel({ group }) {
  if (!group) return null;
  return (
    <div className={styles.auditDetail}>
      <header>
        <div>
          <span>Controle selectionne</span>
          <h3>{group.label}</h3>
          <p>{group.detail}</p>
        </div>
        <strong>{formatNumber(group.value)}</strong>
      </header>

      <div className={styles.checkList}>
        {group.checks.map((check) => (
          <div key={check}>
            <CheckCircle2 size={15} />
            <span>{check}</span>
          </div>
        ))}
      </div>

      <div className={styles.auditDetailIssues}>
        <h4>Elements a verifier</h4>
        {group.items.length ? (
          group.items.slice(0, 8).map((item) => (
            <div className={`${styles.auditIssue} ${styles[item.type]}`} key={`${group.key}-${item.title}-${item.detail}`}>
              <div>
                <strong>{item.title}</strong>
                <span>{item.detail}</span>
              </div>
              <em>{item.action}</em>
            </div>
          ))
        ) : (
          <p>Aucun element bloquant detecte pour ce domaine.</p>
        )}
      </div>
    </div>
  );
}

function TrendPanel({ analysis }) {
  return (
    <article className={styles.panel}>
      <div className={styles.panelHeader}><div><h2>Tendances 12 mois</h2><p>Flux stock, consommations et demandes</p></div><LineChart size={20} /></div>
      <div className={styles.trendChart}>
        {analysis.monthlySeries.map((month) => {
          const max = Math.max(1, ...analysis.monthlySeries.flatMap((item) => [item.entrees, item.sorties, item.consommations, item.demandes]));
          return (
            <div className={styles.monthGroup} key={month.key}>
              <div className={styles.bars}>
                <span className={styles.entryBar} style={{ height: `${Math.max(8, (month.entrees / max) * 100)}%` }} title={`Entrees ${month.entrees}`} />
                <span className={styles.exitBar} style={{ height: `${Math.max(8, (month.sorties / max) * 100)}%` }} title={`Sorties ${month.sorties}`} />
                <span className={styles.useBar} style={{ height: `${Math.max(8, (month.consommations / max) * 100)}%` }} title={`Consommations ${month.consommations}`} />
                <span className={styles.askBar} style={{ height: `${Math.max(8, (month.demandes / max) * 100)}%` }} title={`Demandes ${month.demandes}`} />
              </div>
              <span>{month.label}</span>
            </div>
          );
        })}
      </div>
      <div className={styles.legend}><span><i className={styles.entryDot} />Entrees</span><span><i className={styles.exitDot} />Sorties</span><span><i className={styles.useDot} />Conso.</span><span><i className={styles.askDot} />Demandes</span></div>
    </article>
  );
}

function ProjectionPanel({ analysis }) {
  return (
    <article className={styles.panel}>
      <div className={styles.panelHeader}><div><h2>Projection magasin</h2><p>Horizon {analysis.forecast.horizon} jours</p></div><Activity size={20} /></div>
      <div className={styles.forecastGrid}>
        <div><span>Besoin horizon</span><strong>{formatNumber(analysis.forecast.need)}</strong></div>
        <div><span>Besoin 12 mois</span><strong>{formatNumber(analysis.forecast.annualNeed)}</strong></div>
        <div><span>Demandes 12 mois</span><strong>{formatNumber(analysis.forecast.annualDemandes)}</strong></div>
        <div><span>Confiance modele</span><strong>{analysis.forecast.confidence}</strong></div>
        <div><span>Inventaires ouverts</span><strong>{formatNumber(analysis.forecast.inventairesOuverts)}</strong></div>
        <div><span>Maintenances ouvertes</span><strong>{formatNumber(analysis.forecast.maintenancesOuvertes)}</strong></div>
      </div>
    </article>
  );
}

function StockRiskTable({ rows }) {
  if (!rows.length) return <EmptyState title="Aucun resultat" description="Aucun stock ne correspond aux filtres actifs." />;
  return (
    <div className={styles.tableWrap}>
      <table className={styles.dataTable}>
        <thead><tr><th>Consommable</th><th>Stock</th><th>Couverture</th><th>Tendance</th><th>Besoin</th><th>A commander</th><th>Confiance</th><th>Statut</th></tr></thead>
        <tbody>
          {rows.map((item) => (
            <tr key={item.id || item.name}>
              <td>{item.name}</td>
              <td>{formatNumber(item.stock)}</td>
              <td>{item.daysRemaining === null ? "Stable" : `${formatNumber(item.daysRemaining)} j`}</td>
              <td>{item.trend > 0 ? `+${item.trend}%` : `${item.trend}%`}</td>
              <td>{formatNumber(item.forecastNeed)}</td>
              <td>{formatNumber(item.recommendedOrder)}</td>
              <td>{item.confidence}</td>
              <td><span className={`${styles.statusPill} ${styles[item.level]}`}>{item.level}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function IssueList({ items }) {
  if (!items.length) return <EmptyState title="Aucun signal" description="Aucun controle ne correspond aux filtres actifs." />;
  return (
    <div className={styles.issueTable}>
      {items.map((item) => (
        <div className={`${styles.issueRow} ${styles[item.type]}`} key={`${item.domain}-${item.title}-${item.detail}`}>
          <span>{item.domain}</span>
          <strong>{item.title}</strong>
          <p>{item.detail}</p>
          <em>{item.action}</em>
        </div>
      ))}
    </div>
  );
}

function ForecastPanel({ analysis }) {
  return (
    <article className={styles.panel}>
      <div className={styles.panelHeader}><div><h2>Prevision 12 mois</h2><p>Consommations et demandes attendues</p></div><BarChart3 size={20} /></div>
      <div className={styles.forecastTimeline}>
        {analysis.forecastMonths.map((month) => {
          const max = Math.max(1, ...analysis.forecastMonths.flatMap((item) => [item.consommations, item.demandes]));
          return (
            <div className={styles.forecastRow} key={month.key}>
              <span>{month.label}</span>
              <i><span className={styles.useBar} style={{ width: `${Math.max(4, (month.consommations / max) * 100)}%` }} /></i>
              <strong>{formatNumber(month.consommations)}</strong>
              <i><span className={styles.askBar} style={{ width: `${Math.max(4, (month.demandes / max) * 100)}%` }} /></i>
              <strong>{formatNumber(month.demandes)}</strong>
            </div>
          );
        })}
      </div>
    </article>
  );
}

function DemandPanel({ analysis }) {
  return (
    <article className={styles.panel}>
      <div className={styles.panelHeader}><div><h2>File demandes</h2><p>Repartition par statut</p></div><Clock3 size={20} /></div>
      <div className={styles.funnel}>
        {Object.entries(DEMANDE_LABELS).map(([status, label]) => {
          const value = analysis.demandeStatus[status] || 0;
          const total = Object.values(analysis.demandeStatus).reduce((sum, count) => sum + count, 0) || 1;
          return (
            <div className={styles.funnelRow} key={status}>
              <div><strong>{label}</strong><span>{formatNumber(value)}</span></div>
              <i><span style={{ width: `${Math.max(4, (value / total) * 100)}%` }} /></i>
            </div>
          );
        })}
      </div>
    </article>
  );
}

function MaterialPanel({ analysis }) {
  return (
    <article className={styles.panel}>
      <div className={styles.panelHeader}><div><h2>Etat materiels</h2><p>Lecture operationnelle</p></div><Database size={20} /></div>
      <div className={styles.stateGrid}>
        {Object.entries(analysis.materielStatus).map(([state, count]) => (
          <div key={state}><span>{state.replaceAll("_", " ")}</span><strong>{formatNumber(count)}</strong></div>
        ))}
      </div>
    </article>
  );
}
