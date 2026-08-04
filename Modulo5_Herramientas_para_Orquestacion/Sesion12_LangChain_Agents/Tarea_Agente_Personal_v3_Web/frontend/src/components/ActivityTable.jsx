import { ClipboardList } from "lucide-react";
import { BadgeEstado, BadgePrioridad } from "./UrgencyBadge.jsx";

const SIGUIENTE_ESTADO = { pendiente: "iniciada", iniciada: "completada", completada: "pendiente" };

export default function ActivityTable({ actividades, onCambiarEstado }) {
  if (!actividades.length) {
    return (
      <div className="table-wrap">
        <div className="empty-state">
          <ClipboardList size={32} />
          <span>No hay actividades registradas.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Tipo</th>
            <th>Curso</th>
            <th>Vence</th>
            <th>Prioridad</th>
            <th>Urgencia</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {actividades.map((a) => (
            <tr key={a.id}>
              <td>{a.nombre}</td>
              <td>{a.tipo}</td>
              <td>{a.curso || "—"}</td>
              <td>
                {a.fecha_limite} ({a.dias_restantes}d)
              </td>
              <td>
                <BadgePrioridad prioridad={a.prioridad} />
              </td>
              <td>{a.puntaje_urgencia.toFixed(1)}</td>
              <td>
                <BadgeEstado estado={a.estado} />
              </td>
              <td>
                {onCambiarEstado && (
                  <button
                    type="button"
                    className="btn-small"
                    onClick={() => onCambiarEstado(a.id, SIGUIENTE_ESTADO[a.estado])}
                  >
                    Marcar {SIGUIENTE_ESTADO[a.estado]}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
