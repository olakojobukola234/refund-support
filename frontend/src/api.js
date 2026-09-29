const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function submitRefund(payload) {
  const res = await fetch(`${BASE}/refund-request/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(Object.values(err).flat().join(" ") || "Request failed");
  }
  return res.json();
}

export async function fetchRequests() {
  const res = await fetch(`${BASE}/requests/`);
  if (!res.ok) throw new Error("Could not load requests");
  return res.json();
}

export async function fetchCustomers() {
  const res = await fetch(`${BASE}/customers/`);
  if (!res.ok) throw new Error("Could not load customers");
  return res.json();
}