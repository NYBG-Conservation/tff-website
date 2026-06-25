import { fetchPublicDatasets, fetchPublicProjects, fetchPublicPublications } from '$lib/api/public';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const [researchProjects, publicDatasets, featuredPublications, publicPublications] = await Promise.all([
			fetchPublicProjects(fetch),
			fetchPublicDatasets('', fetch),
			fetchPublicPublications({ featured: true }, fetch),
			fetchPublicPublications({}, fetch)
		]);
		return {
			researchProjects,
			publicDatasets,
			featuredPublications,
			publicPublications,
			apiError: null as string | null
		};
	} catch (err) {
		const message = err instanceof Error ? err.message : 'Unable to load research data.';
		return {
			researchProjects: [],
			publicDatasets: [],
			featuredPublications: [],
			publicPublications: [],
			apiError: message
		};
	}
};
