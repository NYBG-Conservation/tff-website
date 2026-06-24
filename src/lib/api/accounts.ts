import { apiRequest } from './client';

export type UserRole =
	| 'internal_superadmin'
	| 'internal_admin'
	| 'external_superadmin'
	| 'external_admin';

export type CurrentUser = {
	id: number;
	username: string;
	email: string;
	role: UserRole | null;
	organization_id: number | null;
	organization_name: string | null;
	can_assign_roles: boolean;
};

export type AssignRolePayload = {
	username: string;
	role: UserRole;
	organization?: number | null;
};

export async function getCurrentUser(fetchImpl?: typeof fetch): Promise<CurrentUser> {
	return apiRequest<CurrentUser>('/api/accounts/me/', { method: 'GET' }, fetchImpl);
}

export async function assignRole(
	payload: AssignRolePayload,
	fetchImpl?: typeof fetch
): Promise<{
	username: string;
	role: UserRole;
	organization_id: number | null;
	organization_name: string | null;
}> {
	return apiRequest('/api/accounts/assign-role/', { method: 'POST', body: payload }, fetchImpl);
}
