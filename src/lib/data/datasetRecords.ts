/** @deprecated Public pages load from `/api/public/datasets/` via `+page.server.ts`. */
export type DatasetRecord = {
	id: string;
	title: string;
	organization: string;
	cadence: 'Annual' | 'One-off' | 'Continuous';
	status: 'Planned' | 'Active' | 'Archived';
	lastUpdated: string;
	projectId?: string;
};

export const datasetRecords: DatasetRecord[] = [
	{
		id: 'knotweed-treatment-plots',
		title: 'Knotweed Treatment Plot Outcomes',
		organization: 'New York Botanical Garden, NYC Parks',
		cadence: 'Annual',
		status: 'Concluded',
		lastUpdated: '2026-04-23',
		projectId: 'knotweed-management-study'
	}
];
