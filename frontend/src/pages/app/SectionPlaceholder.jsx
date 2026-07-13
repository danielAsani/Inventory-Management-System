import { Construction } from "lucide-react";
import styles from "./SectionPlaceholder.module.css";

export default function SectionPlaceholder({ title, description }) {
  return (
    <section className={styles.page}>
      <p className={styles.eyebrow}>Module en préparation</p>
      <h1>{title}</h1>
      <div className={styles.card}>
        <div className={styles.icon}><Construction size={25} /></div>
        <div><h2>Cette section est prête à être construite</h2><p>{description}</p></div>
      </div>
    </section>
  );
}
