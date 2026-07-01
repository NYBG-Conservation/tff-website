export type ResearchHighlight = {
	title: string;
	summary: string;
	slug: string;
	ongoing: boolean;
};

export const researchHighlights: ResearchHighlight[] = [
	{
		title: 'CFI',
		summary:
			'Long-running transect sampling of trees, shrubs, and herbaceous cover across the forest.',
		slug: 'forest-inventory-transect-study',
		ongoing: true
	},
	{
		title: 'Knotweed Management Study',
		summary:
			'Collaborative invasive species management trial for Japanese knotweed control along the Bronx River.',
		slug: 'knotweed-management-study',
		ongoing: true
	},
	{
		title: 'Forest Soil Monitoring',
		summary:
			'Soil sampling and nutrient analysis in partnership with the Forest Ecosystem Monitoring Cooperative.',
		slug: 'soil-monitoring',
		ongoing: true
	}
];
