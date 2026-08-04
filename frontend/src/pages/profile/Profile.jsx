import { useState } from "react";
import { KeyRound, Save } from "lucide-react";
import { changePassword } from "../../api/authApi";
import { useAuth } from "../../hooks/useAuth";
import { getApiErrorMessage } from "../../utils/apiErrors";
import { roleLabel } from "../../utils/permissions";
import styles from "./Profile.module.css";

const initialForm = {
  current_password: "",
  new_password: "",
  confirm_password: "",
};

export default function Profile() {
  const { user } = useAuth();
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const updateField = (fieldName, value) => {
    setForm((current) => ({ ...current, [fieldName]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);
    setMessage("");
    setError("");

    try {
      const response = await changePassword(form);
      setForm(initialForm);
      setMessage(response.detail || "Mot de passe modifie avec succes.");
    } catch (submitError) {
      setError(getApiErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className={styles.page}>
      <header className={styles.heading}>
        <h1>Mon profil</h1>
        <p>{user?.matricule || "Utilisateur"} peut gerer son acces a la plateforme.</p>
      </header>

      <div className={styles.grid}>
        <article className={styles.panel}>
          <h2>Compte</h2>
          <div className={styles.summary}>
            <div className={styles.summaryItem}>
              <span>Nom</span>
              <strong>{user?.nom_users || "-"}</strong>
            </div>
            <div className={styles.summaryItem}>
              <span>Matricule</span>
              <strong>{user?.matricule || "-"}</strong>
            </div>
            <div className={styles.summaryItem}>
              <span>Role</span>
              <strong>{roleLabel(user?.role)}</strong>
            </div>
            <div className={styles.summaryItem}>
              <span>Perimetre</span>
              <strong>{user?.perimetre || user?.scope_type || "-"}</strong>
            </div>
          </div>
        </article>

        <article className={styles.panel}>
          <h2>Mot de passe</h2>
          {message && <div className={styles.message}>{message}</div>}
          {error && <div className={styles.error}>{error}</div>}

          <form className={styles.form} onSubmit={handleSubmit}>
            <label className={styles.field}>
              <span>Mot de passe actuel</span>
              <input
                type="password"
                value={form.current_password}
                onChange={(event) => updateField("current_password", event.target.value)}
                autoComplete="current-password"
                required
              />
            </label>
            <label className={styles.field}>
              <span>Nouveau mot de passe</span>
              <input
                type="password"
                value={form.new_password}
                onChange={(event) => updateField("new_password", event.target.value)}
                autoComplete="new-password"
                required
              />
            </label>
            <label className={styles.field}>
              <span>Confirmation</span>
              <input
                type="password"
                value={form.confirm_password}
                onChange={(event) => updateField("confirm_password", event.target.value)}
                autoComplete="new-password"
                required
              />
            </label>

            <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
              {isSubmitting ? <KeyRound size={16} /> : <Save size={16} />}
              {isSubmitting ? "Modification..." : "Modifier"}
            </button>
          </form>
        </article>
      </div>
    </section>
  );
}
