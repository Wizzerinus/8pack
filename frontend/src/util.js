import { useAuthStore } from "@/stores/auth.js"

const BACKEND_URL = "http://localhost:8003"

export function get(url, token = null, headers = {}) {
    headers = { ...headers, "Content-Type": "application/json" }
    if (token) {
        headers.Authorization = `Bearer ${token}`
    }
    return fetch(`${BACKEND_URL}/${url}`, {
        method: "GET",
        mode: "cors",
        headers,
    })
}

export function post(url, body = {}, token = null, headers = {}) {
    headers = { ...headers, "Content-Type": "application/json" }
    if (token) {
        headers.Authorization = `Bearer ${token}`
    }
    return fetch(`${BACKEND_URL}/${url}`, {
        method: "POST",
        mode: "cors",
        headers,
        body: JSON.stringify(body),
    })
}

export function auth_get(url, headers = {}) {
    const auth = useAuthStore()
    return get(url, auth.token, headers)
}

export function auth_post(url, body = {}, headers = {}) {
    const auth = useAuthStore()
    return post(url, body, auth.token, headers)
}
