<script lang="ts">
	const naturalHistoryBase =
		'ColProjectsLocal_tab=Natural%20History%20of%20the%20New%20York%20Botanical%20Garden';
	const narrativesPurpose = 'DesPurpose=Natural%20History%20of%20the%20New%20York%20Botanical%20Garden';

	const plantLinks = [
		{
			label: 'Fungi',
			href: `https://sweetgum.nybg.org/science/vh/specimen-list/?${naturalHistoryBase}&SpeDivision=Fungi`
		},
		{
			label: 'Lichens',
			href: `https://sweetgum.nybg.org/science/vh/specimen-list/?${naturalHistoryBase}&SpeDivision=Lichens`
		},
		{
			label: 'Hepatics',
			href: `https://sweetgum.nybg.org/science/vh/specimen-list/?${naturalHistoryBase}&SpeDivision=Hepatics`
		},
		{
			label: 'Mosses',
			href: `https://sweetgum.nybg.org/science/vh/specimen-list/?${naturalHistoryBase}&SpeDivision=Mosses`
		},
		{
			label: 'Ferns',
			href: `https://sweetgum.nybg.org/science/vh/specimen-list/?${naturalHistoryBase}&DarPhylum=Pteridophyta`
		},
		{
			label: 'Conifers',
			href: `https://sweetgum.nybg.org/science/vh/specimen-list/?${naturalHistoryBase}&DarPhylum=Pinophyta`
		},
		{
			label: 'Flowering Plants',
			href: `https://sweetgum.nybg.org/science/vh/specimen-list/?${naturalHistoryBase}&DarPhylum=Magnoliophyta`
		}
	];

	const animalLinks = [
		{
			label: 'Fish',
			href: `https://sweetgum.nybg.org/science/vh/narratives-list/?DesType_tab=Fish&${narrativesPurpose}`
		},
		{
			label: 'Birds',
			href: `https://sweetgum.nybg.org/science/vh/narratives-list/?DesType_tab=Birds&${narrativesPurpose}`
		},
		{
			label: 'Reptiles',
			href: `https://sweetgum.nybg.org/science/vh/narratives-list/?DesType_tab=Reptiles&${narrativesPurpose}`
		},
		{
			label: 'Amphibians',
			href: `https://sweetgum.nybg.org/science/vh/narratives-list/?DesType_tab=Amphibians&${narrativesPurpose}`
		}
	];
</script>

<section class="about-content">
	<section class="page-section" aria-labelledby="about-overview-heading">
		<div class="section-body">
			<p class="body-paragraph">
				For thousands of years, this old-growth Forest has changed, adapted and survived. When you visit
				the Forest, you will walk along Native American hunting trails, see marks left by glaciers, and
				pass under trees dating back to the American Revolution. The unique beauty and ecological
				importance of the forest are one of the reasons why the founders selected this site for The New
				York Botanical Garden in 1895.
			</p>
			<p class="body-paragraph">
				Today this is the largest uncut expanse of New York's original wooded landscape. The Forest
				remains a magnificent reminder of the beauty and resilience of nature in the face of complex
				human-caused disturbances. To preserve the Forest for future generations the Garden manages
				invasive species, plants native plants, and performs research.
			</p>
			<p class="body-paragraph">
				Download the
				<a
					href="https://www.nybg.org/content/uploads/2017/04/Forest-Plan-2016.pdf"
					target="_blank"
					rel="noopener noreferrer"
				>Thain Family Forest Program 2008-2025</a>
				to learn more about ongoing forest restoration, education, and research.
			</p>
		</div>
	</section>

	<section class="page-section" aria-labelledby="natural-history-heading">
		<h2 id="natural-history-heading" class="section-heading">Natural History of the Forest</h2>
		<div class="section-body">
			<p class="body-paragraph">
				On May 24, 1895 the northern portion of Bronx Park was chosen by a selected committee of the
				Scientific Board of Directors and cited in a letter to the board from Nathaniel Lord Britton as
				follows: &ldquo;Your committee would therefore recommend the selection of the northern end of
				Bronx Park as this site for the Garden, for the reasons that it combines all the desirable
				elements of ready accessibility, rich and varied soils, grand natural scenery, [and a] dense
				natural forest.&rdquo;
			</p>
			<p class="body-paragraph">
				In 1898, the first checklist of plants living on the Grounds was published in the
				<em>Journal of The New York Botanical Garden</em>. This checklist was followed by many articles
				about the site, the Hemlock Forest, and the development of the Garden. The study of the region
				continued with local floras for the City of New York and its vicinity, geologic and soil surveys,
				and beyond. In 1924, the Olmsted Brothers reported: &ldquo;The most notable natural feature of
				the Botanical Garden, perhaps as a matter of botany and certainly as a matter of landscape, is
				the gorge of the Bronx River with its wild growth of hemlocks and associated plants, its
				picturesque precipitous slopes and ledges, its sense of remoteness and seclusion from the city
				and most of the works of men.&rdquo;
			</p>
			<p class="body-paragraph">
				Since the Garden&rsquo;s establishment, Garden staff, visiting experts, and enthusiastic members
				of the public have studied the history, wildlife, plant life, geology, climate, soils, and
				ecology of the Garden. All of these studies have been performed separately and have never been
				documented in one place. As part of the new Forest Program, Garden staff and visiting experts are
				creating a Natural History of The New York Botanical Garden to document the physical setting,
				biota, ecology, management, and ethnobotany of the site as stated in the outline below. The site
				is defined as all natural areas within the Garden including the Forest, Twin Lakes, South
				Arboretum, portion of land between the Rose Garden and Bronx River Parkway perimeter fence, rock
				outcrops, etc. The goal is to study spontaneous nature at the Garden.
			</p>

			<h3 class="subsection-heading">Plants</h3>
			<ul class="resource-list">
				{#each plantLinks as link}
					<li>
						<a href={link.href} target="_blank" rel="noopener noreferrer">{link.label}</a>
					</li>
				{/each}
			</ul>

			<h3 class="subsection-heading">Animals</h3>
			<ul class="resource-list">
				{#each animalLinks as link}
					<li>
						<a href={link.href} target="_blank" rel="noopener noreferrer">{link.label}</a>
					</li>
				{/each}
			</ul>
		</div>
	</section>
</section>


<style>
	.about-content {
		max-width: 1400px;
		margin: 2rem auto;
		padding: 0 1rem 3rem;
	}

	.page-section {
		max-width: 1100px;
		margin: 0 auto 2.5rem;
	}

	.body-paragraph {
		font-family: 'GT Super Regular', serif;
		font-size: 1.05rem;
		line-height: 1.6;
		margin: 0 0 1rem;
		color: #222;
	}

	.section-heading {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.35rem, 2.2vw, 2rem);
		text-transform: uppercase;
		line-height: 1.1;
		margin: 0 0 1rem;
		color: #1e2f1e;
	}

	.subsection-heading {
		font-family: 'GT Super Bold', serif;
		font-size: 1.05rem;
		margin: 1.5rem 0 0.65rem;
		color: #1e2f1e;
	}

	.resource-list {
		margin: 0 0 1rem;
		padding-left: 1.25rem;
	}

	.resource-list li {
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		line-height: 1.55;
		margin-bottom: 0.55rem;
	}
</style>
