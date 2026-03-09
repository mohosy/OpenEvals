import { PropsWithChildren } from "react";

import { cn } from "../lib/utils";

type SectionCardProps = PropsWithChildren<{
  className?: string;
}>;

export function SectionCard({ className, children }: SectionCardProps) {
  return (
    <section className={cn("rounded-[2rem] border border-ink/10 bg-white/90 p-6 shadow-panel backdrop-blur", className)}>
      {children}
    </section>
  );
}

