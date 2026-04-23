import { apiRequest } from './client';

export type MetadataField = {
	id?: number;
	key: string;
	label: string;
	field_type: string;
	unit?: string;
	required?: boolean;
	allowed_values?: string[];
	sort_order?: number;
};

export type MetadataValue = {
	field_key: string;
	value: unknown;
};

export type Dataset = {
	id: number;
	title: string;
	description: string;
	cadence: 'annual' | 'one_off' | 'continuous';
	status: 'draft' | 'active' | 'archived';
	data_type?:
		| 'tabular'
		| 'geospatial'
		| 'image'
		| 'sensor_time_series'
		| 'biodiversity_observation'
		| 'document_archive';
	project_id?: string;
	organization: number;
	owner: number;
	owner_username?: string;
	additional_research_partners: string[];
	paper_links: string[];
	metadata_schema_version: number;
	data_collection_start?: string;
	data_collection_end?: string;
	projected_project_end_date?: string;
	metadata_fields: MetadataField[];
	resolved_metadata_values?: Array<{
		field_key: string;
		value: unknown;
	}>;
	publications?: Array<{
		id?: number;
		title: string;
		citation?: string;
		doi?: string;
		url?: string;
		publication_year?: number;
		notes?: string;
		attachment?: string;
	}>;
};

export type DatasetInput = Omit<Dataset, 'id' | 'owner_username' | 'resolved_metadata_values'> & {
	owner?: number;
	metadata_values?: MetadataValue[];
};

export type MetadataFieldType = {
	value: string;
	label: string;
};

export async function listDatasets(fetchImpl?: typeof fetch): Promise<Dataset[]> {
	return apiRequest<Dataset[]>('/api/datasets/', { method: 'GET' }, fetchImpl);
}

export async function createDataset(payload: DatasetInput, fetchImpl?: typeof fetch): Promise<Dataset> {
	return apiRequest<Dataset>(
		'/api/datasets/',
		{
			method: 'POST',
			body: JSON.stringify(payload)
		},
		fetchImpl
	);
}

export async function getMetadataFieldTypes(fetchImpl?: typeof fetch): Promise<MetadataFieldType[]> {
	return apiRequest<MetadataFieldType[]>('/api/metadata/field-types/', { method: 'GET' }, fetchImpl);
}
