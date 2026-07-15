<script lang="ts">
	import CustomHero from '$lib/components/CustomHero.svelte';
	import ResearchProjectCard from '$lib/components/ResearchProjectCard.svelte';
	import { researchHighlights } from '$lib/data/researchHighlights';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<CustomHero heroImage={data.announcements?.[0]?.image} />
<div class="homepage-content">
	<h2 class="highlights-heading">Research highlights</h2>
	<section class="highlights-grid">
		{#each researchHighlights as highlight}
			<ResearchProjectCard
				title={highlight.title}
				summary={highlight.summary}
				ongoing={highlight.ongoing}
				leadName={highlight.leadName}
				href={`/research?project=${encodeURIComponent(highlight.slug)}`}
			/>
		{/each}
	</section>
</div>

<style>
	.homepage-content {
		width: 100%;
		background-color: #f4f4f4;
		padding: 4rem 0;
	}

	.highlights-heading {
		max-width: 1400px;
		margin: 0 auto 1.25rem;
		padding: 0 1rem;
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.3rem, 3vw, 2.3rem);
		line-height: 1.1;
		text-transform: uppercase;
		text-align: center;
		color: #1e2f1e;
	}

	.highlights-grid {
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 1rem;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1.5rem;
	}

	@media (max-width: 900px) {
		.homepage-content {
			padding: 3rem 0;
		}

		.highlights-grid {
			grid-template-columns: 1fr;
			max-width: 700px;
		}
	}
</style>
