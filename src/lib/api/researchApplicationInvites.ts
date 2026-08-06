import { PUBLIC_DJANGO_API_BASE_URL } from '$env/static/public';
import { djangoAdminHomeUrl } from '$lib/api/djangoAdmin';

const API_BASE_URL = PUBLIC_DJANGO_API_BASE_URL || 'http://localhost:8000';

export type ClaimInvitePayload = {
	token: string;
	username: string;
	password: string;
	password_confirm: string;
};

export type ClaimInviteResponse = {
	username: string;
	project_id: number;
	project_slug: string;
	application_id: number;
	admin_login_url: string;
	detail: string;
};

export async function claimResearchApplicationInvite(
	payload: ClaimInvitePayload,
	fetchImpl: typeof fetch = fetch
): Promise<ClaimInviteResponse> {
	const response = await fetchImpl(`${API_BASE_URL}/api/public/research-application-invites/claim/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	const text = await response.text();
	let data: unknown = {};
	if (text) {
		try {
			data = JSON.parse(text);
		} catch {
			data = { detail: text };
		}
	}

	if (!response.ok) {
		const err = new Error(
			typeof data === 'object' && data && 'detail' in data
				? String((data as { detail: unknown }).detail)
				: `API ${response.status}`
		) as Error & { status?: number; body?: unknown };
		err.status = response.status;
		err.body = data;
		throw err;
	}

	const result = data as ClaimInviteResponse;
	if (!result.admin_login_url) {
		result.admin_login_url = djangoAdminHomeUrl();
	}
	return result;
}
