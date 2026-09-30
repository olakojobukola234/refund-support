const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function submitRefund(payload) {
  let res;
  try {
    res = await fetch(`${BASE}/refund-request/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    err.retryable = true;
    throw err;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const error = new Error(Object.values(err).flat().join(" ") || "Request failed");
    error.retryable = res.status === 429 || res.status >= 500;
    throw error;
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