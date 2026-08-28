// Design philosophy: Salon Noir — API failures are quiet, explicit, and never allowed to obscure the critical check-in state.

export type CheckinStatus = "SUCCESS" | "ALREADY_SCANNED" | "INVALID" | "ERROR";

export type CheckinResponse = {
  status: CheckinStatus;
  message: string;
  trace_id: string;
  guest_id?: string | null;
  name?: string | null;
  table?: string | null;
  scanned_at?: string | null;
};

const API_URL = import.meta.env.VITE_GATSBY_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) throw new Error(`Gatsby API ${response.status}`);
  return response.json() as Promise<T>;
}

export function checkIn(guestToken: string, eventId = "event-grand-bal") {
  return request<CheckinResponse>(`/api/check-in/${encodeURIComponent(guestToken)}?event_id=${encodeURIComponent(eventId)}`, { method: "POST" });
}

export function getDashboardStats(eventId = "event-grand-bal") {
  return request<{ total: number; present: number; remaining: number; rate: number }>(`/api/dashboard/stats?event_id=${encodeURIComponent(eventId)}`);
}

export function getGuestQrUrl(guestId: string, eventId = "event-grand-bal") {
  return `${API_URL}/api/qr/${encodeURIComponent(guestId)}.png?event_id=${encodeURIComponent(eventId)}`;
}
