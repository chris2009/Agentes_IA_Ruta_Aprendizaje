import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PlusCircle } from "lucide-react";
import { getActivities, updateEstado } from "../api/client.js";
import ActivityTable from "../components/ActivityTable.jsx";
import Banner from "../components/Banner.jsx";
import Spinner from "../components/Spinner.jsx";

export default function ActivitiesPage() {
  const [actividades, setActividades] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargar = () => {
    setError("");
    getActivities()
      .then(setActividades)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  };

  useEffect(cargar, []);

  const cambiarEstado = (id, nuevoEstado) => {
    updateEstado(id, nuevoEstado).then(cargar).catch((err) => setError(err.message));
  };

  return (
    <section>
      <div className="page-header">
        <h1>Actividades</h1>
        <Link className="btn-small" to="/actividades/nueva">
          <PlusCircle />
          Nueva actividad
        </Link>
      </div>
      <Banner type="error">{error}</Banner>
      {cargando ? <Spinner label="Cargando actividades…" /> : <ActivityTable actividades={actividades} onCambiarEstado={cambiarEstado} />}
    </section>
  );
}
