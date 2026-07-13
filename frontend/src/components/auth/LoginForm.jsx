import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import styles from "./LoginForm.module.css";

function getLoginErrorMessage(error) {
  const data = error.response?.data;

  if (!data) {
    return "Impossible de contacter le serveur.";
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
    return data.non_field_errors[0];
  }

  return "Connexion impossible. Verifiez vos informations.";
}

export default function LoginForm() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [erreur, setErreur] = useState("");
  const [chargement, setChargement] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (chargement) return;

    setErreur("");
    setChargement(true);

    try {
      const trimmedIdentifier = identifier.trim();
      await login({
        [trimmedIdentifier.includes("@") ? "email" : "matricule"]: trimmedIdentifier,
        password,
      });
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (error) {
      setErreur(getLoginErrorMessage(error));
    } finally {
      setChargement(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      {erreur && <div className={styles.error} role="alert">{erreur}</div>}

      <div className={styles.field}>
        <label className={styles.label} htmlFor="identifier">
          Matricule ou email <span aria-hidden="true">*</span>
        </label>
        <input
          id="identifier"
          type="text"
          value={identifier}
          onChange={(event) => setIdentifier(event.target.value)}
          placeholder="Ex. ADMIN001 ou admin@example.com"
          required
          autoComplete="username"
          className={styles.input}
        />
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="password">
          Mot de passe <span aria-hidden="true">*</span>
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Entrez votre mot de passe"
          required
          autoComplete="current-password"
          className={styles.input}
        />
      </div>

      <button type="submit" disabled={chargement} className={styles.submitButton}>
        {chargement ? "Connexion..." : "Se connecter"}
      </button>
    </form>
  );
}
