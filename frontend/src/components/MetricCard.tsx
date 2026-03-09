type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
};

export function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <div className="rounded-[1.5rem] border border-ink/10 bg-paper p-4">
      <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">{label}</p>
      <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
      {hint ? <p className="mt-2 text-sm text-ink/55">{hint}</p> : null}
    </div>
  );
}

