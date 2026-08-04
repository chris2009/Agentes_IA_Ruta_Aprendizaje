import { useEffect, useState } from "react";
import { File, Folder, FolderOpen } from "lucide-react";
import { browseFiles } from "../api/client.js";
import Banner from "./Banner.jsx";
import Spinner from "./Spinner.jsx";

/**
 * Explorador de CARPETA_AUTORIZADA. Si se pasa onSelect, cada carpeta
 * muestra un botón "Elegir esta carpeta" (selector embebido); si no, es
 * solo navegación de lectura (página Materiales standalone).
 */
export default function FileBrowser({ onSelect }) {
  const [ruta, setRuta] = useState("");
  const [entradas, setEntradas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    setCargando(true);
    browseFiles(ruta)
      .then((datos) => setEntradas(datos.entradas))
      .catch((err) => {
        setError(err.message);
        setEntradas([]); // evita mostrar el listado de la carpeta anterior junto al error
      })
      .finally(() => setCargando(false));
  }, [ruta]);

  const partes = ruta.split("/").filter(Boolean);

  const irA = (indice) => setRuta(partes.slice(0, indice + 1).join("/"));

  return (
    <div className="file-browser">
      <div className="file-browser-toolbar">
        <nav className="breadcrumbs">
          <button type="button" onClick={() => setRuta("")}>
            materiales
          </button>
          {partes.map((parte, i) =>
            i === partes.length - 1 ? (
              <span key={i} className="current">
                / {parte}
              </span>
            ) : (
              <span key={i}>
                / <button onClick={() => irA(i)}>{parte}</button>
              </span>
            ),
          )}
        </nav>
        {onSelect && (
          <button type="button" className="btn-small" onClick={() => onSelect(ruta)}>
            Elegir esta carpeta
          </button>
        )}
      </div>

      <Banner type="error">{error}</Banner>

      {cargando ? (
        <Spinner label="Cargando…" />
      ) : (
        <ul className="file-list">
          {entradas.map((e) => (
            <li key={e.ruta_relativa}>
              {e.es_carpeta ? (
                <button type="button" className="file-row is-folder link-button" onClick={() => setRuta(e.ruta_relativa)}>
                  <Folder />
                  {e.nombre}
                </button>
              ) : (
                <span className={`file-row is-file ${e.extension_admitida ? "" : "muted"}`}>
                  <File />
                  {e.nombre}
                </span>
              )}
            </li>
          ))}
          {!entradas.length && !error && (
            <div className="empty-state">
              <FolderOpen size={32} />
              <span>Carpeta vacía.</span>
            </div>
          )}
        </ul>
      )}
    </div>
  );
}
