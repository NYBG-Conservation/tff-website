import { PUBLIC_DJANGO_API_BASE_URL } from '$env/static/public';

const API_BASE_URL = PUBLIC_DJANGO_API_BASE_URL || 'http://localhost:8000';

function getCsrfTokenFromCookie(): string | null {
	if (typeof document === 'undefined') {
		return null;
	}
	const token = document.cookie
		.split(';')
		.map((item) => item.trim())
		.find((item) => item.startsWith('csrftoken='));
	return token ? decodeURIComponent(token.split('=')[1]) : null;
}

export async function ensureCsrfCookie(fetchImpl: typeof fetch = fetch): Promise<void> {
	await fetchImpl(`${API_BASE_URL}/api/accounts/csrf/`, {
		method: 'GET',
		credentials: 'include'
	});
}

export async function apiRequest<T>(
	path: string,
	init: RequestInit = {},
	fetchImpl: typeof fetch = fetch
): Promise<T> {
	const headers = new Headers(init.headers || {});
	const method = (init.method || 'GET').toUpperCase();
	if (!headers.has('Content-Type') && !(init.body instanceof FormData)) {
		headers.set('Content-Type', 'application/json');
	}

	if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
		const csrfToken = getCsrfTokenFromCookie();
		if (csrfToken) {
			headers.set('X-CSRFToken', csrfToken);
		}
	}

	const response = await fetchImpl(`${API_BASE_URL}${path}`, {
		...init,
		headers,
		credentials: 'include'
	});

	if (!response.ok) {
		const text = await response.text();
		throw new Error(`API ${response.status}: ${text || response.statusText}`);
	}

	if (response.status === 204) {
		return {} as T;
	}

	return (await response.json()) as T;
}
