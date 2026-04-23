<script lang="ts">
	import '../../../styles/all.css';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	type NavLink = {
		href: string;
		label: string;
		/** If true, open in a new tab (e.g. leave the map context). */
		openInNewTab?: boolean;
	};

	const links: NavLink[] = [
		{ href: '/blue-zones', label: 'Map Explorer' },
		{ href: '/blue-zones/about', label: 'About this Project' },
		// { href: '/blue-zones/map-explorer', label: 'Map Explorer' },
		{ href: '/contact', label: 'Contact', openInNewTab: true }
	];

	const pageColors: Record<string, string> = {
		'blue-zones/about': '#FEC3F9',
	};

	$: activeAccentColor = '#FEC3F9';

	let isMenuOpen = false;
	let isMobile = false;

	function isActive(href: string): boolean {
		const currentPath = $page.url.pathname;
		if (href === '/blue-zones') return currentPath === '/blue-zones';
		return currentPath.startsWith(href);
	}


	function toggleMenu() {
		isMenuOpen = !isMenuOpen;
	}

	function closeMenu() {
		isMenuOpen = false;
	}

	function checkMobile() {
		if (typeof window !== 'undefined') {
			isMobile = window.innerWidth < 768;
			if (!isMobile) isMenuOpen = false;
		}
	}

	onMount(() => {
		checkMobile();
		if (typeof window !== 'undefined') {
			window.addEventListener('resize', checkMobile);
			return () => {
				window.removeEventListener('resize', checkMobile);
			};
		}
	});
</script>

<nav style="--active-accent: #FEC3F9">
	<a href="/blue-zones" class="logo-link" on:click={closeMenu}>
		<div class="logo-lockup">
			<div class="logo-wordmark">
				<span class="logo-word">BLUE</span>
				<span class="logo-word zones">
					Z
					<img src="/imgs/blue-zones-o.svg" alt="" class="logo-o" aria-hidden="true" />
					NES
				</span>
			</div>
			<span class="logo-subline">BY NYBG</span>
		</div>
	</a>

	<button class="menu-toggle" class:open={isMenuOpen} on:click={toggleMenu} aria-label="Toggle menu" aria-expanded={isMenuOpen}>
		<span class="hamburger-line"></span>
		<span class="hamburger-line"></span>
		<span class="hamburger-line"></span>
	</button>

	<div class="links" class:open={isMenuOpen}>
		{#each links as link}
			<a
				href={link.href}
				class:active={isActive(link.href)}
				on:click={closeMenu}
				target={link.openInNewTab ? '_blank' : undefined}
				rel={link.openInNewTab ? 'noopener noreferrer' : undefined}
			>
				{link.label}
			</a>
		{/each}
	</div>
</nav>

<style>
	nav {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
		background-color: #f5f2eb;
		margin: 0;
		padding: 0 20px;
		padding-top: env(safe-area-inset-top, 0px);
		box-sizing: border-box;
		min-height: calc(var(--nav-height, 72px) + env(safe-area-inset-top, 0px));
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		align-items: center;
		font-family: 'GT Super Regular', serif;
		color: #079ed3;
		border-bottom: 3px solid #079ed3;
		box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
	}

	.links a {
		color: #079ed3;
		text-decoration: none;
		position: relative;
		padding-bottom: 4px;
		transition: color 0.3s ease, text-decoration 0.3s ease;
	}

	.links a:hover,
	.links a.active {
		text-decoration: underline;
		text-decoration-style: wavy;
		text-decoration-color: #079ed3;
		text-underline-offset: 0.22em;
	}

	.logo-link {
		padding-bottom: 0;
		cursor: pointer;
		position: relative;
		text-decoration: none;
	}

	.logo-lockup {
		display: flex;
		flex-direction: row;
		line-height: 0.95;
	}

	.logo-wordmark {
		display: flex;
		gap: 0.4rem;
		align-items: center;
	}

	.logo-word {
		font-family: 'NY Botanical Gothic', serif;
		font-size: 2.6rem;
		color: #079ed3;
		letter-spacing: 0.04em;
		display: inline-flex;
		align-items: center;
	}

	.logo-word.zones {
		gap: 0.16rem;
	}

	.logo-o {
		width: 0.76em;
		height: 0.92em;
		display: inline-block;
		transform: translateY(-0.02em);
	}

	.logo-subline {
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		/* letter-spacing: 0.1em; */
		color: #079ed3;
		margin-top: 0.08rem;
		display: inline-flex;
		align-items: flex-end;
	}

	.links {
		min-width: 40%;
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		align-items: center;
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
		z-index: 1001;
	}

	.hamburger-line {
		width: 100%;
		height: 3px;
		background-color: #079ed3;
		border-radius: 3px;
		transition: all 0.3s ease;
	}

	.menu-toggle:hover .hamburger-line {
		opacity: 0.8;
	}

	@media (max-width: 900px) {
		.logo-word {
			font-size: 2.2rem;
		}
	}

	@media (max-width: 768px) {
		nav {
			padding: env(safe-area-inset-top, 0px) 15px 0;
			flex-wrap: wrap;
		}

		.logo-word {
			font-size: 1.8rem;
		}

		.logo-subline {
			font-size: 0.62rem;
			letter-spacing: 0.18em;
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
			background-color: #f5f2eb;
			flex-direction: column;
			align-items: stretch;
			min-width: 100%;
			padding: 1rem 0;
			box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3);
		}

		.links.open {
			display: flex;
		}

		.links a {
			padding: 1rem 20px;
			width: 100%;
			text-align: left;
			border-bottom: 1px solid rgba(7, 158, 211, 0.25);
		}

		.links a:last-child {
			border-bottom: none;
		}

		.links a.active {
			background-color: rgba(7, 158, 211, 0.08);
		}

		.menu-toggle.open .hamburger-line:nth-child(1) {
			transform: rotate(45deg) translate(8px, 8px);
		}

		.menu-toggle.open .hamburger-line:nth-child(2) {
			opacity: 0;
		}

		.menu-toggle.open .hamburger-line:nth-child(3) {
			transform: rotate(-45deg) translate(7px, -7px);
		}
	}
</style>
