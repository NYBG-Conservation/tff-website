import { apiRequest, ensureCsrfCookie } from './client';

export type ProjectManager = {
	id: number;
	user: number;
	username: string;
	added_by?: number | null;
	added_by_username?: string;
	created_at: string;
};

export type Project = {
	id: number;
	short_title: string;
	full_title?: string;
	nybg_pi_name: string;
	external_pi_name?: string;
	shared_publicly: boolean;
	start_date?: string;
	end_date?: string;
	ongoing: boolean;
	lead_institution?: number;
	lead_institution_name?: string;
	contact_email: string;
	external_url?: string;
	institutional_partners?: string[];
	collection_frequency?: string;
	update_frequency?: string;
	last_updated_note?: string;
	organization: number;
	owner: number;
	owner_username?: string;
	managers?: ProjectManager[];
	created_at: string;
	updated_at: string;
};

export type ProjectInput = Omit<Project, 'id' | 'owner_username' | 'created_at' | 'updated_at' | 'managers'> & {
	owner?: number;
};

export async function listProjects(query = '', fetchImpl?: typeof fetch): Promise<Project[]> {
	const suffix = query ? `?${query}` : '';
	return apiRequest<Project[]>(`/api/projects/${suffix}`, { method: 'GET' }, fetchImpl);
}

export async function createProject(payload: ProjectInput, fetchImpl?: typeof fetch): Promise<Project> {
	await ensureCsrfCookie(fetchImpl);
	return apiRequest<Project>(
		'/api/projects/',
		{
			method: 'POST',
			body: JSON.stringify(payload)
		},
		fetchImpl
	);
}

export async function updateProject(
	projectId: number,
	payload: Partial<ProjectInput>,
	fetchImpl?: typeof fetch
): Promise<Project> {
	await ensureCsrfCookie(fetchImpl);
	return apiRequest<Project>(
		`/api/projects/${projectId}/`,
		{
			method: 'PATCH',
			body: JSON.stringify(payload)
		},
		fetchImpl
	);
}

export async function addProjectManager(
	projectId: number,
	username: string,
	fetchImpl?: typeof fetch
): Promise<{ id: number; username: string }> {
	await ensureCsrfCookie(fetchImpl);
	return apiRequest<{ id: number; username: string }>(
		`/api/projects/${projectId}/managers/`,
		{
			method: 'POST',
			body: JSON.stringify({ username })
		},
		fetchImpl
	);
}

export async function removeProjectManager(
	projectId: number,
	userId: number,
	fetchImpl?: typeof fetch
): Promise<void> {
	await ensureCsrfCookie(fetchImpl);
	await apiRequest<void>(`/api/projects/${projectId}/managers/${userId}/`, { method: 'DELETE' }, fetchImpl);
}
