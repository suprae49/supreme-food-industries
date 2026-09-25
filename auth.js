const TOKEN_KEY = "sfi_token";
const SESSION_KEY = "sfi_session";

function apiUrl(path) {
  return path.startsWith("/api/") ? path : `/api/${path}`;
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

function getSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || "null");
  } catch {
    return null;
  }
}

function setSession(user) {
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({
      id: user.id,
      name: user.name,
      phone: user.phone,
      is_admin: !!user.is_admin,
      loggedInAt: Date.now(),
    })
  );
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
  setToken("");
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(apiUrl(path), {
    ...options,
    headers,
  });

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = { ok: false, error: "सर्भरबाट उत्तर आएन।" };
  }

  if (!response.ok && !data.error) {
    data.error = "केही गलत भयो। फेरि प्रयास गर्नुहोस्।";
  }
  return { ...data, status: response.status };
}

async function signupUser({ name, phone, password }) {
  const result = await api("/api/signup", {
    method: "POST",
    body: JSON.stringify({ name, phone, password }),
  });
  if (result.ok) {
    setToken(result.token);
    setSession(result.user);
  }
  return result;
}

async function loginUser({ phone, password }) {
  const result = await api("/api/login", {
    method: "POST",
    body: JSON.stringify({ phone, password }),
  });
  if (result.ok) {
    setToken(result.token);
    setSession(result.user);
  }
  return result;
}

async function logoutUser() {
  try {
    await api("/api/logout", { method: "POST", body: "{}" });
  } catch {
    // ignore network errors on logout
  }
  clearSession();
}

async function submitContact({ name, phone, message }) {
  return api("/api/contact", {
    method: "POST",
    body: JSON.stringify({ name, phone, message }),
  });
}

async function fetchCompany() {
  return api("/api/company");
}

function renderAuthNav(nav) {
  if (!nav) return;

  const existing = nav.querySelector(".auth-slot");
  if (existing) existing.remove();

  const slot = document.createElement("div");
  slot.className = "auth-slot";

  const session = getSession();
  if (session) {
    slot.innerHTML = `
      <span class="auth-user" title="${session.phone}">नमस्ते, ${session.name.split(" ")[0]}</span>
      ${session.is_admin ? '<a href="admin.html" class="nav-cta">एडमिन</a>' : ""}
      <button type="button" class="nav-cta auth-logout">लगआउट</button>
    `;
    slot.querySelector(".auth-logout")?.addEventListener("click", async () => {
      await logoutUser();
      window.location.reload();
    });
  } else {
    slot.innerHTML = `
      <a href="login.html">लगइन</a>
      <a href="signup.html" class="nav-cta">साइन अप</a>
    `;
  }

  nav.appendChild(slot);
}
