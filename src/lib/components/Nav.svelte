<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { djangoAdminHomeUrl } from '$lib/api/djangoAdmin';

	type NavLink = {
		href: string;
		label: string;
	};

	const infoForLinks: NavLink[] = [
		{ href: '/research', label: 'Researchers' },
		{ href: djangoAdminHomeUrl(), label: 'Research portal' }
	];

	const links: NavLink[] = [
		{ href: '/', label: 'Home' },
		{ href: '/about', label: 'About' },
		{ href: '/research', label: 'Research' },
		{ href: '/data', label: 'Data and Archives' }
	];

	let isMenuOpen = false;
	let isMobile = false;
	let isInfoMenuOpen = false;
	let infoMenuWrap: HTMLDivElement | null = null;
	let subnavHidden = false;
	let lastScrollY = 0;

	const SCROLL_DELTA = 6;
	const TOP_REVEAL_OFFSET = 12;
	const UTILITY_NAV_HEIGHT_DESKTOP = 64;
	const UTILITY_NAV_HEIGHT_MOBILE = 56;
	const SUBNAV_HEIGHT = 48;

	$: utilityNavHeight = isMobile ? UTILITY_NAV_HEIGHT_MOBILE : UTILITY_NAV_HEIGHT_DESKTOP;
	$: siteNavHeight = utilityNavHeight + (subnavHidden && !isMenuOpen ? 0 : SUBNAV_HEIGHT);

	$: if (typeof document !== 'undefined') {
		document.documentElement.style.setProperty('--site-nav-height', `${siteNavHeight}px`);
	}

	function isActive(href: string): boolean {
		const currentPath = $page.url.pathname;
		if (href === '/') {
			return currentPath === '/';
		}
		return currentPath.startsWith(href);
	}

	function toggleMenu() {
		isMenuOpen = !isMenuOpen;
	}

	function closeMenu() {
		isMenuOpen = false;
	}

	function toggleInfoMenu(event: MouseEvent) {
		event.stopPropagation();
		isInfoMenuOpen = !isInfoMenuOpen;
	}

	function closeInfoMenu() {
		isInfoMenuOpen = false;
	}

	function checkMobile() {
		if (typeof window !== 'undefined') {
			isMobile = window.innerWidth < 768;
			if (!isMobile) {
				isMenuOpen = false;
			}
		}
	}

	function updateSubnavOnScroll() {
		if (typeof window === 'undefined') return;

		const currentScrollY = window.scrollY;

		// Keep the hamburger row visible on phones so the menu stays reachable.
		if (window.innerWidth < 640) {
			subnavHidden = false;
			lastScrollY = currentScrollY;
			return;
		}

		if (isMenuOpen || currentScrollY <= TOP_REVEAL_OFFSET) {
			subnavHidden = false;
		} else if (currentScrollY > lastScrollY + SCROLL_DELTA) {
			subnavHidden = true;
		} else if (currentScrollY < lastScrollY - SCROLL_DELTA) {
			subnavHidden = false;
		}

		lastScrollY = currentScrollY;
	}

	onMount(() => {
		const handleOutsideClick = (event: MouseEvent) => {
			const target = event.target as Node;
			if (infoMenuWrap && !infoMenuWrap.contains(target)) {
				closeInfoMenu();
			}
		};

		checkMobile();
		lastScrollY = window.scrollY;
		document.documentElement.style.setProperty('--site-nav-height', `${siteNavHeight}px`);

		if (typeof window !== 'undefined') {
			window.addEventListener('resize', checkMobile);
			window.addEventListener('click', handleOutsideClick);
			window.addEventListener('scroll', updateSubnavOnScroll, { passive: true });
			return () => {
				window.removeEventListener('resize', checkMobile);
				window.removeEventListener('click', handleOutsideClick);
				window.removeEventListener('scroll', updateSubnavOnScroll);
				document.documentElement.style.removeProperty('--site-nav-height');
				document.body.style.overflow = '';
			};
		}
	});

	$: if ($page.url.pathname) {
		isMenuOpen = false;
		subnavHidden = false;
		lastScrollY = typeof window !== 'undefined' ? window.scrollY : 0;
	}

	$: if (typeof document !== 'undefined') {
		document.body.style.overflow = isMenuOpen ? 'hidden' : '';
	}
</script>

