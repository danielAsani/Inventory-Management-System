import { Navigate } from "react-router-dom";
import logo from "../../../public/logo.png";
import LoginForm from "../../components/auth/LoginForm";
import { useAuth } from "../../hooks/useAuth";
import styles from "./Login.module.css";

export default function Login() {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <main className={styles.page}>
      <section className={styles.card} aria-labelledby="login-title">
        <div className={styles.brandBar} aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <div className={styles.content}>
          <header className={styles.header}>
            <img src={logo} alt="Gestion Inventaire" className={styles.logo} />
            <p className={styles.eyebrow}>Plateforme interne</p>
            <h1 id="login-title">Gestion d'inventaire</h1>
            <p className={styles.description}>
              Connectez-vous avec votre matricule pour acceder a votre espace.
            </p>
          </header>

          <LoginForm />
        </div>

        <footer className={styles.footer}>
          Societe Nationale d'Electricite <span aria-hidden="true">-</span> Espace securise
        </footer>
      </section>
    </main>
  );
}
