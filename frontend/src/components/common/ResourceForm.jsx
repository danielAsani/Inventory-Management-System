import { Box, Boxes, CircleDot, Droplets, Layers, Package, Ruler, Weight } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createResourceApi } from "../../api/resourceApi";
import { getApiErrorMessage, getFieldError } from "../../utils/apiErrors";
import { buildStatusDateValues, todayDateInputValue } from "../../utils/statusDates";
import styles from "./ResourceForm.module.css";

function shouldDefaultDateToday(field, formMode) {
  if (formMode !== "create" || field.type !== "date") return false;
  if (field.defaultValue !== undefined || field.autoToday === false) return false;
  return ![
    "date_fin",
    "date_retour",
    "garantie_fin",
    "date_fin_prevue",
    "date_fin_reelle",
    "prochaine_date",
  ].includes(field.name);
}

function initialValue(field, item, formMode) {
  if (item && item[field.name] !== undefined && item[field.name] !== null) return item[field.name];
  if (field.defaultValue !== undefined) return field.defaultValue;
  if (shouldDefaultDateToday(field, formMode)) return todayDateInputValue();
  if (field.type === "checkbox") return false;
  return "";
}

function normalizeValue(field, value) {
  if (field.type === "checkbox") return Boolean(value);
  if (field.type === "file") return value;
  if (typeof value === "string" && shouldUppercaseField(field)) return value.toUpperCase();
  if (value === "" && !field.required) return undefined;
  if (field.type === "number" && value !== "") return Number(value);
  return value;
}

function emptyValue(field) {
  if (field.type === "checkbox") return false;
  return "";
}

function isEmpty(value) {
  return value === undefined || value === null || value === "";
}

function fileDisplayName(value) {
  if (!value) return "";
  return value.name || String(value);
}

function shouldUppercaseField(field) {
  return Boolean(field?.uppercase)
    || /^code_/.test(field?.name || "")
    || ["abreviation", "matricule", "rccm", "nif", "symbole"].includes(field?.name);
}

function normalizeInputValue(field, value) {
  if (typeof value === "string" && shouldUppercaseField(field)) return value.toUpperCase();
  return value;
}

function getFieldResource(field, values, options, item, formMode, user) {
  if (typeof field.resource === "function") {
    return field.resource({ values, options, item, mode: formMode, user });
  }
  return field.resource;
}

function fieldOptions(field, values, options, item, formMode, user) {
  const resource = getFieldResource(field, values, options, item, formMode, user);
  const staticOptions = formMode === "create" && field.createOptions ? field.createOptions : field.options;
  const sourceOptions = staticOptions || options[resource] || [];
  const filteredOptions = typeof field.filterOptions === "function"
    ? sourceOptions.filter((option) => field.filterOptions({ option, values, options, item, mode: formMode, user }))
    : sourceOptions;
  if (typeof field.availableWhen !== "function") return filteredOptions;
  return filteredOptions.filter((option) => field.availableWhen({ option, values, options, item, mode: formMode, user }));
}

function articleSearchOptions(options) {
  const materiels = (options.materiels || []).map((option) => {
    const item = option.item || {};
    const label = [
      item.code_materiel,
      [item.marque, item.modele].filter(Boolean).join(" "),
      item.categorie_nom,
      item.famille_nom,
    ].filter(Boolean).join(" - ");
    return { value: `${label || option.label} (materiel:${option.value})`, label: label || option.label };
  });
  const consommables = (options.consommables || []).map((option) => {
    const item = option.item || {};
    const label = [
      item.code_consommable,
      item.nom_consommable,
      item.categorie_nom,
      item.famille_nom,
    ].filter(Boolean).join(" - ");
    return { value: `${label || option.label} (consommable:${option.value})`, label: label || option.label };
  });
  return [...materiels, ...consommables];
}

function fieldIsRequired(field, values, options, item, formMode, user) {
  return Boolean(field.required)
    || Boolean(typeof field.requiredWhen === "function" && field.requiredWhen({ values, options, item, mode: formMode, user }));
}

function fieldBound(field, bound, values, options, item, formMode, user) {
  const value = field?.[bound];
  if (typeof value === "function") return value({ values, options, item, mode: formMode, user });
  return value;
}

