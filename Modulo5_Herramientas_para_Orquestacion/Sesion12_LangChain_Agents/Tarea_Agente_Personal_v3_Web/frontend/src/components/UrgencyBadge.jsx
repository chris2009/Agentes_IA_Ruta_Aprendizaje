const COLOR_PRIORIDAD = { alta: "badge-alta", media: "badge-media", baja: "badge-baja" };
const COLOR_ESTADO = {
  pendiente: "badge-pendiente",
  iniciada: "badge-iniciada",
  completada: "badge-completada",
};

export function BadgePrioridad({ prioridad }) {
  return <span className={`badge ${COLOR_PRIORIDAD[prioridad] || ""}`}>{prioridad}</span>;
}

export function BadgeEstado({ estado }) {
  return <span className={`badge ${COLOR_ESTADO[estado] || ""}`}>{estado}</span>;
}
