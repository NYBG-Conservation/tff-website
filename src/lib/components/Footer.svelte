
<footer>
	<div class="footer-content">
		<div class="footer-logo">
			<a href="/">
				<span class="logo">NYBG</span>
				<span class="tagline">THAIN FAMILY FOREST</span>
			</a>
		</div>
		<a
			href="https://e.nybg.org/p/7T8J-VT/sign-up-for-urban-conservation-updates"
			target="_blank"
			rel="noopener noreferrer"
			class="subscribe-link"
		>
			Subscribe
		</a>
	</div>
	<div class="footer-bottom">
		<p>&copy; {new Date().getFullYear()} NYBG Urban Conservation.</p>
	</div>

</footer>

<style>
	footer {
		background-color: #fff;
		color: #111;
		border-top: 4px solid var(--olive);
	}

	.footer-content {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.65rem 1rem;
	}

	.footer-logo {
		display: flex;
		align-items: center;
	}

	.footer-logo a {
		text-decoration: none;
		color: #111;
		display: inline-flex;
		align-items: baseline;
		gap: 0.5rem;
	}

	.footer-logo .logo {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.5rem, 2.8vw, 2rem);
		line-height: 1;
		color: #111;
	}

	.footer-logo .tagline {
		font-family: 'GT Super Regular', serif;
		font-size: clamp(0.66rem, 1.2vw, 0.88rem);
		letter-spacing: 0.04em;
		color: rgba(17, 17, 17, 0.85);
	}

	.subscribe-link {
		text-decoration: none;
		color: #111;
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		position: relative;
		padding-bottom: 0.1rem;
	}

	.subscribe-link::after {
		content: '';
		position: absolute;
		left: 0;
		bottom: 0;
		width: 100%;
		height: 1px;
		background-color: #111;
		opacity: 0.4;
	}

	.subscribe-link:hover::after {
		opacity: 1;
	}

	.footer-bottom {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 1rem 0.55rem;
		text-align: left;
		border-top: 1px solid rgba(0, 0, 0, 0.08);
	}

	.footer-bottom p {
		font-family: 'GT Super Regular', serif;
		font-size: 0.8rem;
		color: #111;
		margin: 0;
		opacity: 0.7;
	}

	@media (max-width: 968px) {
		.footer-content {
			padding: 0.65rem 1rem;
		}
	}

	@media (max-width: 768px) {
		.footer-content {
			flex-wrap: wrap;
			row-gap: 0.4rem;
		}

		.footer-logo a {
			gap: 0.35rem;
		}
	}
</style>