function fieldIsHidden(field, values, options, item, formMode, user) {
  return field.type === "hidden"
    || Boolean(typeof field.hiddenWhen === "function" && field.hiddenWhen({ values, options, item, mode: formMode, user }));
}

function optionSearchText(option) {
  const item = option.item || {};
  return [
    option.label,
    item.code_materiel,
    item.numero_serie,
    item.marque,
    item.modele,
    item.categorie_nom,
    item.famille_nom,
    item.code_consommable,
    item.nom_consommable,
    item.unite_nom,
    item.quantite_stock,
    item.etat,
    item.nom_departement,
    item.nom_direction,
    item.nom_famille,
    item.nom_categorie,
    item.code_unite,
    item.nom_unite,
    item.symbole,
  ].filter(Boolean).join(" ").toLowerCase();
}

function firstRecordValue(record, keys) {
  return keys.map((key) => record[key]).find(Boolean);
}

function recordPrimary(option) {
  const record = option.item || {};
  const value = firstRecordValue(record, [
    "code_materiel",
    "code_departement",
    "code_direction",
    "code_famille",
    "code_categorie",
    "code_consommable",
    "code_unite",
    "matricule",
  ]);
  return value ? String(value).toUpperCase() : option.label;
}

function recordSecondary(option) {
  const record = option.item || {};
  return [record.marque, record.modele].filter(Boolean).join(" ")
    || firstRecordValue(record, [
      "nom_departement",
      "nom_direction",
      "nom_famille",
      "nom_categorie",
      "nom_consommable",
      "nom_unite",
      "nom_users",
    ])
    || option.label;
}

function recordMeta(option) {
  const record = option.item || {};
  return [record.famille_nom, record.categorie_nom].filter(Boolean).join(" / ")
    || [record.departement_nom, record.direction_nom].filter(Boolean).join(" / ")
    || record.symbole
    || record.email
    || "";
}

function recordStatus(option) {
  const record = option.item || {};
  const stock = record.quantite_stock !== undefined && record.quantite_stock !== null
    ? `Stock: ${record.quantite_stock}${record.unite_nom ? ` ${record.unite_nom}` : ""}`
    : "";
  return [stock, record.etat].filter(Boolean).join(" - ")
    || (record.statut === false || record.is_active === false ? "Inactif" : "")
    || (record.statut === true || record.is_active === true ? "Actif" : "");
}

function UnitRecordIcon({ record }) {
  const code = String(record.code_unite || record.symbole || "").toUpperCase();
  const Icon = {
    PCS: CircleDot,
    BT: Box,
    PAQ: Boxes,
    M: Ruler,
    RLX: Layers,
    KG: Weight,
    L: Droplets,
  }[code] || Package;

  return (
    <span className={styles.recordIcon} aria-hidden="true">
      <Icon size={20} strokeWidth={1.9} />
    </span>
  );
}

function RecordPicker({ field, value, values, options, item, formMode, user, disabled, required, error, onChange }) {
  const [search, setSearch] = useState("");
  const resourceKey = getFieldResource(field, values, options, item, formMode, user);
  const allOptions = fieldOptions(field, values, options, item, formMode, user);
  const normalizedSearch = search.trim().toLowerCase();
  const filteredOptions = normalizedSearch
    ? allOptions.filter((option) => optionSearchText(option).includes(normalizedSearch))
    : allOptions;

  return (
    <div className={`${styles.field} ${styles.recordPicker} ${disabled ? styles.disabled : ""}`}>
      <span>{field.label}{required ? " *" : ""}</span>
      <input
        type="search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder={field.searchPlaceholder || "Rechercher..."}
        disabled={disabled}
      />
      <div className={styles.recordGrid}>
        {filteredOptions.map((option) => {
          const record = option.item || {};
          const optionValue = String(option.value);
          const selected = String(value) === optionValue;
          return (
            <button
              type="button"
              className={`${styles.recordCard} ${selected ? styles.selectedRecord : ""}`}
              onClick={() => onChange(field.name, option.value)}
              disabled={disabled}
              key={optionValue}
            >
              <div className={styles.recordHeader}>
                {resourceKey === "unites" && <UnitRecordIcon record={record} />}
                <strong>{recordPrimary(option)}</strong>
              </div>
              <span>{recordSecondary(option)}</span>
              <small>{recordMeta(option) || "-"}</small>
              <em>{recordStatus(option) || "Disponible"}</em>
            </button>
          );
        })}
      </div>
      {!filteredOptions.length && <em className={styles.emptyPicker}>{field.emptyText || "Aucun element trouve."}</em>}
      {error && <small>{error}</small>}
    </div>
  );
}

