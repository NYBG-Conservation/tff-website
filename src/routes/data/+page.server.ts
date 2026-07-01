import { getCurrentUser } from '$lib/api/accounts';
import { fetchPublicDatasets, fetchPublicProjects } from '$lib/api/public';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const projectSlug = url.searchParams.get('project') ?? '';
	let isAuthenticated = false;

	try {
		const [researchProjects, datasetRecords] = await Promise.all([
			fetchPublicProjects(fetch),
			fetchPublicDatasets('', fetch)
		]);

		try {
			const currentUser = await getCurrentUser(fetch);
			isAuthenticated = Boolean(currentUser?.id);
		} catch {
			// Anonymous visitors see the sign-in note under manage links.
		}

		return {
			researchProjects,
			datasetRecords,
			projectSlug,
			isAuthenticated,
			apiError: null as string | null
		};
	} catch (err) {
		const message = err instanceof Error ? err.message : 'Unable to load dataset records.';
		return {
			researchProjects: [],
			datasetRecords: [],
			projectSlug,
			isAuthenticated: false,
			apiError: message
		};
	}
};
