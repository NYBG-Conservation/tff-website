import { apiRequest, ensureCsrfCookie } from './client';

export type ProjectPublication = {
	id: number;
	project: number | null;
	project_slug?: string | null;
	citation: string;
	title?: string;
	publication_year?: number | null;
	doi?: string;
	url?: string;
	featured: boolean;
	expose_on_public_api: boolean;
	sort_order: number;
	created_at: string;
	updated_at: string;
};

export type ProjectPublicationInput = Pick<
	ProjectPublication,
	'citation' | 'title' | 'publication_year' | 'doi' | 'url' | 'featured' | 'expose_on_public_api' | 'sort_order'
>;

export async function listProjectPublications(
	projectId: number,
	fetchImpl?: typeof fetch
): Promise<ProjectPublication[]> {
	return apiRequest<ProjectPublication[]>(
		`/api/projects/${projectId}/publications/`,
		{ method: 'GET' },
		fetchImpl
	);
}

export async function createProjectPublication(
	projectId: number,
	payload: ProjectPublicationInput,
	fetchImpl?: typeof fetch
): Promise<ProjectPublication> {
	await ensureCsrfCookie(fetchImpl);
	return apiRequest<ProjectPublication>(
		`/api/projects/${projectId}/publications/`,
		{ method: 'POST', body: JSON.stringify(payload) },
		fetchImpl
	);
}

export async function updateProjectPublication(
	projectId: number,
	publicationId: number,
	payload: Partial<ProjectPublicationInput>,
	fetchImpl?: typeof fetch
): Promise<ProjectPublication> {
	await ensureCsrfCookie(fetchImpl);
	return apiRequest<ProjectPublication>(
		`/api/projects/${projectId}/publications/${publicationId}/`,
		{ method: 'PATCH', body: JSON.stringify(payload) },
		fetchImpl
	);
}

export async function deleteProjectPublication(
	projectId: number,
	publicationId: number,
	fetchImpl?: typeof fetch
): Promise<void> {
	await ensureCsrfCookie(fetchImpl);
	await apiRequest<void>(
		`/api/projects/${projectId}/publications/${publicationId}/`,
		{ method: 'DELETE' },
		fetchImpl
	);
}
