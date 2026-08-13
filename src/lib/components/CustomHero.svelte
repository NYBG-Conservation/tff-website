<script lang="ts">
	let { heroImage = '' }: { heroImage?: string } = $props();
	const fallbackHero = '/heroes/tff-forest-group.png';
</script>

<section
	class="hero"
	style="background-image: linear-gradient(rgba(0,0,0,0.42), rgba(0,0,0,0.42)), url('{heroImage || fallbackHero}')"
>
	<div class="hero-content">
		<p class="hero-kicker">ABOUT</p>
		<h1 class="hero-title">WELCOME TO THE<br />THAIN FAMILY FOREST</h1>
		<p class="hero-desc">NYBG's 50-acre old-growth forest for research and recreation</p>
		<div class="hero-ctas">
			<a href="/about" class="hero-button">Learn more</a>
		</div>
	</div>
</section>

<style>
	.hero {
		min-height: clamp(460px, 58vh, 640px);
		background-position: center 35%;
		background-size: cover;
		display: grid;
		place-items: center;
		padding: 2rem 1rem;
	}

	.hero-content {
		max-width: 840px;
		text-align: center;
		color: #fff;
	}

	.hero-kicker {
		font-family: 'GT Super Regular', serif;
		font-size: 1.15rem;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		margin: 0 0 0.8rem 0;
	}

	.hero-title {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(2rem, 4vw, 4rem);
		line-height: 1.05;
		letter-spacing: 0.01em;
		margin: 0;
		text-transform: uppercase;
		color: white;
	}

	.hero-desc {
		font-family: 'GT Super Regular', serif;
		font-size: clamp(1rem, 2vw, 2rem);
		line-height: 1.4;
		max-width: 44rem;
		margin: 1.25rem auto 0;
		color: rgba(255, 255, 255, 0.94);
	}

	.hero-ctas {
		margin-top: 1.5rem;
	}

	.hero-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.5rem 1rem;
		color: white;
		font-family: 'GT Super Regular', serif;
		text-decoration: none;
		border: 1px solid #fff;
		transition: background-color 0.2s ease, color 0.2s ease;
	}

	.hero-button:hover {
		background-color: #fff;
		color: #111;
	}

	@media (max-width: 900px) {
		.hero {
			min-height: 430px;
		}
	}

	@media (max-width: 600px) {
		.hero {
			min-height: 390px;
		}
	}
</style>
