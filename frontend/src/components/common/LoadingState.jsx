import styles from "./States.module.css";

export default function LoadingState({ label = "Chargement..." }) {
  return (
    <div className={styles.state} role="status">
      <span className={styles.spinner} aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}
