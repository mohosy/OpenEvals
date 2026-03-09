import clsx from "clsx";

export function cn(...values: Array<string | false | null | undefined>) {
  return clsx(values);
}

export function downloadTextFile(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function formatScore(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "--";
  }
  return `${value.toFixed(1)}`;
}

export function formatDelta(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "--";
  }
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}`;
}

