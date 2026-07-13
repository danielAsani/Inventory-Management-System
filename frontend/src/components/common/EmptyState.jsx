import { Inbox } from "lucide-react";
import styles from "./States.module.css";

export default function EmptyState({ title = "Aucune donnee", description = "Aucun enregistrement ne correspond a votre recherche." }) {
  return (
    <div className={styles.state}>
      <Inbox size={28} aria-hidden="true" />
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}
