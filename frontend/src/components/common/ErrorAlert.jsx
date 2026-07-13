import { TriangleAlert } from "lucide-react";
import styles from "./States.module.css";

export default function ErrorAlert({ message, onRetry }) {
  if (!message) return null;

  return (
    <div className={styles.alert} role="alert">
      <TriangleAlert size={18} aria-hidden="true" />
      <span>{message}</span>
      {onRetry && <button type="button" onClick={onRetry}>Reessayer</button>}
    </div>
  );
}
