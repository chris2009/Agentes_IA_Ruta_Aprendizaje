import { Download, Eye, EyeOff, ScrollText } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { downloadPlanUrl } from "../api/client.js";

export default function PlanCard({ plan, contenido, onVerPreview }) {
  return (
    <div className="plan-card">
      <div className="plan-card-header">
        <ScrollText size={18} />
        <strong>{plan.nombre_archivo}</strong>
        <span className="muted">{plan.fecha_generacion}</span>
        <button type="button" className="btn-small" onClick={() => onVerPreview(plan.nombre_archivo)}>
          {contenido ? <EyeOff /> : <Eye />}
          {contenido ? "Ocultar preview" : "Ver preview"}
        </button>
        <a className="btn-small" href={downloadPlanUrl(plan.nombre_archivo)} download>
          <Download />
          Descargar
        </a>
      </div>
      {contenido && (
        <div className="plan-preview">
          <ReactMarkdown>{contenido}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
