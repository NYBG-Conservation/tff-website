import { fetchPublicDatasets, fetchPublicProjects } from '$lib/api/public';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const [researchProjects, publicDatasets] = await Promise.all([
			fetchPublicProjects(fetch),
			fetchPublicDatasets('', fetch)
		]);
		return { researchProjects, publicDatasets, apiError: null as string | null };
	} catch (err) {
		const message = err instanceof Error ? err.message : 'Unable to load research data.';
		return { researchProjects: [], publicDatasets: [], apiError: message };
	}
};
