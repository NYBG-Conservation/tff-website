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
		id: 'transect-db-2024',
		title: 'Transect Tree and Shrub Measurements',
		organization: 'NYBG Forest Program',
		cadence: 'Annual',
		status: 'Active',
		lastUpdated: '2025-11-19',
		projectId: 'forest-inventory-transect-study'
	},
	{
		id: 'canopy-gap-regeneration-2023',
		title: 'Canopy Gap Seedling Regeneration Survey',
		organization: 'NYBG Forest Program',
		cadence: 'Annual',
		status: 'Active',
		lastUpdated: '2025-10-03',
		projectId: 'filling-in-the-gaps'
	},
	{
		id: 'salamander-coverboards-2010-present',
		title: 'Redback Salamander Coverboard Counts',
		organization: 'NYBG + Volunteer Monitoring',
		cadence: 'Continuous',
		status: 'Active',
		lastUpdated: '2026-02-14',
		projectId: 'redback-salamander-monitoring'
	},
	{
		id: 'phenology-observations',
		title: 'Citizen Phenology Observation Records',
		organization: 'NY Phenology Network',
		cadence: 'Continuous',
		status: 'Active',
		lastUpdated: '2026-03-09',
		projectId: 'citizen-science-phenology-monitoring'
	},
	{
		id: 'knotweed-treatment-plots',
		title: 'Knotweed Treatment Plot Outcomes',
		organization: 'Bronx River Alliance',
		cadence: 'Annual',
		status: 'Active',
		lastUpdated: '2025-09-27',
		projectId: 'knotweed-management-study'
	},
	{
		id: 'bronx-river-macroinvertebrates',
		title: 'Macroinvertebrate Taxa and Water Quality',
		organization: 'Bronx River Alliance',
		cadence: 'Annual',
		status: 'Active',
		lastUpdated: '2025-12-05',
		projectId: 'macroinvertebrate-monitoring'
	},
	{
		id: 'forest-index-method-notes',
		title: 'Continuous Forest Index Method Development',
		organization: 'NYBG Forest Program',
		cadence: 'One-off',
		status: 'Planned',
		lastUpdated: '2026-01-20',
		projectId: 'continuous-forest-index-2026'
	}
];
