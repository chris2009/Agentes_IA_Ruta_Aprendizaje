const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function solicitar(ruta, opciones = {}) {
  const respuesta = await fetch(`${BASE_URL}/api${ruta}`, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });

  const datos = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    throw new Error(datos.detail || `Error ${respuesta.status}`);
  }

  return datos;
}

export const getHealth = () => solicitar("/health");

export const getActivities = () => solicitar("/activities");

export const createActivity = (actividad) =>
  solicitar("/activities", { method: "POST", body: JSON.stringify(actividad) });

export const updateEstado = (id, nuevoEstado) =>
  solicitar(`/activities/${id}/estado`, {
    method: "PATCH",
    body: JSON.stringify({ nuevo_estado: nuevoEstado }),
  });

export const getEvents = (fecha = "") =>
  solicitar(`/calendar/events${fecha ? `?fecha=${fecha}` : ""}`);

export const createEvent = (evento) =>
  solicitar("/calendar/events", { method: "POST", body: JSON.stringify(evento) });

export const generatePlan = (datos) =>
  solicitar("/plans/generate", { method: "POST", body: JSON.stringify(datos) });

export const listPlans = () => solicitar("/plans");

export const getPlan = (nombreArchivo) => solicitar(`/plans/${nombreArchivo}`);

export const downloadPlanUrl = (nombreArchivo) => `${BASE_URL}/api/plans/${nombreArchivo}/download`;

export const browseFiles = (path = "") =>
  solicitar(`/files/browse${path ? `?path=${encodeURIComponent(path)}` : ""}`);

export const sendChat = (message, history) =>
  solicitar("/chat", { method: "POST", body: JSON.stringify({ message, history }) });
