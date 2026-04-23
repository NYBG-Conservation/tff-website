<script lang="ts">
	import Profiles from '$lib/components/Profile.svelte';

	// Load all partner logos from assets (png, jpg, jpeg, svg, gif, webp)
	const logoModules = import.meta.glob<string>(
		'$lib/assets/partner-logos/*.{png,jpg,jpeg,svg,gif,webp}',
		{ eager: true, query: '?url', import: 'default' }
	);

	const partnerLogos = $derived(
		Object.entries(logoModules).map(([path, mod]) => {
			const name = path.split('/').pop()?.replace(/\.[^.]+$/, '') ?? 'Partner';
			const url = typeof mod === 'string' ? mod : (mod as { default: string })?.default;
			return { name, url };
		}).filter((p): p is { name: string; url: string } => Boolean(p.url))
	);

	// Partner website URLs (logo name -> link). Add or update as needed.
	const partnerLinks: Record<string, string> = {
		BxRAlliance: 'https://bronxriver.org/',
		CALL: 'https://www.cityaslivinglab.org/',
		DEP: 'https://www.nyc.gov/dep',
		StemTeachersNYC: 'https://stemteachersnyc.org'
	};

	interface Section {
		title: string;
		content: string[];
	}

	interface AboutContent {
		intro: string[];
		sections: Section[];
	}

	const aboutContent: AboutContent = {
		intro: [
			'We leverage scientific and public platforms to propose solutions to pressing environmental challenges, creating digital resources for communities, educators, and researchers along the way. Our work is guided by the <a href="https://www.nybg.org/plant-research-and-conservation/science-strategy/">NYBG Science Strategy</a>.',
			'By partnering with local communities, government agencies, and other organizations, we develop and convey the understanding necessary to adapt cities to a changing climate. Through education and exhibitions, we express the complex and affirming ways that fostering nature improves cities and the planet, while collaborating to build and sustain communities that create and affirm ecologies in cities and elsewhere.',
		
		],
		sections: [
			{
				title: 'Our Vision',
				content: [
					'A future where cities are shaped by nature, fostering resilience and adaptation to climate change and urbanization. Historical ecology becomes a core lens for planning and policy, embraced by communities and integrated into everyday thinking. People and nature thrive together in mutual interdependence, creating livable cities that center nature and connect people to their urban environment.'
				]
			},
			{
				title: 'Our Mission',
				content: [
					'Our mission is to reconnect urban communities with nature by integrating historical ecology into planning, policy, and public awareness. We work to create resilient, livable cities where people and nature thrive together, fostering adaptation to climate change and urbanization through education, tools, and collaborative action.'
				]
			}
		]
	};

</script>

<div class="our-approach">
	<h2>Our Approach</h2>
	{#each aboutContent.intro as paragraph}
		<p>{@html paragraph}</p>
	{/each}
</div>

{#each aboutContent.sections as section}
	<h2>{section.title}</h2>
	{#each section.content as paragraph}
		<p>{paragraph}</p>
	{/each}
{/each}

<h2>The team</h2>
<Profiles />


<h2>Our Partners</h2>
<div class="partners-grid">
	{#each partnerLogos as { name, url }}
		<div class="partner-logo">
			{#if partnerLinks[name]}
				<a href={partnerLinks[name]} target="_blank" rel="noopener noreferrer" title={name}>
					<img src={url} alt={name} />
				</a>
			{:else}
				<img src={url} alt={name} />
			{/if}
		</div>
	{/each}
</div>

<style>
	p {
		color: #000;
		font-family: 'GT Super Text';
		font-size: 1.15rem;
		font-style: normal;
		font-weight: 400;
		line-height: normal;
		width: 42rem;
		max-width: 90%;
		margin: 1em auto;
	}

	h2 {
		color: #000;
		font-family: 'NY Botanical Gothic';
		font-size: 2.1rem;
		font-style: normal;
		font-weight: 800;
		line-height: normal;
		text-align: center;
		margin: 2em auto 1em auto;
	}

	.partners-grid {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-items: center;
		gap: 2rem;
		width: 90%;
		max-width: 900px;
		margin: 2rem auto;
	}

	.partner-logo {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 80px;
		max-width: 160px;
	}

	.partner-logo a {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		width: 100%;
	}

	.partner-logo img {
		max-height: 100%;
		max-width: 100%;
		width: auto;
		height: auto;
		object-fit: contain;
		/* filter: grayscale(100%); */
		opacity: 0.85;
	}

	/* Our Approach section links: pine color + underline animation */
	.our-approach p :global(a) {
		color: var(--sugar-pine);
		text-decoration: underline;
		position: relative;
	}

	.our-approach p :global(a)::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		width: 0;
		height: 2px;
		background-color: var(--sugar-pine);
		transition: width 0.3s ease;
	}

	.our-approach p :global(a:hover)::after {
		width: 100%;
	}

</style>
