<script lang="ts">
	import '../styles/all.css';
	import Nav from '$lib/components/Nav.svelte';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { page } from '$app/stores';
	import { dev } from '$app/environment';
	import { injectAnalytics } from '@vercel/analytics/sveltekit';

	let { children, data } = $props();

	const isHomepage = $derived($page.url.pathname === '/');

	const origin = $derived($page.url.origin);
	const path = $derived($page.url.pathname);
	const canonicalUrl = $derived(`${origin}${path}`);

	const ogTitle = $derived(data?.ogTitle ?? 'Thain Family Forest | NYBG');
	const ogDescription = $derived(
		data?.ogDescription ??
			"NYBG's 50-acre old-growth forest for research and recreation"
	);
	const ogImage = $derived(`${origin}/imgs/opengraph.png`);
	const pageTitle = $derived(data?.title ?? 'Thain Family Forest | NYBG');

	injectAnalytics({ mode: dev ? 'development' : 'production' });
</script>

<svelte:head>
	<title>{pageTitle}</title>
	<link rel="icon" href="https://www.nybg.org/content/uploads/2024/01/cropped-favicon-32x32.png" type="image/png" />
	<meta property="og:type" content="website" />
	<meta property="og:url" content={canonicalUrl} />
	<meta property="og:title" content={ogTitle} />
	<meta property="og:description" content={ogDescription} />
	<meta property="og:image" content={ogImage} />
	<meta property="og:site_name" content="Thain Family Forest | NYBG" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={ogTitle} />
	<meta name="twitter:description" content={ogDescription} />
	<meta name="twitter:image" content={ogImage} />
</svelte:head>

<div class="app-container" class:homepage={isHomepage}>
	<div class="nav-header-band">
		<Nav />
		{#if !isHomepage}
			<Header />
		{/if}
	</div>

	<main class="page-main">
		{@render children()}
	</main>

	<Footer />
</div>

<style>
	.app-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		transition: background-color 0.3s ease;
	}

	.app-container.homepage {
		background-color: var(--bg-light);
	}

	.app-container:not(.homepage) {
		background-color: var(--bg-light);
	}

	.nav-header-band {
		position: relative;
		z-index: 1000;
		background-color: transparent;
		padding-top: var(--site-nav-height, 112px);
		transition: padding-top 0.28s ease;
	}

	.page-main {
		flex: 1 0 auto;
	}
</style>
