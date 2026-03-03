/**
 * api.js — ALICI™ API Client
 * Isolated API client with JWT management and automatic token refresh.
 */

const AliciAPI = (() => {
    let _token = null;
    let _refreshToken = null;

    function setTokens(access, refresh) {
        _token = access;
        _refreshToken = refresh || _refreshToken;
        if (access) localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
    }

    function clearTokens() {
        _token = null;
        _refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('alici_user');
    }

    function loadTokens() {
        _token = localStorage.getItem('access_token');
        _refreshToken = localStorage.getItem('refresh_token');
    }

    function getToken() {
        return _token;
    }

    function isAuthenticated() {
        return Boolean(_token);
    }

    async function _tryRefresh() {
        if (!_refreshToken) throw new Error('UNAUTHORIZED');
        const resp = await fetch('/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: _refreshToken }),
        });
        if (!resp.ok) {
            clearTokens();
            throw new Error('UNAUTHORIZED');
        }
        const data = await resp.json();
        setTokens(data.access_token, data.refresh_token);
        return data.access_token;
    }

    async function _request(method, url, body = null, isRetry = false) {
        const headers = {};
        if (_token) headers['Authorization'] = 'Bearer ' + _token;
        if (body !== null) headers['Content-Type'] = 'application/json';

        const opts = { method, headers };
        if (body !== null) opts.body = JSON.stringify(body);

        const resp = await fetch(url, opts);

        if (resp.status === 401 && !isRetry) {
            try {
                await _tryRefresh();
                return _request(method, url, body, true);
            } catch (_) {
                clearTokens();
                throw new Error('UNAUTHORIZED');
            }
        }

        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            const msg = (data && (data.message || data.detail)) || `HTTP ${resp.status}`;
            throw new Error(msg);
        }
        return data;
    }

    async function uploadFile(url, formData) {
        const headers = {};
        if (_token) headers['Authorization'] = 'Bearer ' + _token;

        const resp = await fetch(url, { method: 'POST', headers, body: formData });

        if (resp.status === 401) {
            try {
                await _tryRefresh();
                const headers2 = { 'Authorization': 'Bearer ' + _token };
                const resp2 = await fetch(url, { method: 'POST', headers: headers2, body: formData });
                const data2 = await resp2.json().catch(() => ({}));
                if (!resp2.ok) throw new Error(data2.message || `HTTP ${resp2.status}`);
                return data2;
            } catch (_) {
                clearTokens();
                throw new Error('UNAUTHORIZED');
            }
        }

        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) throw new Error(data.message || `HTTP ${resp.status}`);
        return data;
    }

    return {
        init: loadTokens,
        setTokens,
        clearTokens,
        loadTokens,
        getToken,
        isAuthenticated,
        get: (url) => _request('GET', url),
        post: (url, body) => _request('POST', url, body),
        put: (url, body) => _request('PUT', url, body),
        delete: (url) => _request('DELETE', url),
        patch: (url, body) => _request('PATCH', url, body),
        uploadFile,
    };
})();

// Auto-init on load
AliciAPI.init();
