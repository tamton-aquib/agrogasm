const DEFAULT_API = "http://127.0.0.1:5000";
const DEFAULT_CITY = "Kottayam";

function readLS(key: string): string {
  try {
    return localStorage.getItem(key) || "";
  } catch {
    return "";
  }
}

export const API_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") || DEFAULT_API;

export const WEATHER_API_KEY = import.meta.env.VITE_OWM_KEY || "";

export function getWeatherCity(): string {
  return (
    readLS("agrogasm.city") ||
    import.meta.env.VITE_OWM_CITY ||
    DEFAULT_CITY
  );
}

export function timeAgo(iso?: string): string {
  if (!iso) return "";
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return "";
  const s = Math.floor((Date.now() - t) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}
