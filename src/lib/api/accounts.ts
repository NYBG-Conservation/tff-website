import { apiRequest } from './client';

export type CurrentUser = {
	id: number;
	username: string;
	email: string;
	role: 'internal_admin' | 'external_partner_admin' | null;
};

export async function getCurrentUser(fetchImpl?: typeof fetch): Promise<CurrentUser> {
	return apiRequest<CurrentUser>('/api/accounts/me/', { method: 'GET' }, fetchImpl);
}
