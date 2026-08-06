import { PUBLIC_DJANGO_API_BASE_URL } from '$env/static/public';

const API_BASE_URL = PUBLIC_DJANGO_API_BASE_URL || 'http://localhost:8000';

export type PublicOrganization = {
	id: number;
	name: string;
};

export async function fetchPublicOrganizations(
	fetchImpl: typeof fetch = fetch
): Promise<PublicOrganization[]> {
	const response = await fetchImpl(`${API_BASE_URL}/api/public/organizations/`);
	if (!response.ok) {
		throw new Error(`API ${response.status}: could not load organizations`);
	}
	return (await response.json()) as PublicOrganization[];
}
