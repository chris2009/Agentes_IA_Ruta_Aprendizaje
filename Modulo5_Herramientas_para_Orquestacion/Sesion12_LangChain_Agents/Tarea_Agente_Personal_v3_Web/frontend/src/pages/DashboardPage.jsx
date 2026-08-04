import { useEffect, useState } from "react";
import { getActivities, updateEstado } from "../api/client.js";
import ActivityTable from "../components/ActivityTable.jsx";
import Banner from "../components/Banner.jsx";
import Spinner from "../components/Spinner.jsx";

export default function DashboardPage() {
  const [actividades, setActividades] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargar = () => {
    setError("");
    getActivities()
      .then((datos) => setActividades(datos.filter((a) => a.estado !== "completada")))
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  };

  useEffect(cargar, []);

  const cambiarEstado = (id, nuevoEstado) => {
    updateEstado(id, nuevoEstado).then(cargar).catch((err) => setError(err.message));
  };

  return (
    <section>
      <h1>Dashboard</h1>
      <p className="page-intro">Pendientes ordenados por puntaje de urgencia (mayor primero).</p>
      <Banner type="error">{error}</Banner>
      {cargando ? <Spinner label="Cargando actividades…" /> : <ActivityTable actividades={actividades} onCambiarEstado={cambiarEstado} />}
    </section>
  );
}
