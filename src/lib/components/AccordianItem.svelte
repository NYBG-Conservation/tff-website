<script lang="ts">
	import { slide } from 'svelte/transition';

	const muirImage = '/imgs/mw-for-web.png';
	const processImage = '/imgs/processdiag-transparent.png';

	export let i: number;
	export let show: number | null;
	export let showCollapse: (index: number) => void;
	export let item: string;
	export let text: string | string[] | unknown[];
	export let type: string;
	export let theme: 'dark' | 'light' = 'dark';

	let lesson_data = [
		{
			lesson: 0,
			title: 'Introductory lesson',
			description:
				"Students use maps and images to understand the basic idea of comparing the natural history of 1609 Mannahatta with the urbanized present of Manhattan.  We recommend that this lesson be taught before any others in order to give students a sense of the territory they'll be covering in future lessons.",
			file: 'intro_lesson1.zip',
			overview_file: 'background_intro.pdf'
		},
		{
			lesson: 1,
			title: 'Tracing Mannahatta',
			description:
				'Students trace historic natural features from old Manhattan, and layer them over the modern street grid in order to see how the land has changed over time.  Through this lesson, students will come to understand how much information they can learn just from close examination of visual evidence.',
			file: 'lesson_1_tracing.zip',
			overview_file: 'mannahatta_intro_lesson.pdf'
		},
		{
			lesson: 2,
			title: 'Weaving a Mannahatta Muir Web',
			description:
				'Students use their bodies and ribbon to create a web of habitats, species and abiotic elements that were present on Mannahatta.  Through this lesson, they learn about the interconnectedness and interdependence of life.',
			file: 'lesson_2_muir_web.zip',
			overview_file: 'background2.pdf'
		},
		{
			lesson: 3,
			title: 'The Changing Life of a Water Droplet',
			description:
				'Students pretend they are water droplets moving through the water cycle first on the Mannahatta of 1609, and next on modern Manhattan.  This lesson teaches students about how humans have affected the movement of water, and what that can mean for the environment.',
			file: 'lesson_3_water.zip',
			overview_file: 'background3.pdf'
		},
		{
			lesson: 4,
			title: 'Field Trip - Uncovering Streams in Central Park',
			description:
				'This field trip, in which students uncover an ancient stream in Central Park, reinforces what students have learned in the first three lessons about mapping, habitats, species and water on Mannahatta.',
			file: 'lesson_4_central_park1.zip',
			overview_file: 'background4.pdf'
		},
		{
			lesson: 5,
			title: 'Island of Many Hills',
			description:
				"Students build clay models of sections of Mannahatta, then learn how to create contour maps based on their models. This lesson uses basic math and graphing skills to help students understand how the island's topography has changed from 1609 to today.",
			file: 'lesson_5_hills.zip',
			overview_file: 'background5.pdf'
		},
		{
			lesson: 6,
			title: 'The Mighty Beaver',
			description:
				'In this lesson, students act out the roles of the different species that can live along and in streams and wetlands of Mannahatta. They learn how beavers alter the landscape and, in so doing, create new habitats for new species.',
			file: 'lesson_6_beaver1.zip',
			overview_file: 'background6.pdf'
		},
		{
			lesson: 7,
			title: 'The Search for Lenape Campsites',
			description:
				'The native people of Mannahatta, the Lenape, chose their campsites based on their proximity to what they needed to live: food, water, and shelter.  In this lesson, students pretend they are Lenape families, working together to search for the best campsites on Mannahatta.',
			file: 'lesson_7_lenape.zip',
			overview_file: 'background7.pdf'
		},
		{
			lesson: 8,
			title: 'Field Trip - Exploring Inwood Hill Park',
			description:
				'On this field trip, in which students explore the forest and salt marsh of Inwood Hill Park, students reinforce what they have learned in this module about topography, native habitats and Lenape life on Mannahatta.',
			file: 'lesson_8_inwood.zip',
			overview_file: 'background8.pdf'
		},
		{
			lesson: 9,
			title: 'Migration, Immigration and the Importance of Diversity',
			description:
				'Students use bird migration to compare the biodiversity of 1609 Mannahatta with the cultural diversity of New York City today. In this lesson, students learn about the importance of diversity to natural and human environments.',
			file: 'lesson_9_diversity.zip',
			overview_file: 'background9.pdf'
		},
		{
			lesson: 10,
			title: 'The Eco-History of Our Block',
			description:
				"Students use the Mannahatta website to learn about the ecological history of particular blocks on the island of Mannahatta-and then compare what they've learned with what exists there today.",
			file: 'lesson_10_eco-history.zip',
			overview_file: 'background10.pdf'
		},
		{
			lesson: 11,
			title: 'Designing the City of the Future',
			description:
				"Based on what they have learned from studying the history of Mannahatta, students design the city they hope will exist 400 years in the future, focusing on the city's waterfront.",
			file: 'lesson_11_future.zip',
			overview_file: 'background11.pdf'
		},
		{
			lesson: 12,
			title: 'Field Trip - Stuyvesant Town: Building a City on the Island',
			description:
				"On this field trip, students search for all the orignial ecological communities in what is now the Stuyvesant Town section of Manhattan. Students learn about how people changed the shape of Mannahatta island, and think about how people will continue to shape the island into the future. They pay particular attention to how the island's waterfront has changed over the years, and what its future possibilities are.",
			file: 'lesson_12_stuytown.zip',
			overview_file: 'background12.pdf'
		}
	];

	let splitted: string[] = [];
	if (typeof text === 'object' && text !== null && Array.isArray(text) && typeof text[0] === 'string') {
		splitted = text[0].split(',');
	}
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="collapse__header" class:theme-light={theme === 'light'} on:click={() => showCollapse(i)}>
	<span>{item}</span>
	<span class="icon-spot">
		{#if show === i}
			<svg
				class="chevron-icon"
				xmlns="http://www.w3.org/2000/svg"
				width="26"
				height="26"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				aria-hidden="true"
			>
				<polyline points="18 15 12 9 6 15" />
			</svg>
		{:else}
			<svg
				class="chevron-icon"
				xmlns="http://www.w3.org/2000/svg"
				width="26"
				height="26"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				aria-hidden="true"
			>
				<polyline points="6 9 12 15 18 9" />
			</svg>
		{/if}
	</span>
</div>
{#if show === i}
	<div class="collapse__body" class:theme-light={theme === 'light'} transition:slide>
		{#if typeof text == 'object'}
			<ul class="ed-list">
				{#each splitted as o}
					<li>
						<h3>
							{parseInt(o) != 0 ? 'Lesson ' + parseInt(o) + ': ' : ''}{lesson_data[parseInt(o)][
								'title'
							]}
						</h3>
						<span class="ed-link"
							>{#if lesson_data[parseInt(o)]['overview_file'] && lesson_data[parseInt(o)]['overview_file'] !== ''}
								<a
									href="/education_data/{lesson_data[parseInt(o)]['overview_file']}"
									target="_blank">Lesson plan</a
								>
								|
							{/if}
							<a href="/education_data/{lesson_data[parseInt(o)]['file']}">Materials</a></span
						>
						<p class="ed-desc">{lesson_data[parseInt(o)]['description']}</p>
					</li>
				{/each}
			</ul>
		{:else if type == 'files'}
			{@html text}
		{:else if text == '1'}
			<div style="text-align: center"></div>
			<p class="ed-desc">
				To construct our historical ecology dataset, we began with a collection of historical maps
				that described the original features of city. We then added information from soil surveys,
				tree rings, descriptions of plant life and animal life, historical accounts, and field
				surveys.
			</p>
			<p class="ed-desc">
				From there, we georeferenced the information into a single base map, the 1782 British
				Headquarters map from The National Archives in the United Kingdom. The georeferenced points
				were loaded to a geographic information system (GIS) database, in this case, the most
				complete description of a landscape ever attempted. For the other boroughs, we are using a
				combination of maps from the 18th and 19th centuries to carefully reconstruct the forgotten
				landscape.
			</p>
		{:else if text == '2'}
			<div style="text-align: center">
				<img
					src={muirImage}
					width="80%"
					style="margin: 1rem auto 1rem auto"
					alt="A data visualization of a large network."
				/>
			</div>

			<p class="ed-desc">
				The Muir web is a complex network model representing over 8,000 complex and intertwined
				relationships between the inhabitants of Mannahatta and Welikia. Named after John Muir, a
				California naturalist who emphasized the interconnection of all beings in nature, this web
				includes not only living species and habitats but also abiotic elements, such as water, sun,
				soil, and air. We use this network of relationships to predict the distribution of plants,
				animals, and other ecological factors in the past.
			</p>
		{:else if text == '0'}
			<p class="ed-desc">
				Our starting point to reconstruct Mannahatta was geolocating the 18th century British
				Headquarters Map to the modern street grid of New York. We found over 200 control points
				where we could locate features on the map (e.g. streams, hills, ponds) to their current
				locations. The final composition was accomplished with an error of approximately 40 meters,
				or about half an uptown block in midtown. Georeferencing the British Headquarters Map with
				this level of accuracy means that all data layers derived from it are equivalently spatially
				accurate, allowing us to estimate the distribution of ecological features block by block
				across the city.
			</p>
			<p class="ed-desc">
				For the rest of the city, without an equivalent basemap, we needed to synthesize information
				from many different sources into one composite base map to work with. Fortunately, because
				development of the rest of the city (except for parts of Brooklyn) began later than that of
				Manhattan, we are able to use maps through most of the 19th century to detect old streams,
				hills and shorelines that have since been erased by development.
			</p>

			<div style="text-align: center">
				<img
					src={processImage}
					alt="A diagram of our workflow for the Welikia Project."
					width="100%"
					style="margin:auto; max-width: 370px;"
				/>
			</div>
		{/if}
	</div>
{/if}

<style>
	.ed-list {
		padding: 0em;
	}
	.ed-link {
		display: none;
	}

	.ed-link a,
	.ed-link {
		color: var(--helleborus);
		text-transform: uppercase;
		text-decoration: none;
		font-family: 'GT Super Regular', serif;
	}

	h3 {
		text-align: left;
		color: white !important;
		color: white;
		font-family: 'GT Super Regular', serif;
		font-weight: 400;
		font-size: 1.2rem;
	}

	.ed-desc {
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
	}

	.collapse__header {
		padding: 1.2rem 0 0rem 0;
		border-bottom: 2px solid var(--light);
		color: var(--light);
		font-family: 'GT Super Bold', serif;
		transition: background 200ms ease-in-out;
		font-size: 1.2rem;
		justify-content: space-between;
		vertical-align: middle;
		display: flex;
	}
	.collapse__header:hover {
		/* background: #f7f7f7; */
		cursor: pointer;
	}

	.collapse__header.theme-light {
		padding: 0.85rem 0 0.65rem;
		border-bottom: 1px solid rgba(0, 0, 0, 0.15);
		color: #1e2f1e;
		font-family: 'GT Super Bold', serif;
		font-size: 1.05rem;
	}

	.collapse__header.theme-light:hover {
		color: #111;
	}

	.collapse__body.theme-light {
		padding: 0.75rem 0 0.25rem;
		color: #222;
	}

	.collapse__body.theme-light :global(.resource-list) {
		margin: 0;
		padding-left: 1.25rem;
	}

	.collapse__body.theme-light :global(.resource-list li) {
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		line-height: 1.55;
		margin-bottom: 0.55rem;
	}

	.collapse__body {
		padding: 1rem;
		/* background: #f0f0f0; */
		font-family: 'GT Super', serif;
		font-size: 1rem;
		color: var(--light);
	}

	.collapse__body img {
		margin: auto;
	}

	.icon-spot {
		/* text-align: right; */
		vertical-align: middle;
	}

	@media (min-width: 768px) {
		.ed-link {
			display: block;
		}
	}
</style>
