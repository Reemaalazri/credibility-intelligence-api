const API_BASE = "https://credibility-intelligence-api.onrender.com";

function getAccessToken() {
  return localStorage.getItem("access");
}

function getRefreshToken() {
  return localStorage.getItem("refresh");
}

function setTokens(access, refresh) {
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
}

function clearTokens() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  localStorage.removeItem("username");
}

function getUsername() {
  return localStorage.getItem("username");
}

function setUsername(username) {
  localStorage.setItem("username", username);
}

function authHeaders(json = true) {
  const headers = {};
  const token = getAccessToken();

  if (json) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = `Bearer ${token}`;

  return headers;
}

async function apiGet(path, useAuth = false) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: useAuth ? authHeaders(false) : {}
  });
  return response;
}

async function apiPost(path, data, useAuth = false) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: useAuth ? authHeaders(true) : { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return response;
}

async function apiPut(path, data, useAuth = true) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: authHeaders(true),
    body: JSON.stringify(data)
  });
  return response;
}

async function apiPatch(path, data, useAuth = true) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: authHeaders(true),
    body: JSON.stringify(data)
  });
  return response;
}

async function apiDelete(path, useAuth = true) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: authHeaders(false)
  });
  return response;
}

function prettyJSON(data) {
  return JSON.stringify(data, null, 2);
}

function setIsAdmin(value) {
    localStorage.setItem("is_admin", value ? "true" : "false");
  }
  
  function isAdmin() {
    return localStorage.getItem("is_admin") === "true";
  }