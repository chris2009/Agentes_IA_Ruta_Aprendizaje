import { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  Bot,
  Calendar,
  FolderOpen,
  LayoutDashboard,
  ListChecks,
  Menu,
  MessageCircle,
  Moon,
  PlusCircle,
  ScrollText,
  Sun,
} from "lucide-react";
import useTheme from "../hooks/useTheme.js";

const ENLACES = [
  { to: "/", etiqueta: "Dashboard", icono: LayoutDashboard, fin: true },
  { to: "/actividades", etiqueta: "Actividades", icono: ListChecks },
  { to: "/actividades/nueva", etiqueta: "Nueva actividad", icono: PlusCircle },
  { to: "/calendario", etiqueta: "Calendario", icono: Calendar },
  { to: "/planes", etiqueta: "Planes", icono: ScrollText },
  { to: "/materiales", etiqueta: "Materiales", icono: FolderOpen },
  { to: "/chat", etiqueta: "Chat", icono: MessageCircle },
];

export default function NavBar() {
  const [colapsado, setColapsado] = useState(() => localStorage.getItem("sidebar-colapsado") === "true");
  const { theme, toggleTheme } = useTheme();

  const alternarColapso = () => {
    setColapsado((valor) => {
      localStorage.setItem("sidebar-colapsado", String(!valor));
      return !valor;
    });
  };

  return (
    <aside className={`sidebar ${colapsado ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        <div className="sidebar-title">
          <Bot size={22} />
          <span>Agente Personal</span>
        </div>
        <button type="button" className="sidebar-toggle" onClick={alternarColapso} title="Colapsar/expandir menú">
          <Menu size={18} />
        </button>
      </div>

      {ENLACES.map(({ to, etiqueta, icono: Icono, fin }) => (
        <NavLink key={to} to={to} end={fin} className={({ isActive }) => (isActive ? "navlink active" : "navlink")} title={etiqueta}>
          <Icono />
          <span>{etiqueta}</span>
        </NavLink>
      ))}

      <div className="sidebar-footer">
        <button type="button" className="theme-toggle" onClick={toggleTheme} title="Cambiar tema">
          {theme === "light" ? <Moon /> : <Sun />}
          <span>{theme === "light" ? "Tema oscuro" : "Tema claro"}</span>
        </button>
      </div>
    </aside>
  );
}
