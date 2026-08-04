import { useEffect, useState } from "react";
import { CalendarDays, CalendarPlus } from "lucide-react";
import { createEvent, getEvents } from "../api/client.js";
import Banner from "../components/Banner.jsx";
import Spinner from "../components/Spinner.jsx";

const HOY = new Date().toISOString().slice(0, 10);
const EVENTO_VACIO = { fecha: HOY, hora_inicio: "", hora_fin: "", resumen: "", descripcion: "" };

export default function CalendarPage() {
  const [fecha, setFecha] = useState(HOY);
  const [eventos, setEventos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [formEvento, setFormEvento] = useState(EVENTO_VACIO);
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);

  const cargarEventos = () => {
    setError("");
    setCargando(true);
    getEvents(fecha)
      .then(setEventos)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  };

  useEffect(cargarEventos, [fecha]);

  const actualizar = (campo) => (evento) => setFormEvento({ ...formEvento, [campo]: evento.target.value });

  const agendar = (evento) => {
    evento.preventDefault();
    setMensaje("");
    setEnviando(true);
    createEvent(formEvento)
      .then((res) => {
        setMensaje(res.mensaje);
        setFormEvento({ ...EVENTO_VACIO, fecha });
        cargarEventos();
      })
      .catch((err) => setError(err.message))
      .finally(() => setEnviando(false));
  };

  return (
    <section>
      <h1>Calendario</h1>

      <label className="form" style={{ maxWidth: 220 }}>
        Fecha
        <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} />
      </label>

      <Banner type="error">{error}</Banner>

      {cargando ? (
        <Spinner label="Consultando Google Calendar…" />
      ) : (
        <ul className="event-list">
          {eventos.map((e, i) => (
            <li key={i}>
              <CalendarDays size={16} />
              <strong>{e.resumen}</strong>
              <span className="event-time">
                {e.inicio.includes("T") ? `${e.inicio.slice(11, 16)} – ${e.fin.slice(11, 16)}` : "todo el día"}
              </span>
            </li>
          ))}
          {!eventos.length && !error && (
            <div className="empty-state">
              <CalendarDays size={32} />
              <span>No hay eventos para esta fecha.</span>
            </div>
          )}
        </ul>
      )}

      <hr />

      <h2>Agendar evento en el calendario</h2>
      <p className="page-intro">
        Esto crea un evento REAL en tu Google Calendar (distinto de registrar una actividad pendiente).
      </p>

      <form className="form" onSubmit={agendar}>
        <label>
          Fecha
          <input type="date" value={formEvento.fecha} onChange={actualizar("fecha")} required />
        </label>
        <label>
          Hora inicio
          <input type="time" value={formEvento.hora_inicio} onChange={actualizar("hora_inicio")} required />
        </label>
        <label>
          Hora fin
          <input type="time" value={formEvento.hora_fin} onChange={actualizar("hora_fin")} required />
        </label>
        <label>
          Título
          <input value={formEvento.resumen} onChange={actualizar("resumen")} required />
        </label>
        <label>
          Descripción (opcional)
          <input value={formEvento.descripcion} onChange={actualizar("descripcion")} />
        </label>

        <Banner type="success">{mensaje}</Banner>

        <button type="submit" className="btn-primary" disabled={enviando}>
          <CalendarPlus />
          {enviando ? "Agendando…" : "Agendar evento"}
        </button>
      </form>
    </section>
  );
}
