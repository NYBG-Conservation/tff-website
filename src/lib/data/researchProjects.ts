/** @deprecated Public pages load from `/api/public/projects/` via `+page.server.ts`. */
export type ResearchProject = {
	id: string;
	image: string;
	title: string;
	summary: string;
	descriptionParagraphs: string[];
	datasetIds?: string[];
	archiveRecordIds?: string[];
};

// TODO: Reuse `id` as route param for future `/research/[projectId]` pages.
// TODO: Populate `archiveRecordIds` when the archives route and records are added.
export const researchProjects: ResearchProject[] = [
	{
		id: 'continuous-forest-index-2026',
		image: '/images/home/forest-canopy.png',
		title: '2026 Continuous Forest Index',
		summary: 'Longitudinal monitoring initiative tracking urban forest condition and restoration outcomes.',
		datasetIds: ['forest-index-method-notes'],
		descriptionParagraphs: [
			'This project is currently in development and will provide an integrated index for tracking forest condition across restoration zones in the Thain Family Forest.',
			'Dataset links will be added as the 2026 baseline and subsequent monitoring records are published.'
		]
	},
	{
		id: 'forest-inventory-transect-study',
		image: '/images/home/forest-trail.png',
		title: 'Forest Inventory Transect Study',
		summary: 'Long-running transect sampling of trees, shrubs, and herbaceous cover across the forest.',
		datasetIds: ['transect-db-2024'],
		descriptionParagraphs: [
			'Since 2001, Garden staff have been sampling fourteen 10-meter-wide transects across the Forest, from the western boundary to the Bronx River. Data collected includes all trees and shrubs that are 1 cm or greater in diameter at breast height (DBH at 4.5 feet), as well as herbaceous plants and tree seedling percent cover.',
			'These data are used to monitor how the Forest is changing, track invasive plant management, and prioritize ongoing restoration work such as native plant restoration. Results from the 2011 survey showed that Amur honeysuckle and Amur corktree management successfully removed the largest specimens, but small Amur corktree are still present. More recently, data have shown that Japanese angelica tree is increasing, and management efforts are now focused on that species.'
		]
	},
	{
		id: 'filling-in-the-gaps',
		image: '/images/home/forest-group.png',
		title: 'Filling in the Gaps: Plant Establishment After Hurricane Sandy',
		summary: 'Post-disturbance canopy gap study following Hurricane Sandy.',
		datasetIds: ['canopy-gap-regeneration-2023'],
		descriptionParagraphs: [
			"On October 29, 2012, Hurricane Sandy caused major structural damage to the Forest by uprooting or destroying 167 trees that were 6 inches DBH or greater, creating canopy gaps. While storms like hurricanes and nor'easters are part of the region's natural disturbance regime, Sandy was the most damaging storm in the recorded history of the Garden landscape.",
			'This study assesses newly formed canopy gaps, how plant species reestablish after disturbance, and how management should respond in disturbed areas. The project measures abundance and distribution of first-year tree and herbaceous seedling species in 10 canopy gaps. One-square-meter plots were placed within canopy gaps and intact forest along 10-meter transects north and south of each canopy gap center.'
		]
	},
	{
		id: 'redback-salamander-monitoring',
		image: '/images/home/forest-canopy.png',
		title: 'Long-term Redback Salamander Monitoring',
		summary: 'Indicator species monitoring for forest health in urban northeastern deciduous forest.',
		datasetIds: ['salamander-coverboards-2010-present'],
		descriptionParagraphs: [
			'The eastern redback salamander (Plethodon cinereus) can act as an indicator of forest health in northeastern deciduous forests. In 2010, a long-term monitoring study was established in the Thain Family Forest to document salamander abundance and distribution throughout the Forest.',
			"A blog post featuring a short documentary about this salamander study is available on NYBG's Plant Talk blog."
		]
	},
	{
		id: 'citizen-science-phenology-monitoring',
		image: '/images/home/forest-trail.png',
		title: 'Citizen Science Phenology Monitoring',
		summary: 'Volunteer-supported phenology observations to track climate-related seasonal changes.',
		datasetIds: ['phenology-observations'],
		descriptionParagraphs: [
			'To study climate change impacts on the Thain Family Forest, the Garden engages volunteers in collecting scientific data on specific tree species. With expert training, participants learn about eight native tree species and record seasonal biological processes (phenology), such as when leaves, flowers, and fruits appear.',
			'Working with partners at the National Phenology Network, New York Phenology Project, and the Northeast Regional Phenology Network, the Garden has tailored this program to support scientific research needs. The program also helps participants actively engage in plant biology, forest ecology, and related sciences while building intimate knowledge of the Thain Family Forest.',
			'If you would like to participate as a citizen scientist, please contact Volunteer Services.'
		]
	},
	{
		id: 'knotweed-management-study',
		image: '/images/home/forest-group.png',
		title: 'Knotweed Management Study',
		summary: 'Collaborative invasive species management trial for Japanese knotweed control.',
		datasetIds: ['knotweed-treatment-plots'],
		descriptionParagraphs: [
			'This study is a partnership with the Bronx River Alliance, the Natural Resources Group of the Department of Parks and Recreation, and Columbia University to determine best management practices for controlling Japanese knotweed and hybrid knotweed (Reynoutria x bohemica).',
			'Management techniques include cutting knotweed back three times per year, or cutting once and removing rhizomes twice per year. Data collection documents impacts on plant species diversity, plant percent cover, restoration tree establishment, and knotweed height and stem count. This project was supported by a WCS-NOAA Regional Partnership Grant (2009 to 2011) and remains ongoing from 2009 to present.'
		]
	},
	{
		id: 'macroinvertebrate-monitoring',
		image: '/images/home/forest-canopy.png',
		title: 'Macroinvertebrate Monitoring',
		summary: 'Community science stream biodiversity and water quality monitoring.',
		datasetIds: ['bronx-river-macroinvertebrates'],
		descriptionParagraphs: [
			'Freshwater streams are among the most biologically diverse ecosystems on Earth. They are interdependent with forests, flow into larger bodies of water, and are strongly impacted by overuse, pollution, and urbanization.',
			'This project involves students, visiting school groups, and citizen scientists in monitoring benthic macroinvertebrates (small animals living among sediments and stones at stream and river bottoms). Insects make up the largest diversity of these organisms, and their diversity is an indicator of water quality in the Forest stream along the Sweet Gum Trail and the Bronx River.',
			'Using Stroud Leaf Pack Network protocols, kick netting, and Bronx River Alliance water quality protocols, participants collect biodiversity and water quality data. These data help document the health and interdependence of the Forest stream and Bronx River ecosystem. This project is a partnership with Garden volunteers and the Bronx River Alliance, supported by WCS-NOAA Regional Partnership Grants (2011 to 2013), and remains ongoing from 2010 to present.',
			"If you would like to participate as a citizen scientist, please contact Volunteer Services.",
			"If you would like to participate in a teacher professional development workshop or have your school participate in this project, please contact Children's Education."
		]
	}
];
