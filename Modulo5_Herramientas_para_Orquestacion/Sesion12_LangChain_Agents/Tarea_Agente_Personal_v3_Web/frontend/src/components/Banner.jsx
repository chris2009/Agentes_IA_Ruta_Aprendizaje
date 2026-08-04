import { AlertCircle, CheckCircle2, Info } from "lucide-react";

const CONFIG = {
  error: { clase: "banner-error", Icono: AlertCircle },
  success: { clase: "banner-success", Icono: CheckCircle2 },
  info: { clase: "banner-info", Icono: Info },
};

export default function Banner({ type = "info", children }) {
  if (!children) return null;

  const { clase, Icono } = CONFIG[type];

  return (
    <div className={`banner ${clase}`}>
      <Icono size={16} />
      <span>{children}</span>
    </div>
  );
}
