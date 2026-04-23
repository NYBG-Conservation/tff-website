
<footer>
	<div class="footer-content">
		<div class="footer-logo">
			<a href="/">
				<span class="logo">NYBG</span>
				<span class="tagline">Urban Conservation</span>
			</a>
		</div>

		<div class="footer-links">
			<div class="link-column">
				<h3>About</h3>
				<ul>
					<li><a href="/about#team">Our Team</a></li>
					<li><a href="/about#our-mission">Our Mission</a></li>
					<li><a href="/about#our-vision">Our Vision</a></li>
					<li><a href="/press">Press</a></li>
				</ul>
			</div>

			<div class="link-column">
				<h3>Resources</h3>
				<ul>
					<li><a href="/research">Research Tools</a></li>
					<!-- <li><a href="/research">Data Downloads</a></li> -->
					<li><a href="/education">Education</a></li>
					<!-- <li><a href="/education">Workshops</a></li> -->
				</ul>
			</div>

			<div class="link-column">
				<h3>Connect</h3>
				<ul>
					<li><a href="/contact">Contact Us</a></li>
					<!-- <li><a href="/contact">Image Licensing</a></li> -->
					<!-- <li><a href="#">Events</a></li> -->
					<!-- <li><a href="#">Partnerships</a></li> -->
				</ul>
			</div> 

			<div class="newsletter-column">
				<h3>Stay Updated</h3>
				<p>Subscribe to our newsletter for updates on research, events, and conservation initiatives.</p>
				<a
					href="https://e.nybg.org/p/7T8J-VT/sign-up-for-urban-conservation-updates"
					target="_blank"
					rel="noopener noreferrer"
					class="newsletter-button"
				>
					Subscribe
				</a>
			</div>
		</div>
	</div>

	<div class="footer-bottom">
		<p>&copy; {new Date().getFullYear()} NYBG Urban Conservation. All rights reserved.</p>
	</div>
</footer>

<style>
	footer {
		background-color: black;
		color: var(--helleborous);
		padding: 3rem 2rem 1.5rem;
		/* margin-top: 4rem; */
		border-top: 2px solid var(--helleborous);
	}

	.footer-content {
		max-width: 1200px;
		margin: 0 auto;
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: 3rem;
		margin-bottom: 2rem;
	}

	.footer-logo {
		display: flex;
		flex-direction: column;
	}

	.footer-logo a {
		text-decoration: none;
		color: var(--helleborous);
		display: inline-block;
	}

	.footer-logo .logo {
		font-family: 'NY Botanical Gothic';
		font-size: 2.5rem;
		color: transparent;
		-webkit-text-stroke: 1px var(--helleborous);
		display: block;
		margin-bottom: 0.5rem;
	}

	.footer-logo .tagline {
		font-family: 'GT Super Regular';
		font-size: 1.1rem;
		color: var(--helleborous);
	}

	.footer-links {
		display: grid;
		grid-template-columns: repeat(3, 1fr) 1.5fr;
		gap: 2rem;
	}

	.link-column h3,
	.newsletter-column h3 {
		font-family: 'NY Botanical Gothic', serif;
		font-size: 1.2rem;
		color: var(--helleborous);
		margin: 0 0 1rem 0;
	}

	.link-column ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.link-column li {
		margin-bottom: 0.75rem;
	}

	.link-column a {
		color: var(--light);
		text-decoration: none;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		transition: color 0.2s;
		position: relative;
	}


	.link-column a::after {
		content: '';
		position: absolute;
		bottom: -2px;
		left: 0;
		width: 0;
		height: 1px;
		background-color: var(--light);
		transition: width 0.3s ease;
	}

	.link-column a:hover::after {
		width: 100%;
	}

	.newsletter-column p {
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		line-height: 1.5;
		margin: 0 0 1rem 0;
		color: var(--light);
	}

	.newsletter-button {
		display: inline-block;
		padding: 0.75rem 1.5rem;
		background-color: var(--helleborous);
		border: 2px solid var(--helleborous);
		color: var(--dark);
		text-decoration: none;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		white-space: nowrap;
	}

	.newsletter-button:hover {
		background-color: transparent;
		color: var(--helleborous);
	}

	.footer-bottom {
		max-width: 1200px;
		margin: 0 auto;
		padding-top: 2rem;
		border-top: 1px solid rgba(228, 255, 178, 0.2);
		text-align: center;
	}

	.footer-bottom p {
		font-family: 'GT Super Regular', serif;
		font-size: 0.85rem;
		color: var(--light);
		margin: 0;
		opacity: 0.8;
	}

	@media (max-width: 968px) {
		.footer-content {
			grid-template-columns: 1fr;
			gap: 2rem;
		}

		.footer-links {
			grid-template-columns: repeat(2, 1fr);
			gap: 2rem;
		}

		.newsletter-column {
			grid-column: 1 / -1;
		}
	}

	@media (max-width: 768px) {
		footer {
			padding: 2rem 1.5rem 1rem;
		}

		.footer-links {
			grid-template-columns: 1fr;
			gap: 2rem;
		}

		.newsletter-button {
			width: 100%;
			text-align: center;
		}
	}
</style>

