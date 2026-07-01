import { PUBLIC_DJANGO_API_BASE_URL } from '$env/static/public';

export function getDjangoApiBaseUrl(): string {
	return PUBLIC_DJANGO_API_BASE_URL || 'http://localhost:8000';
}

export function djangoAdminUrl(path: string): string {
	const base = getDjangoApiBaseUrl().replace(/\/$/, '');
	const normalizedPath = path.startsWith('/') ? path : `/${path}`;
	return `${base}${normalizedPath}`;
}

export function djangoAdminHomeUrl(): string {
	return djangoAdminUrl('/admin/');
}

export function djangoAdminDatasetUrl(datasetId: number): string {
	return djangoAdminUrl(`/admin/datasets/dataset/${datasetId}/change/`);
}

export function djangoAdminProjectSearchUrl(query: string): string {
	const params = new URLSearchParams({ q: query });
	return djangoAdminUrl(`/admin/datasets/project/?${params.toString()}`);
}
