import { apiRequest, ensureCsrfCookie } from './client';

export type Organization = {
	id: number;
	name: string;
	contact_email?: string;
	website_url?: string;
	description?: string;
};

export async function listOrganizations(fetchImpl?: typeof fetch): Promise<Organization[]> {
	return apiRequest<Organization[]>('/api/organizations/', { method: 'GET' }, fetchImpl);
}

export async function createOrganization(
	payload: Pick<Organization, 'name'> & Partial<Pick<Organization, 'contact_email' | 'website_url' | 'description'>>,
	fetchImpl?: typeof fetch
): Promise<Organization> {
	await ensureCsrfCookie(fetchImpl);
	return apiRequest<Organization>(
		'/api/organizations/',
		{
			method: 'POST',
			body: JSON.stringify(payload)
		},
		fetchImpl
	);
}
