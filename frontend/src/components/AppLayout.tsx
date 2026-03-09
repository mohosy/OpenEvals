import { Link } from "@tanstack/react-router";
import { Boxes, Github, Rocket } from "lucide-react";
import { PropsWithChildren } from "react";

export function AppLayout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-paper text-ink">
      <div className="fixed inset-0 -z-10 bg-grid bg-[size:36px_36px] opacity-40" />
      <div className="fixed inset-x-0 top-0 -z-10 h-[28rem] bg-[radial-gradient(circle_at_top_left,_rgba(200,87,42,0.28),_transparent_48%),radial-gradient(circle_at_top_right,_rgba(13,93,86,0.18),_transparent_38%)]" />
      <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <Link to="/" className="flex items-center gap-3">
          <div className="rounded-2xl border border-ink/10 bg-white px-3 py-2 shadow-panel">
            <Boxes className="h-5 w-5 text-ember" />
          </div>
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.3em] text-ink/60">OpenEvals</p>
            <h1 className="font-display text-lg font-bold tracking-tight">Prompt Reliability Studio</h1>
          </div>
        </Link>
        <nav className="flex items-center gap-3">
          <Link
            to="/suites/new"
            className="rounded-full border border-ink/10 bg-white px-4 py-2 text-sm font-medium shadow-panel transition hover:-translate-y-0.5"
          >
            New suite
          </Link>
          <a
            href="https://github.com/new"
            className="inline-flex items-center gap-2 rounded-full bg-ink px-4 py-2 text-sm font-medium text-white"
            rel="noreferrer"
            target="_blank"
          >
            <Github className="h-4 w-4" />
            Publish fast
          </a>
        </nav>
      </header>
      <main className="mx-auto max-w-7xl px-6 pb-16">{children}</main>
      <footer className="mx-auto flex max-w-7xl items-center justify-between px-6 py-10 text-sm text-ink/60">
        <p>Open-source evals for prompt teams who care about regressions.</p>
        <p className="inline-flex items-center gap-2 font-mono uppercase tracking-[0.2em]">
          <Rocket className="h-4 w-4" />
          GitHub-ready MVP
        </p>
      </footer>
    </div>
  );
}
