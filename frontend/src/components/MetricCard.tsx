import type { LucideIcon } from "lucide-react";

interface Props { icon: LucideIcon; label: string; value: string; description: string; tone?: "default" | "warning" }

export function MetricCard({ icon: Icon, label, value, description, tone = "default" }: Props) {
  return <article className={`metric-card metric-card--${tone}`}>
    <div className="metric-card__heading"><span>{label}</span><Icon size={17} aria-hidden="true" /></div>
    <strong>{value}</strong><p>{description}</p>
  </article>;
}
