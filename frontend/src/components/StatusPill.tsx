import { cn } from "../lib/utils";

const statusStyles: Record<string, string> = {
  completed: "bg-spruce/10 text-spruce",
  partial: "bg-brass/15 text-brass",
  failed: "bg-ember/10 text-ember",
  running: "bg-ink/10 text-ink",
  pending: "bg-ink/10 text-ink",
  error: "bg-ember/10 text-ember",
};

export function StatusPill({ status }: { status: string }) {
  return (
    <span className={cn("rounded-full px-3 py-1 font-mono text-xs uppercase tracking-[0.18em]", statusStyles[status] ?? statusStyles.pending)}>
      {status}
    </span>
  );
}