export default function ResourceForm({ config, item, mode, options, user, errors, isSubmitting, onSubmit, onCancel, onOptionCreated }) {
  const navigate = useNavigate();
  const formMode = mode || (item ? "edit" : "create");
  const wizardEnabled = Boolean(config.formSteps?.length);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [quickCreateField, setQuickCreateField] = useState("");
  const [quickCreateError, setQuickCreateError] = useState("");
  const baseFields = useMemo(
    () => config.fields.filter((field) => {
      if (formMode === "edit" && field.createOnly) return false;
      if (formMode === "create" && field.autoGenerated) return false;
      return true;
    }),
    [config.fields, formMode],
  );
  const [values, setValues] = useState(() => Object.fromEntries(baseFields.map((field) => [field.name, initialValue(field, item, formMode)])));
  const visibleFields = useMemo(
    () => baseFields.filter((field) => {
      if (typeof field.visibleWhen === "function") {
        return field.visibleWhen({ values, options, item, mode: formMode, user });
      }
      return true;
    }),
    [baseFields, formMode, item, options, user, values],
  );
  const baseFieldByName = useMemo(() => Object.fromEntries(baseFields.map((field) => [field.name, field])), [baseFields]);
  const fieldByName = useMemo(() => Object.fromEntries(visibleFields.map((field) => [field.name, field])), [visibleFields]);
  const groups = useMemo(() => {
    if (wizardEnabled) {
      return config.formSteps
        .map((step) => ({
          ...step,
          fields: step.fields
            .map((fieldName) => fieldByName[fieldName])
            .filter((field) => field && !fieldIsHidden(field, values, options, item, formMode, user)),
        }))
        .filter((step) => step.fields.length);
    }
    if (config.formGroups?.length) {
      return config.formGroups
        .map((group) => ({
          ...group,
          fields: group.fields
            .map((fieldName) => fieldByName[fieldName])
            .filter((field) => field && !fieldIsHidden(field, values, options, item, formMode, user)),
        }))
        .filter((group) => group.fields.length);
    }
    return [{ title: "Informations", tone: "blue", fields: visibleFields }];
  }, [config.formGroups, config.formSteps, fieldByName, formMode, item, options, user, values, visibleFields, wizardEnabled]);
  const itemKey = item?.[config.idField] ?? "";

  useEffect(() => {
    setActiveStepIndex(0);
  }, [config.idField, formMode, itemKey]);

  useEffect(() => {
    setActiveStepIndex((current) => Math.min(current, Math.max(groups.length - 1, 0)));
  }, [groups.length]);

  const fieldIsDisabled = useCallback((field, currentValues) => {
    if (field.disabled) return true;
    if (typeof field.disabledWhen === "function") {
      return field.disabledWhen({ values: currentValues, options, item, mode: formMode, user });
    }
    return false;
  }, [formMode, item, options, user]);

  const clearDisabledFields = useCallback((currentValues) => {
    const nextValues = { ...currentValues };
    let changed = false;

    visibleFields.forEach((field) => {
      if (!fieldIsDisabled(field, nextValues) || field.clearWhenDisabled === false) return;
      const nextValue = field.disabledValue !== undefined ? field.disabledValue : emptyValue(field);
      if (nextValues[field.name] === nextValue || (field.disabledValue === undefined && isEmpty(nextValues[field.name]))) return;

      nextValues[field.name] = nextValue;
      changed = true;
    });

    return changed ? nextValues : currentValues;
  }, [visibleFields, fieldIsDisabled]);

  useEffect(() => {
    setValues((current) => clearDisabledFields(current));
  }, [clearDisabledFields]);

  const updateValue = (name, value) => {
    setValues((current) => {
      const field = baseFieldByName[name];
      const nextValues = { ...current, [name]: normalizeInputValue(field, value) };
      Object.assign(nextValues, buildStatusDateValues({
        fields: baseFields,
        currentValues: nextValues,
        fieldName: name,
        value: nextValues[name],
      }));
      (field?.clears || []).forEach((fieldName) => {
        nextValues[fieldName] = "";
      });
      return clearDisabledFields(nextValues);
    });
  };

  const createRelatedOption = async (field) => {
    if (!field.quickCreate || quickCreateField) return;
    if (field.quickCreate.navigateTo) {
      navigate(field.quickCreate.navigateTo);
      return;
    }

    const label = field.quickCreate.defaultLabel?.trim();
    if (!label) {
      setQuickCreateError("La creation rapide de cet element n'est pas configuree.");
      return;
    }

    setQuickCreateField(field.name);
    setQuickCreateError("");
    try {
      const api = createResourceApi(field.quickCreate.endpoint);
      const created = await api.create({
        [field.quickCreate.nameField]: label,
        ...(field.quickCreate.defaults || {}),
      });
      const option = {
        value: created[field.quickCreate.idField],
        label: created[field.quickCreate.labelField],
        item: created,
      };
      onOptionCreated?.(field.quickCreate.resourceKey, option);
      updateValue(field.name, option.value);
    } catch (error) {
      setQuickCreateError(getApiErrorMessage(error));
    } finally {
      setQuickCreateField("");
    }
  };

  const updateArticleSearch = (value) => {
    setValues((current) => {
      const nextValues = { ...current, article_search: value, id_materiel: "", id_consommable: "" };
      const match = String(value).match(/\((materiel|consommable):(\d+)\)$/);
      const [, type, id] = match || [];
      if (type === "materiel") nextValues.id_materiel = id;
      if (type === "consommable") nextValues.id_consommable = id;
      return clearDisabledFields(nextValues);
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(
      visibleFields
        .filter((field) => !field.virtual && !fieldIsDisabled(field, values))
        .map((field) => [field.name, normalizeValue(field, values[field.name])])
        .filter(([, value]) => value !== undefined),
    );
    Object.assign(payload, buildStatusDateValues({
      fields: baseFields,
      currentValues: values,
      fieldName: "statut",
      value: values.statut,
    }));
    onSubmit(payload);
  };

  const activeGroup = wizardEnabled ? groups[Math.min(activeStepIndex, Math.max(groups.length - 1, 0))] : null;
  const displayedGroups = wizardEnabled && activeGroup ? [activeGroup] : groups;
  const currentStepIsValid = useMemo(() => {
    if (!wizardEnabled || !activeGroup) return true;
    return activeGroup.fields.every((field) => {
      if (field.virtual && !field.required && typeof field.requiredWhen !== "function") return true;
      if (fieldIsDisabled(field, values)) return true;
      if (!fieldIsRequired(field, values, options, item, formMode, user)) return true;
      return !isEmpty(values[field.name]);
    });
  }, [activeGroup, fieldIsDisabled, formMode, item, options, user, values, wizardEnabled]);

  const goToNextStep = () => {
    if (!currentStepIsValid) return;
    setActiveStepIndex((current) => Math.min(current + 1, groups.length - 1));
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      {quickCreateError && (
        <div className={styles.formError} role="alert">
          {quickCreateError}
        </div>
      )}

      {wizardEnabled && (
        <nav className={styles.stepper} aria-label="Progression du formulaire">
          {groups.map((group, index) => (
            <button
              type="button"
              className={index === activeStepIndex ? styles.activeStep : ""}
              onClick={() => setActiveStepIndex(index)}
              key={group.title}
            >
              <span>{index + 1}</span>
              {group.title}
            </button>
          ))}
        </nav>
      )}

      {displayedGroups.map((group) => (
        <section className={`${styles.group} ${styles[group.tone || "blue"]}`} key={group.title}>
          <h3>{group.title}</h3>
          <div className={styles.grid}>
        {group.fields.map((field) => {
          const error = getFieldError(errors, field.name);
          const value = values[field.name];
          const disabled = fieldIsDisabled(field, values) || isSubmitting;
          const required = field.required || (typeof field.requiredWhen === "function" && field.requiredWhen({ values, options, item, mode: formMode, user }));

          if (fieldIsHidden(field, values, options, item, formMode, user)) return null;

          if (field.type === "checkbox") {
            return (
              <label className={`${styles.checkbox} ${disabled ? styles.disabled : ""}`} key={field.name}>
                <input
                  type="checkbox"
                  checked={Boolean(value)}
                  onChange={(event) => updateValue(field.name, event.target.checked)}
                  disabled={disabled}
                />
                <span>{field.label}</span>
              </label>
            );
          }

          if (field.type === "articleSearch") {
            return (
              <label className={`${styles.field} ${disabled ? styles.disabled : ""}`} key={field.name}>
                <span>{field.label}{required ? " *" : ""}</span>
                <input
                  type="search"
                  list={`${config.idField}-${field.name}-options`}
                  value={value ?? ""}
                  onChange={(event) => updateArticleSearch(event.target.value)}
                  placeholder="Rechercher par code, nom, marque..."
                  required={required && !disabled}
                  disabled={disabled}
                />
                <datalist id={`${config.idField}-${field.name}-options`}>
                  {articleSearchOptions(options).map((option) => (
                    <option value={option.value} key={option.value}>{option.label}</option>
                  ))}
                </datalist>
                {error && <small>{error}</small>}
              </label>
            );
          }

          if (field.type === "recordPicker") {
            return (
              <RecordPicker
                field={field}
                value={value}
                values={values}
                options={options}
                item={item}
                formMode={formMode}
                user={user}
                disabled={disabled}
                required={required}
                error={error}
                onChange={updateValue}
                key={field.name}
              />
            );
          }

          return (
            <label className={`${styles.field} ${disabled ? styles.disabled : ""}`} key={field.name}>
              <span>{field.label}{required ? " *" : ""}</span>
              {field.type === "textarea" ? (
                <textarea
                  value={value ?? ""}
                  onChange={(event) => updateValue(field.name, event.target.value)}
                  rows={3}
                  required={required && !disabled}
                  disabled={disabled}
                />
              ) : field.type === "select" ? (
                <>
                  <select
                    value={value ?? ""}
                    onChange={(event) => updateValue(field.name, event.target.value)}
                    required={required && !disabled}
                    disabled={disabled}
                  >
                    <option value="">{field.noneLabel || "Selectionner..."}</option>
                    {fieldOptions(field, values, options, item, formMode, user).map((option) => {
                      const optionValue = typeof option === "string" ? option : option.value;
                      const label = typeof option === "string" ? option : option.label;
                      return <option value={optionValue} key={optionValue}>{label}</option>;
                    })}
                  </select>
                  {field.quickCreate && !disabled && (
                    <button
                      type="button"
                      className={styles.inlineButton}
                      onClick={() => createRelatedOption(field)}
                      disabled={Boolean(quickCreateField)}
                    >
                      {quickCreateField === field.name ? "Ajout..." : field.quickCreate.label}
                    </button>
                  )}
                </>
              ) : field.type === "file" ? (
                <>
                  <input
                    type="file"
                    accept={field.accept}
                    onChange={(event) => updateValue(field.name, event.target.files?.[0] || "")}
                    required={required && !disabled && !value}
                    disabled={disabled}
                  />
                  {value && <em className={styles.fileName}>{fileDisplayName(value)}</em>}
                </>
              ) : (
                <input
                  type={field.type || "text"}
                  value={value ?? ""}
                  onChange={(event) => updateValue(field.name, event.target.value)}
                  min={fieldBound(field, "min", values, options, item, formMode, user)}
                  max={fieldBound(field, "max", values, options, item, formMode, user)}
                  required={required && !disabled}
                  disabled={disabled}
                />
              )}
              {error && <small>{error}</small>}
            </label>
          );
        })}
          </div>
        </section>
      ))}

      <div className={styles.actions}>
        <button type="button" className={styles.secondary} onClick={onCancel}>Annuler</button>
        {wizardEnabled && activeStepIndex > 0 && (
          <button type="button" className={styles.secondary} onClick={() => setActiveStepIndex((current) => current - 1)}>
            Precedent
          </button>
        )}
        {wizardEnabled && activeStepIndex < groups.length - 1 ? (
          <button type="button" className={styles.primary} onClick={goToNextStep} disabled={isSubmitting || !currentStepIsValid}>
            Suivant
          </button>
        ) : (
          <button type="submit" className={styles.primary} disabled={isSubmitting}>
            {isSubmitting ? "Enregistrement..." : "Enregistrer"}
          </button>
        )}
      </div>
    </form>
  );
}
