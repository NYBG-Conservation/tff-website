import { fetchPublicDatasets, fetchPublicProjects } from '$lib/api/public';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const projectSlug = url.searchParams.get('project') ?? '';

	try {
		const [researchProjects, datasetRecords] = await Promise.all([
			fetchPublicProjects(fetch),
			fetchPublicDatasets(projectSlug, fetch)
		]);
		return { researchProjects, datasetRecords, projectSlug, apiError: null as string | null };
	} catch (err) {
		const message = err instanceof Error ? err.message : 'Unable to load dataset records.';
		return { researchProjects: [], datasetRecords: [], projectSlug, apiError: message };
	}
};
