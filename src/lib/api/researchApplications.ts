import { PUBLIC_DJANGO_API_BASE_URL } from '$env/static/public';

const API_BASE_URL = PUBLIC_DJANGO_API_BASE_URL || 'http://localhost:8000';

export type ResearchProjectType = 'Plant_material_collections' | 'onsite_research';
export type ResearchCollectionType =
	| 'on-site_collection'
	| 'off-site_collection'
	| 'other'
	| '';

export type ResearchApplicationPayload = {
	website?: string;
	applicant_name: string;
	title_position?: string;
	institution: string;
	email: string;
	phone?: string;
	address?: string;
	co_pi?: string;
	project_title: string;
	project_type: ResearchProjectType;
	description: string;
	start_date?: string;
	end_date?: string;
	anticipated_start_date?: string;
	anticipated_end_date?: string;
	desired_species?: string;
	collection_type?: ResearchCollectionType;
	research_location?: string;
	plant_tracker_notes?: string;
	abiotic_variables?: string;
	biotic_variables?: string;
	funding_sources?: string;
	wildlife_permits?: string;
	nybg_infrastructure?: string;
	site_visits?: string;
	visitor_impacts?: string;
	research_sensitivity?: string;
	resources?: string;
	publications?: string;
	additional_comments?: string;
	attestation_name: string;
	attestation_date: string;
};

export type ResearchApplicationResponse = {
	id: number;
	status: string;
	detail: string;
};

export async function submitResearchApplication(
	payload: ResearchApplicationPayload,
	fetchImpl: typeof fetch = fetch
): Promise<ResearchApplicationResponse> {
	const response = await fetchImpl(`${API_BASE_URL}/api/public/research-applications/`, {
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

	return data as ResearchApplicationResponse;
}
