import { useCallback, useEffect, useMemo, useState } from "react";
import { getFieldError } from "../../utils/apiErrors";
import styles from "./ResourceForm.module.css";

function initialValue(field, item) {
  if (item && item[field.name] !== undefined && item[field.name] !== null) return item[field.name];
  if (field.defaultValue !== undefined) return field.defaultValue;
  if (field.type === "checkbox") return false;
  return "";
}

function normalizeValue(field, value) {
  if (field.type === "checkbox") return Boolean(value);
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

export default function ResourceForm({ config, item, options, user, errors, isSubmitting, onSubmit, onCancel }) {
  const editableFields = useMemo(
    () => config.fields.filter((field) => !(item && field.createOnly)),
    [config.fields, item],
  );
  const [values, setValues] = useState(() => Object.fromEntries(editableFields.map((field) => [field.name, initialValue(field, item)])));

  const fieldIsDisabled = useCallback((field, currentValues) => {
    if (field.disabled) return true;
    if (typeof field.disabledWhen === "function") {
      return field.disabledWhen({ values: currentValues, options, item, user });
    }
    return false;
  }, [item, options, user]);

  const clearDisabledFields = useCallback((currentValues) => {
    const nextValues = { ...currentValues };
    let changed = false;

    editableFields.forEach((field) => {
      if (!fieldIsDisabled(field, nextValues) || field.clearWhenDisabled === false) return;
      const nextValue = field.disabledValue !== undefined ? field.disabledValue : emptyValue(field);
      if (nextValues[field.name] === nextValue || (field.disabledValue === undefined && isEmpty(nextValues[field.name]))) return;

      nextValues[field.name] = nextValue;
      changed = true;
    });

    return changed ? nextValues : currentValues;
  }, [editableFields, fieldIsDisabled]);

  useEffect(() => {
    setValues((current) => clearDisabledFields(current));
  }, [clearDisabledFields]);

  const updateValue = (name, value) => {
    setValues((current) => clearDisabledFields({ ...current, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(
      editableFields
        .filter((field) => !fieldIsDisabled(field, values))
        .map((field) => [field.name, normalizeValue(field, values[field.name])])
        .filter(([, value]) => value !== undefined),
    );
    onSubmit(payload);
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.grid}>
        {editableFields.map((field) => {
          const error = getFieldError(errors, field.name);
          const value = values[field.name];
          const disabled = fieldIsDisabled(field, values) || isSubmitting;

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

          return (
            <label className={`${styles.field} ${disabled ? styles.disabled : ""}`} key={field.name}>
              <span>{field.label}{field.required ? " *" : ""}</span>
              {field.type === "textarea" ? (
                <textarea
                  value={value ?? ""}
                  onChange={(event) => updateValue(field.name, event.target.value)}
                  rows={3}
                  required={field.required && !disabled}
                  disabled={disabled}
                />
              ) : field.type === "select" ? (
                <select
                  value={value ?? ""}
                  onChange={(event) => updateValue(field.name, event.target.value)}
                  required={field.required && !disabled}
                  disabled={disabled}
                >
                  <option value="">Selectionner...</option>
                  {(field.options || options[field.resource] || []).map((option) => {
                    const optionValue = typeof option === "string" ? option : option.value;
                    const label = typeof option === "string" ? option : option.label;
                    return <option value={optionValue} key={optionValue}>{label}</option>;
                  })}
                </select>
              ) : (
                <input
                  type={field.type || "text"}
                  value={value ?? ""}
                  onChange={(event) => updateValue(field.name, event.target.value)}
                  required={field.required && !disabled}
                  disabled={disabled}
                />
              )}
              {error && <small>{error}</small>}
            </label>
          );
        })}
      </div>

      <div className={styles.actions}>
        <button type="button" className={styles.secondary} onClick={onCancel}>Annuler</button>
        <button type="submit" className={styles.primary} disabled={isSubmitting}>
          {isSubmitting ? "Enregistrement..." : "Enregistrer"}
        </button>
      </div>
    </form>
  );
}
