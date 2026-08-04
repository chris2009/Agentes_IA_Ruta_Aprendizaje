import { useEffect, useState } from "react";
import { ScrollText, Sparkles } from "lucide-react";
import { generatePlan, getPlan, listPlans } from "../api/client.js";
import Banner from "../components/Banner.jsx";
import PlanCard from "../components/PlanCard.jsx";
import Spinner from "../components/Spinner.jsx";

const HOY = new Date().toISOString().slice(0, 10);

export default function PlansPage() {
  const [planes, setPlanes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [form, setForm] = useState({ fecha: HOY, hora_inicio: "", hora_fin: "" });
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [generando, setGenerando] = useState(false);
  const [previews, setPrevias] = useState({});

  const cargarPlanes = () => {
    setError("");
    listPlans()
      .then(setPlanes)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  };

  useEffect(cargarPlanes, []);

  const actualizar = (campo) => (evento) => setForm({ ...form, [campo]: evento.target.value });

  const generar = (evento) => {
    evento.preventDefault();
    setMensaje("");
    setGenerando(true);
    generatePlan(form)
      .then((res) => {
        setMensaje(res.mensaje);
        cargarPlanes();
      })
      .catch((err) => setError(err.message))
      .finally(() => setGenerando(false));
  };

  const togglePreview = (nombreArchivo) => {
    if (previews[nombreArchivo]) {
      setPrevias({ ...previews, [nombreArchivo]: null });
      return;
    }

    getPlan(nombreArchivo)
      .then((res) => setPrevias({ ...previews, [nombreArchivo]: res.contenido }))
      .catch((err) => setError(err.message));
  };

  return (
    <section>
      <h1>Planes</h1>
      <p className="page-intro">Genera un plan para un rango horario y respeta tu calendario real.</p>

      <form className="form" onSubmit={generar}>
        <label>
          Fecha
          <input type="date" value={form.fecha} onChange={actualizar("fecha")} required />
        </label>
        <label>
          Hora inicio
          <input type="time" value={form.hora_inicio} onChange={actualizar("hora_inicio")} required />
        </label>
        <label>
          Hora fin
          <input type="time" value={form.hora_fin} onChange={actualizar("hora_fin")} required />
        </label>

        <Banner type="error">{error}</Banner>
        <Banner type="success">{mensaje}</Banner>

        <button type="submit" className="btn-primary" disabled={generando}>
          <Sparkles />
          {generando ? "Generando…" : "Generar plan"}
        </button>
      </form>

      <hr />

      <h2>Historial de planes</h2>
      {cargando ? (
        <Spinner label="Cargando planes…" />
      ) : !planes.length ? (
        <div className="empty-state">
          <ScrollText size={32} />
          <span>Aún no hay planes generados.</span>
        </div>
      ) : (
        planes.map((plan) => (
          <PlanCard key={plan.nombre_archivo} plan={plan} contenido={previews[plan.nombre_archivo]} onVerPreview={togglePreview} />
        ))
      )}
    </section>
  );
}
