<script lang="ts">
	import '../../styles/all.css';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	type NavLink = {
		href: string;
		label: string;
	};

	const infoForLinks: NavLink[] = [
		{ href: '/education', label: 'Teachers' },
		{ href: '/research', label: 'Researchers' },
		{ href: '/visit', label: 'Visitors' }
	];

	const links: NavLink[] = [
		{ href: '/', label: 'Home' },
		{ href: '/about', label: 'About' },
		{ href: '/research', label: 'Research' },
		{ href: '/education', label: 'Education' },
		{ href: '/visit', label: 'Visit' }
	];

	let isMenuOpen = false;
	let isMobile = false;
	let isInfoMenuOpen = false;
	let infoMenuWrap: HTMLDivElement | null = null;

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

	onMount(() => {
		const handleOutsideClick = (event: MouseEvent) => {
			const target = event.target as Node;
			if (infoMenuWrap && !infoMenuWrap.contains(target)) {
				closeInfoMenu();
			}
		};

		checkMobile();
		if (typeof window !== 'undefined') {
			window.addEventListener('resize', checkMobile);
			window.addEventListener('click', handleOutsideClick);
			return () => {
				window.removeEventListener('resize', checkMobile);
				window.removeEventListener('click', handleOutsideClick);
			};
		}
	});
</script>

<nav>
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

	<div class="main-nav-row">
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

<style>
	nav {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
		font-family: 'GT Super Regular', serif;
		box-shadow: 0 3px 10px rgba(0, 0, 0, 0.16);
	}

	.utility-bar {
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
		min-width: 9.5rem;
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
		border-bottom: 1px solid rgba(0, 0, 0, 0.1);
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
	}

	.hamburger-line {
		width: 100%;
		height: 2px;
		background-color: #111;
		border-radius: 2px;
		transition: all 0.25s ease;
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
</style>