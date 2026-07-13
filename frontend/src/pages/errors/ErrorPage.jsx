import { useNavigate } from "react-router-dom";
import styles from "./ErrorPage.module.css";

const illustrations = {
  403: "!",
  404: "?",
  500: "!",
};

export default function ErrorPage({ code, title, description }) {
  const navigate = useNavigate();

  return (
    <main className={styles.page}>
      <section className={styles.card} aria-labelledby={`error-${code}-title`}>
        <div className={styles.brandBar} aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <div className={styles.content}>
          <div className={styles.symbol} aria-hidden="true">
            {illustrations[code]}
          </div>
          <p className={styles.code}>Erreur {code}</p>
          <h1 id={`error-${code}-title`}>{title}</h1>
          <p className={styles.description}>{description}</p>

          <div className={styles.actions}>
            <button type="button" className={styles.primaryButton} onClick={() => navigate("/dashboard")}>
              Retour a l'accueil
            </button>
            <button type="button" className={styles.secondaryButton} onClick={() => navigate("/login")}>
              Reconnexion
            </button>
          </div>
        </div>

        <footer className={styles.footer}>
          Societe Nationale d'Electricite <span aria-hidden="true">-</span> Gestion d'inventaire
        </footer>
      </section>
    </main>
  );
}
