import JsBarcode from "jsbarcode";
import { Printer, Tags } from "lucide-react";
import QRCode from "qrcode";
import { useEffect, useMemo, useRef, useState } from "react";
import styles from "./TraceabilityLabel.module.css";

const LABEL_FORMATS = [
  { id: "50x30", label: "50 x 30 mm", width: 50, height: 30 },
  { id: "70x37", label: "70 x 37 mm", width: 70, height: 37 },
  { id: "90x50", label: "90 x 50 mm", width: 90, height: 50 },
  { id: "100x60", label: "100 x 60 mm", width: 100, height: 60 },
];

function cleanText(value) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

function joinValues(...values) {
  return values.map(cleanText).filter((value) => value !== "-").join(" ");
}

function getLabelData(item, config) {
  const labelConfig = config.traceabilityLabel || {};
  const title = cleanText(item[labelConfig.titleField || config.idField]);
  const subtitle = joinValues(...(labelConfig.subtitleFields || []).map((field) => item[field]));
  const category = cleanText(item[labelConfig.categoryField] || item.categorie_nom || item.famille_nom);
  const location = cleanText(item[labelConfig.locationField] || item.magasin_nom || item.etat);

  return {
    title,
    subtitle,
    category,
    location,
    barcodeValue: cleanText(item[labelConfig.barcodeField || "code_barre"]),
    qrValue: cleanText(item[labelConfig.qrField || "qr_code"]),
    serial: cleanText(item[labelConfig.serialField] || item.numero_serie),
  };
}

export function BarcodeValue({ value, compact = false }) {
  const ref = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!ref.current || !value || value === "-") return;
    try {
      JsBarcode(ref.current, String(value), {
        format: "CODE128",
        displayValue: true,
        width: compact ? 1.15 : 1.45,
        height: compact ? 30 : 44,
        margin: 0,
        font: "Arial",
        fontSize: compact ? 9 : 12,
        textMargin: 3,
        lineColor: "#111827",
      });
      setError("");
    } catch {
      setError("Code-barres invalide");
    }
  }, [compact, value]);

  if (!value || value === "-") return <span>-</span>;

  return (
    <div className={styles.inlineCode}>
      {error ? <span>{error}</span> : <svg ref={ref} className={styles.barcodeSvg} aria-label={`Code-barres ${value}`} />}
    </div>
  );
}

export function QrValue({ value, compact = false }) {
  const [src, setSrc] = useState("");

  useEffect(() => {
    let isMounted = true;
    if (!value || value === "-") {
      setSrc("");
      return () => {
        isMounted = false;
      };
    }

    QRCode.toDataURL(String(value), {
      errorCorrectionLevel: "M",
      margin: 1,
      width: compact ? 92 : 132,
      color: {
        dark: "#111827",
        light: "#ffffff",
      },
    })
      .then((dataUrl) => {
        if (isMounted) setSrc(dataUrl);
      })
      .catch(() => {
        if (isMounted) setSrc("");
      });

    return () => {
      isMounted = false;
    };
  }, [compact, value]);

  if (!value || value === "-") return <span>-</span>;

  return (
    <div className={styles.inlineCode}>
      {src ? <img className={styles.qrImage} src={src} alt={`QR code ${value}`} /> : <span>{value}</span>}
      <small>{value}</small>
    </div>
  );
}

function PrintableLabel({ data, format }) {
  return (
    <article
      className={styles.printLabel}
      style={{
        "--label-width": `${format.width}mm`,
        "--label-height": `${format.height}mm`,
      }}
    >
      <div className={styles.labelInfo}>
        <span>Gestion Inventaire</span>
        <strong>{data.title}</strong>
        <small>{data.subtitle || data.category}</small>
        <em>{data.serial}</em>
      </div>
      <div className={styles.labelBarcode}>
        <BarcodeValue value={data.barcodeValue} compact />
      </div>
      <div className={styles.labelQr}>
        <QrValue value={data.qrValue} compact />
      </div>
      <div className={styles.labelMeta}>
        <span>{data.category}</span>
        <span>{data.location}</span>
      </div>
    </article>
  );
}

export default function TraceabilityLabelPrinter({ item, config }) {
  const [formatId, setFormatId] = useState(LABEL_FORMATS[1].id);
  const [copies, setCopies] = useState(1);
  const format = LABEL_FORMATS.find((entry) => entry.id === formatId) || LABEL_FORMATS[1];
  const data = useMemo(() => getLabelData(item, config), [config, item]);
  const copyCount = Math.max(1, Math.min(50, Number(copies) || 1));
  const printLabels = Array.from({ length: copyCount }, (_, index) => index);

  const print = () => {
    const styleId = "traceability-label-page-size";
    let style = document.getElementById(styleId);
    if (!style) {
      style = document.createElement("style");
      style.id = styleId;
      document.head.appendChild(style);
    }

    style.textContent = `@page { size: ${format.width}mm ${format.height}mm; margin: 0; }`;
    const cleanup = () => {
      document.body.classList.remove("label-print-mode");
      window.removeEventListener("afterprint", cleanup);
    };

    window.addEventListener("afterprint", cleanup);
    document.body.classList.add("label-print-mode");
    window.print();
    window.setTimeout(cleanup, 1000);
  };

  return (
    <section className={styles.panel}>
      <header className={styles.panelHeader}>
        <div>
          <span><Tags size={16} /> Etiquette</span>
          <h3>Code-barres et QR code reels</h3>
        </div>
        <button type="button" className={styles.printButton} onClick={print}>
          <Printer size={17} /> Imprimer
        </button>
      </header>

      <div className={styles.previewGrid}>
        <div className={styles.previewCard}>
          <PrintableLabel data={data} format={format} />
        </div>
        <div className={styles.controls}>
          <label>
            <span>Format</span>
            <select value={formatId} onChange={(event) => setFormatId(event.target.value)}>
              {LABEL_FORMATS.map((entry) => (
                <option value={entry.id} key={entry.id}>{entry.label}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Copies</span>
            <input
              type="number"
              min="1"
              max="50"
              value={copies}
              onChange={(event) => setCopies(event.target.value)}
            />
          </label>
        </div>
      </div>

      <div className={`${styles.printSheet} label-print-sheet`} aria-hidden="true">
        {printLabels.map((index) => <PrintableLabel data={data} format={format} key={index} />)}
      </div>
    </section>
  );
}
