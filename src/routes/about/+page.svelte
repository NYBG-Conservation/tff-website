<script lang="ts">
	// Load all partner logos from assets (png, jpg, jpeg, svg, gif, webp)
	const logoModules = import.meta.glob<string>(
		'$lib/assets/partner-logos/*.{png,jpg,jpeg,svg,gif,webp}',
		{ eager: true, query: '?url', import: 'default' }
	);


</script>

<!-- <h2>About the Forest</h2> -->
<p>
	For thousands of years, this old-growth Forest has changed, adapted and survived. When you visit the
	Forest, you will walk along Native American hunting trails, see marks left by glaciers, and pass under
	trees dating back to the American Revolution. The unique beauty and ecological importance of the forest
	are one of the reasons why the founders selected this site for The New York Botanical Garden in 1895.
</p>
<p>
	Today this is the largest uncut expanse of New York's original wooded landscape. The Forest remains a
	magnificent reminder of the beauty and resilience of nature in the face of complex human-caused
	disturbances. To preserve the Forest for future generations the Garden manages invasive species, plants
	native plants, and performs research.
</p>
<p class="our-approach">
	Download the
	<a
		href="https://www.nybg.org/content/uploads/2017/04/Forest-Plan-2016.pdf"
		target="_blank"
		rel="noopener noreferrer"
	>Thain Family Forest Program 2008-2025</a>
	to learn more about ongoing forest restoration, education, and research.
</p>


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
