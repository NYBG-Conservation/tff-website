import { PUBLIC_DJANGO_API_BASE_URL } from '$env/static/public';

const API_BASE_URL = PUBLIC_DJANGO_API_BASE_URL || 'http://localhost:8000';

export type PublicResearchProject = {
	slug: string;
	title: string;
	full_title?: string;
	summary: string;
	descriptionParagraphs: string[];
	datasetIds: string[];
	external_url?: string;
	lead_name?: string;
	lead_email?: string;
	organization_name?: string;
	institutional_partners?: string[];
	ongoing: boolean;
	collection_frequency?: string;
	update_frequency?: string;
};

export type PublicDatasetRecord = {
	id: number;
	title: string;
	description?: string;
	organization: string;
	project_slug: string;
	cadence: string;
	status: string;
	last_updated: string;
	data_type?: string;
};

export type PublicPublicationRecord = {
	id: number;
	citation: string;
	title?: string;
	publication_year?: number | null;
	doi?: string;
	url?: string;
	featured: boolean;
	project_slug?: string | null;
};

type PublicProjectApi = Omit<PublicResearchProject, 'descriptionParagraphs'> & {
	description_paragraphs: string[];
};

type PublicDatasetApi = PublicDatasetRecord;

function mapProject(project: PublicProjectApi): PublicResearchProject {
	return {
		...project,
		descriptionParagraphs: project.description_paragraphs ?? []
	};
}

export function getPublicApiBaseUrl(): string {
	return API_BASE_URL;
}

export async function fetchPublicProjects(fetchImpl: typeof fetch = fetch): Promise<PublicResearchProject[]> {
	const response = await fetchImpl(`${API_BASE_URL}/api/public/projects/`);
	if (!response.ok) {
		throw new Error(`Public projects API ${response.status}: ${await response.text()}`);
	}
	const data = (await response.json()) as PublicProjectApi[];
	return data.map(mapProject);
}

export async function fetchPublicDatasets(
	projectSlug = '',
	fetchImpl: typeof fetch = fetch
): Promise<PublicDatasetRecord[]> {
	const query = projectSlug ? `?project=${encodeURIComponent(projectSlug)}` : '';
	const response = await fetchImpl(`${API_BASE_URL}/api/public/datasets/${query}`);
	if (!response.ok) {
		throw new Error(`Public datasets API ${response.status}: ${await response.text()}`);
	}
	return (await response.json()) as PublicDatasetApi[];
}

export async function fetchPublicPublications(
	options: { featured?: boolean; projectSlug?: string } = {},
	fetchImpl: typeof fetch = fetch
): Promise<PublicPublicationRecord[]> {
	const params = new URLSearchParams();
	if (options.featured) {
		params.set('featured', 'true');
	}
	if (options.projectSlug) {
		params.set('project', options.projectSlug);
	}
	const query = params.toString() ? `?${params.toString()}` : '';
	const response = await fetchImpl(`${API_BASE_URL}/api/public/publications/${query}`);
	if (!response.ok) {
		throw new Error(`Public publications API ${response.status}: ${await response.text()}`);
	}
	return (await response.json()) as PublicPublicationRecord[];
}
