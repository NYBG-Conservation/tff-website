<script lang="ts">
	import '../styles/all.css';
	import Nav from '$lib/components/Nav.svelte';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { page } from '$app/stores';

	let { children, data } = $props();

	const isHomepage = $derived($page.url.pathname === '/');
	const isCustomLayout = $derived($page.url.pathname.startsWith('/blue-zones'));

	const origin = $derived($page.url.origin);
	const path = $derived($page.url.pathname);
	const canonicalUrl = $derived(`${origin}${path}`);

	const ogTitle = $derived(data?.ogTitle ?? 'Urban Conservation Hub | NYBG');
	const ogDescription = $derived(
		data?.ogDescription ??
			'Partnering with communities and government to develop tools and research that help New York City adapt to a changing climate.'
	);
	const ogImage = $derived(`${origin}/imgs/opengraph.png`);
	const pageTitle = $derived(data?.title ?? 'Urban Conservation Hub | NYBG');
	import { dev } from '$app/environment';
import { injectAnalytics } from '@vercel/analytics/sveltekit';

injectAnalytics({ mode: dev ? 'development' : 'production' });
</script>

<svelte:head>
	{#if !isCustomLayout}
		<title>{pageTitle}</title>
		<link rel="icon" href="https://www.nybg.org/content/uploads/2024/01/cropped-favicon-32x32.png" type="image/png" />
		<meta property="og:type" content="website" />
		<meta property="og:url" content={canonicalUrl} />
		<meta property="og:title" content={ogTitle} />
		<meta property="og:description" content={ogDescription} />
		<meta property="og:image" content={ogImage} />
		<meta property="og:site_name" content="Urban Conservation Hub" />
		<meta name="twitter:card" content="summary_large_image" />
		<meta name="twitter:title" content={ogTitle} />
		<meta name="twitter:description" content={ogDescription} />
		<meta name="twitter:image" content={ogImage} />
	{/if}
</svelte:head>

{#if isCustomLayout}
	{@render children()}
{:else}
	<div class="app-container" class:homepage={isHomepage}>
		<div class="nav-header-band">
			<Nav />
			{#if !isHomepage && !isCustomLayout}
				<Header />
			{/if}
		</div>

		<main class="page-main">
			{@render children()}
		</main>

		<Footer />
	</div>
{/if}

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