/**
 * AliciAPI — centralised HTTP client for all ALICI backend calls.
 *
 * Reads/writes the access_token from localStorage under the key "access_token"
 * and transparently refreshes it when the server returns 401.
 */
export class AliciAPI {
  constructor() {
    this.baseURL = "";
  }

  getToken() {
    return localStorage.getItem("access_token");
  }

  setToken(token) {
    localStorage.setItem("access_token", token);
  }

  getRefreshToken() {
    return localStorage.getItem("refresh_token");
  }

  setRefreshToken(token) {
    localStorage.setItem("refresh_token", token);
  }

  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("alici_user");
  }

  async refreshToken() {
    const refresh = this.getRefreshToken();
    if (!refresh) {
      this.clearTokens();
      window.location.href = "/";
      return;
    }

    try {
      const res = await fetch(`${this.baseURL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });

      if (!res.ok) {
        this.clearTokens();
        window.location.href = "/";
        return;
      }

      const data = await res.json();
      if (data.access_token) this.setToken(data.access_token);
      if (data.refresh_token) this.setRefreshToken(data.refresh_token);
    } catch {
      this.clearTokens();
      window.location.href = "/";
    }
  }

  async request(method, url, body = null, isMultipart = false) {
    const headers = {};

    if (!isMultipart) {
      headers["Content-Type"] = "application/json";
    }

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body !== null) {
      options.body = isMultipart ? body : JSON.stringify(body);
    }

    let response = await fetch(`${this.baseURL}${url}`, options);

    if (response.status === 401) {
      await this.refreshToken();
      const newToken = this.getToken();
      if (newToken) {
        headers["Authorization"] = `Bearer ${newToken}`;
        response = await fetch(`${this.baseURL}${url}`, { ...options, headers });
      }
    }

    return response.json();
  }

  get(url) {
    return this.request("GET", url);
  }

  post(url, body) {
    return this.request("POST", url, body);
  }

  put(url, body) {
    return this.request("PUT", url, body);
  }

  delete(url) {
    return this.request("DELETE", url);
  }

  postForm(url, formData) {
    return this.request("POST", url, formData, true);
  }
}

export const api = new AliciAPI();
