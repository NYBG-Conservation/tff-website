<script lang="ts">
	const footerLinks = [
		{ href: '/about', label: 'About' },
		{ href: '/research', label: 'Research' },
		{ href: '/data', label: 'Data and Archives' }
	] as const;

	const contactEmail = 'forest@nybg.org';
	const year = new Date().getFullYear();
</script>

<footer class="site-footer">
	<div class="footer-bar">
		<a href="/" class="footer-brand">
			<span class="brand-mark">NYBG</span>
			<span class="brand-tagline">Thain Family Forest</span>
		</a>

		<nav class="footer-nav" aria-label="Site">
			{#each footerLinks as link}
				<a href={link.href} class="footer-link">{link.label}</a>
			{/each}
		</nav>

		<a href="mailto:{contactEmail}" class="footer-contact">{contactEmail}</a>
	</div>

	<p class="footer-copy">&copy; {year} The New York Botanical Garden</p>
</footer>

<style>
	.site-footer {
		margin-top: auto;
		background: var(--olive);
		color: #111;
		border-top: 1px solid rgba(0, 0, 0, 0.1);
		box-shadow: 0 -3px 10px rgba(0, 0, 0, 0.08);
	}

	.footer-bar {
		max-width: 1100px;
		margin: 0 auto;
		padding: 0.85rem 1.25rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1.25rem 1.5rem;
		flex-wrap: wrap;
	}

	.footer-brand {
		display: inline-flex;
		align-items: baseline;
		gap: 0.45rem;
		text-decoration: none;
		color: #000;
		flex-shrink: 0;
	}

	.brand-mark {
		font-family: 'NY Botanical Gothic', serif;
		font-size: 1.35rem;
		line-height: 1;
		letter-spacing: 0.02em;
	}

	.brand-tagline {
		font-family: 'GT Super Regular', serif;
		font-size: 0.78rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: #1a1a1a;
	}

	.footer-nav {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.35rem 1.1rem;
		flex: 1 1 auto;
	}

	.footer-link,
	.footer-contact {
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		color: #111;
		text-decoration: none;
		white-space: nowrap;
		transition: color 0.18s ease;
	}

	.footer-link:hover,
	.footer-link:focus-visible,
	.footer-contact:hover,
	.footer-contact:focus-visible {
		color: var(--sugar-pine);
	}

	.footer-contact {
		font-family: 'GT Super Bold', serif;
		flex-shrink: 0;
	}

	.footer-copy {
		max-width: 1100px;
		margin: 0 auto;
		padding: 0 1.25rem 0.65rem;
		font-family: 'GT Super Regular', serif;
		font-size: 0.75rem;
		color: rgba(0, 0, 0, 0.55);
		border-top: 1px solid rgba(0, 0, 0, 0.1);
		padding-top: 0.45rem;
	}

	@media (max-width: 768px) {
		.footer-bar {
			flex-direction: column;
			align-items: flex-start;
			padding: 0.9rem 1rem;
		}

		.footer-nav {
			justify-content: flex-start;
			gap: 0.5rem 1rem;
		}

		.footer-link,
		.footer-contact {
			white-space: normal;
		}
	}
</style>
