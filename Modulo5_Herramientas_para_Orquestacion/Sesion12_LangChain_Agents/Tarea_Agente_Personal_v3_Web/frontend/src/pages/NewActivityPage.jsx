import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FolderSearch } from "lucide-react";
import { createActivity } from "../api/client.js";
import Banner from "../components/Banner.jsx";
import FileBrowser from "../components/FileBrowser.jsx";

const VACIO = {
  nombre: "",
  tipo: "academica",
  fecha_limite: "",
  duracion_minutos: 60,
  prioridad: "media",
  curso: "",
  ruta_contexto: "",
  entregable: "",
};

export default function NewActivityPage() {
  const [form, setForm] = useState(VACIO);
  const [mostrarExplorador, setMostrarExplorador] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);
  const navegar = useNavigate();

  const actualizar = (campo) => (evento) => setForm({ ...form, [campo]: evento.target.value });

  const enviar = (evento) => {
    evento.preventDefault();
    setError("");
    setEnviando(true);
    createActivity({ ...form, duracion_minutos: Number(form.duracion_minutos) })
      .then((res) => {
        setMensaje(res.mensaje);
        setTimeout(() => navegar("/actividades"), 800);
      })
      .catch((err) => setError(err.message))
      .finally(() => setEnviando(false));
  };

  return (
    <section>
      <h1>Nueva actividad</h1>
      <p className="page-intro">
        Registra una actividad o tarea pendiente. Esto NO crea nada en Google Calendar — para eso usa
        "Agendar evento" en la página Calendario.
      </p>

      <form className="form" onSubmit={enviar}>
        <label>
          Nombre
          <input value={form.nombre} onChange={actualizar("nombre")} required />
        </label>

        <label>
          Tipo
          <select value={form.tipo} onChange={actualizar("tipo")}>
            <option value="academica">Académica</option>
            <option value="personal">Personal</option>
          </select>
        </label>

        <label>
          Curso (opcional)
          <input value={form.curso} onChange={actualizar("curso")} />
        </label>

        <label>
          Fecha límite
          <input type="date" value={form.fecha_limite} onChange={actualizar("fecha_limite")} required />
        </label>

        <label>
          Duración estimada (minutos)
          <input type="number" min="5" value={form.duracion_minutos} onChange={actualizar("duracion_minutos")} required />
        </label>

        <label>
          Prioridad
          <select value={form.prioridad} onChange={actualizar("prioridad")}>
            <option value="alta">Alta</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
        </label>

        <label>
          Entregable (opcional)
          <input value={form.entregable} onChange={actualizar("entregable")} />
        </label>

        <label>
          Carpeta de materiales (opcional)
          <div className="inline-field">
            <input value={form.ruta_contexto} onChange={actualizar("ruta_contexto")} placeholder="ej. Investigacion" />
            <button type="button" className="btn-small" onClick={() => setMostrarExplorador(!mostrarExplorador)}>
              <FolderSearch />
              {mostrarExplorador ? "Cerrar" : "Elegir carpeta"}
            </button>
          </div>
        </label>

        {mostrarExplorador && (
          <FileBrowser
            onSelect={(ruta) => {
              setForm({ ...form, ruta_contexto: ruta });
              setMostrarExplorador(false);
            }}
          />
        )}

        <Banner type="error">{error}</Banner>
        <Banner type="success">{mensaje}</Banner>

        <button type="submit" className="btn-primary" disabled={enviando}>
          {enviando ? "Registrando…" : "Registrar actividad"}
        </button>
      </form>
    </section>
  );
}