<nav class:menu-open={isMenuOpen} class:info-menu-open={isInfoMenuOpen}>
	<div class="utility-bar">
		<div class="utility-dropdown" bind:this={infoMenuWrap}>
			<button
				type="button"
				class="utility-link utility-dropdown-button"
				on:click={toggleInfoMenu}
				aria-expanded={isInfoMenuOpen}
				aria-haspopup="true"
			>
				INFO FOR ▾
			</button>
			{#if isInfoMenuOpen}
				<div class="utility-dropdown-menu">
					{#each infoForLinks as link}
						<a href={link.href} on:click={closeInfoMenu}>{link.label}</a>
					{/each}
				</div>
			{/if}
		</div>
		<a href="/" class="logo-link" on:click={closeMenu}>
			<span class="logo">NYBG</span>
			<span class="tagline">THAIN FAMILY FOREST</span>
		</a>
		<span class="utility-spacer" aria-hidden="true"></span>
	</div>

	<div class="main-nav-row" class:subnav-hidden={subnavHidden && !isMenuOpen}>
		<button
			class="menu-toggle"
			class:open={isMenuOpen}
			on:click={toggleMenu}
			aria-label="Toggle menu"
			aria-expanded={isMenuOpen}
		>
			<span class="hamburger-line"></span>
			<span class="hamburger-line"></span>
			<span class="hamburger-line"></span>
		</button>

		<div class="links" class:open={isMenuOpen}>
			{#each links as link}
				<a href={link.href} class:active={isActive(link.href)} on:click={closeMenu}>{link.label}</a>
			{/each}
		</div>
	</div>
</nav>

{#if isMenuOpen && isMobile}
	<button type="button" class="menu-backdrop" aria-label="Close menu" on:click={closeMenu}></button>
{/if}

<style>
	nav {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
		font-family: 'GT Super Regular', serif;
		box-shadow: 0 3px 10px rgba(0, 0, 0, 0.16);
		overflow: hidden;
	}

	nav.menu-open,
	nav.info-menu-open {
		overflow: visible;
	}

	.utility-bar {
		position: relative;
		z-index: 2;
		background-color: var(--olive);
		min-height: 64px;
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
		padding: 0 1.5rem;
	}

	.utility-link {
		color: #111;
		font-size: 0.85rem;
		letter-spacing: 0.02em;
		justify-self: start;
		font-family: inherit;
	}

	.utility-dropdown {
		position: relative;
		justify-self: start;
	}

	.utility-dropdown-button {
		background: transparent;
		border: none;
		padding: 0;
		cursor: pointer;
	}

	.utility-dropdown-menu {
		position: absolute;
		top: calc(100% + 0.35rem);
		left: 0;
		min-width: 11rem;
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.18);
		box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
		z-index: 1100;
		display: grid;
	}

	.utility-dropdown-menu a {
		text-decoration: none;
		color: #111;
		padding: 0.55rem 0.75rem;
		font-size: 0.9rem;
	}

	.utility-dropdown-menu a:hover {
		background: rgba(200, 181, 0, 0.12);
	}

	.logo-link {
		text-decoration: none;
		display: inline-flex;
		align-items: baseline;
		gap: 0.55rem;
		justify-self: center;
	}

	.logo {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.8rem, 4vw, 2.7rem);
		line-height: 1;
		color: #000;
	}

	.tagline {
		font-size: clamp(0.7rem, 1.6vw, 1.02rem);
		letter-spacing: 0.04em;
		color: #1a1a1a;
	}

	.utility-spacer {
		justify-self: end;
	}

	.main-nav-row {
		background-color: #fff;
		min-height: 48px;
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 0 1rem;
		position: relative;
		z-index: 1;
		border-bottom: 1px solid rgba(0, 0, 0, 0.1);
		max-height: 48px;
		overflow: hidden;
		transition:
			max-height 0.28s ease,
			opacity 0.24s ease,
			border-color 0.28s ease;
		opacity: 1;
	}

	nav.menu-open .main-nav-row {
		overflow: visible;
	}

	.main-nav-row.subnav-hidden {
		max-height: 0;
		min-height: 0;
		opacity: 0;
		border-bottom-color: transparent;
		pointer-events: none;
	}

	.links {
		display: flex;
		align-items: center;
		justify-content: center;
		flex-wrap: wrap;
		gap: clamp(1rem, 4vw, 3.5rem);
	}

	.links a {
		color: #111;
		text-decoration: none;
		font-size: 1rem;
		padding: 0.25rem 0;
		position: relative;
	}

	.links a::after {
		content: '';
		position: absolute;
		bottom: -1px;
		left: 0;
		width: 0;
		height: 2px;
		background-color: #111;
		transition: width 0.2s ease;
	}

	.links a:hover::after,
	.links a.active::after {
		width: 100%;
	}

	.menu-toggle {
		display: none;
		flex-direction: column;
		justify-content: space-around;
		width: 30px;
		height: 30px;
		background: transparent;
		border: none;
		cursor: pointer;
		padding: 0;
		position: absolute;
		left: 1rem;
		z-index: 2;
	}

	.hamburger-line {
		width: 100%;
		height: 2px;
		background-color: #111;
		border-radius: 2px;
		transition: all 0.25s ease;
	}

	.menu-backdrop {
		position: fixed;
		inset: 0;
		z-index: 999;
		border: none;
		padding: 0;
		margin: 0;
		background: rgba(0, 0, 0, 0.28);
		cursor: pointer;
	}

	@media (max-width: 768px) {
		.utility-bar {
			min-height: 56px;
			padding: 0 1rem;
		}

		.logo-link {
			gap: 0.35rem;
		}

		.main-nav-row {
			justify-content: flex-start;
		}

		.menu-toggle {
			display: flex;
		}

		.links {
			display: none;
			position: absolute;
			top: 100%;
			left: 0;
			right: 0;
			background-color: #fff;
			flex-direction: column;
			align-items: stretch;
			gap: 0;
			border-bottom: 1px solid rgba(0, 0, 0, 0.1);
		}

		.links.open {
			display: flex;
			z-index: 1100;
			box-shadow: 0 10px 18px rgba(0, 0, 0, 0.12);
		}

		.links a {
			padding: 0.9rem 1.1rem;
			border-bottom: 1px solid rgba(0, 0, 0, 0.08);
		}

		.links a::after {
			display: none;
		}

		.links a.active {
			background-color: rgba(200, 181, 0, 0.12);
		}

		.menu-toggle.open .hamburger-line:nth-child(1) {
			transform: rotate(45deg) translate(7px, 7px);
		}

		.menu-toggle.open .hamburger-line:nth-child(2) {
			opacity: 0;
		}

		.menu-toggle.open .hamburger-line:nth-child(3) {
			transform: rotate(-45deg) translate(6px, -6px);
		}
	}

	@media (max-width: 640px) {
		.utility-dropdown,
		.utility-spacer {
			display: none;
		}

		.utility-bar {
			grid-template-columns: 1fr;
			justify-items: center;
		}

		.logo-link {
			justify-self: center;
		}

		.menu-toggle {
			width: 44px;
			height: 44px;
			padding: 7px;
		}
	}
</style>