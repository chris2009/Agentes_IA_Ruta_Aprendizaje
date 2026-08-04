import FileBrowser from "../components/FileBrowser.jsx";

export default function MaterialsPage() {
  return (
    <section>
      <h1>Materiales</h1>
      <p className="page-intro">Explora los archivos disponibles para alimentar al agente (carpeta autorizada).</p>
      <FileBrowser />
    </section>
  );
}
