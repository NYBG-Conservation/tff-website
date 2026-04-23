<script lang="ts">
	import CustomHero from '$lib/components/CustomHero.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const featureCards = [
		{
			image: '/images/home/forest-canopy.png',
			title: "Lorem ipsum",
			href: '/images/home/forest-canopy.png'
		},
		{
			image: '/images/home/forest-trail.png',
			title: 'Lorem ipsum',
			href: '/images/home/forest-trail.png'
		},
		{
			image: '/images/home/forest-group.png',
			title: 'Lorem ipsum',
			href: '/images/home/forest-group.png'
		}
	];
</script>

<CustomHero heroImage={data.announcements?.[0]?.image} />
<div class="homepage-content">
	<h2 class="feature-heading">Forest highlights</h2>
	<section class="feature-grid">
		{#if featureCards.length > 0}
			{#each featureCards as card}
				<article class="feature-card">
					<a class="feature-link" href={card.href}>
						<img src={card.image} alt={card.title} loading="lazy" />
						<h3 class="feature-title">{card.title}</h3>
					</a>
				</article>
			{/each}
		{:else}
			<article class="feature-card feature-card-fallback"></article>
			<article class="feature-card feature-card-fallback"></article>
			<article class="feature-card feature-card-fallback"></article>
		{/if}
	</section>
</div>

<style>
	.homepage-content {
		width: 100%;
		background-color: #f4f4f4;
		padding: 8rem 0 4rem;
	}

	.feature-heading {
		max-width: 1400px;
		margin: 0 auto 1.25rem;
		padding: 0 1rem;
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.5rem, 3vw, 2.5rem);
		line-height: 1.1;
		text-transform: uppercase;
		color: #1e2f1e;
	}

	.feature-grid {
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 1rem;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1.5rem;
	}

	.feature-card {
		background: transparent;
	}

	.feature-link {
		display: block;
		text-decoration: none;
		color: inherit;
		background: transparent;
	}

	.feature-link:focus-visible {
		outline: 3px solid #1e2f1e;
		outline-offset: 4px;
	}

	.feature-card img {
		width: 100%;
		aspect-ratio: 4 / 3;
		object-fit: cover;
		display: block;
		background: #f4f4f4;
	}

	.feature-title {
		margin: 0;
		padding: 0.7rem 0 0;
		font-family: 'GT Super Regular', serif;
		font-size: clamp(1.2rem, 2.2vw, 2.2rem);
		line-height: 1.05;
		color: #111;
	}

	.feature-card-fallback {
		background: linear-gradient(145deg, #98aa6d, #314d2f);
	}

	@media (max-width: 900px) {
		.homepage-content {
			padding-top: 4.5rem;
		}

		.feature-grid {
			grid-template-columns: 1fr;
			max-width: 700px;
		}
	}
</style>

