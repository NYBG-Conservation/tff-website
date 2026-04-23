<script lang="ts">
	import { onMount } from 'svelte';

	export let announcements: Announcement[] = [];

	interface Announcement {
		image?: string;
		title: string;
		description: string;
		link?: string;
	}
	let test_var = 0;

	let currentIndex = 0;
	let isPaused = false;
	let intervalId: ReturnType<typeof setInterval> | null = null;

	function nextSlide() {
		if (announcements.length === 0) return;
		currentIndex = (currentIndex + 1) % announcements.length;
	}

	function previousSlide() {
		if (announcements.length === 0) return;
		currentIndex = (currentIndex - 1 + announcements.length) % announcements.length;
	}

	function goToSlide(index: number) {
		currentIndex = index;
	}

	function pauseCarousel() {
		isPaused = true;
		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}
	}

	function resumeCarousel() {
		isPaused = false;
		if (announcements.length > 1) {
			intervalId = setInterval(nextSlide, 7000);
		}
	}

	onMount(() => {
		if (announcements.length > 1) {
			intervalId = setInterval(nextSlide, 7000);
		}
		return () => {
			if (intervalId) {
				clearInterval(intervalId);
			}
		};
	});
</script>

{#if announcements.length > 0}
	<div
		class="carousel-container"
		on:mouseenter={pauseCarousel}
		on:mouseleave={resumeCarousel}
		role="region"
		aria-label="Announcements carousel"
	>
		<button
			type="button"
			class="carousel-button carousel-button-prev"
			on:click={previousSlide}
			aria-label="Previous slide"
		>
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M15 18l-6-6 6-6" />
			</svg>
		</button>

		<div class="carousel-wrapper">
			<div class="carousel-track" style="transform: translateX(-{currentIndex * 100}%)">
				{#each announcements as item, index}
					<div class="carousel-slide" data-index={index}>
						<div class="announcement-card">
							{#if item.image}
								<div class="card-image">
						<img src={item.image} alt={item.title} />
								</div>
							{/if}
							<div class="card-content-wrapper">
								<h3 class="card-title">{item.title}</h3>
								<p class="card-description">{item.description}</p>
								{#if item.link}
									<a href={item.link} class="card-link">Learn more →</a>
								{/if}
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<button
			type="button"
			class="carousel-button carousel-button-next"
			on:click={nextSlide}
			aria-label="Next slide"
		>
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M9 18l6-6-6-6" />
			</svg>
		</button>

		{#if announcements.length > 1}
			<div class="carousel-indicators">
				{#each announcements as _, index}
					<button
						type="button"
						class="indicator"
						class:active={index === currentIndex}
						on:click={() => goToSlide(index)}
						aria-label="Go to slide {index + 1}"
					>
						<span class="sr-only">Slide {index + 1}</span>
					</button>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<style>
	.carousel-container {
		position: relative;
		width: 85%;
		max-width: 950px;
		margin: 2rem auto;
		padding: 0 2rem;
	}

	.carousel-wrapper {
		overflow: hidden;
	}

	.carousel-track {
		display: flex;
		transition: transform 0.5s ease-in-out;
		will-change: transform;
	}

	.carousel-slide {
		width: 100%;
		flex-shrink: 0;
		padding: 1rem;
	}

	.announcement-card {
		background-color: white;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		min-height: 450px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
	}

	.card-image {
		width: 100%;
		height: 350px;
		max-height: 400px;
		overflow: hidden;
		background-color: white;
	}

	.card-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.card-content-wrapper {
		padding: 2rem;
		display: flex;
		flex-direction: column;
		flex: 1;
		color: var(--dark);
	}

	.card-title {
		font-family: 'NY Botanical Gothic', serif;
		font-size: 1.8rem;
		margin: 0 0 1rem 0;
		color: var(--dark);
	}

	.card-description {
		flex: 1;
		font-family: 'GT Super Regular', serif;
		line-height: 1.6;
		margin: 0 0 1rem 0;
		color: var(--dark);
		flex-wrap: wrap;
		width: 100%;
		display: flex;
	}

	.card-link {
		display: inline-block;
		margin-top: auto;
		color: var(--dark);
		text-decoration: none;
		font-family: 'GT Super Regular', serif;
		font-weight: 600;
		position: relative;
		padding-bottom: 4px;
		transition: color 0.3s ease;
		width: fit-content;
		align-self: flex-start;
	}

	.card-link::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		width: 0;
		height: 2px;
		background-color: var(--dark);
		transition: width 0.3s ease;
	}

	.card-link:hover::after {
		width: 100%;
	}

	.carousel-button {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		/* background-color: var(--dark); */
		border: 2px solid var(--dark);
		border-radius: 50%;
		color: var(--dark);
		width: 50px;
		height: 50px;
		/* border-radius: 50%; */
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.2s;
		z-index: 10;
		padding: 0;
	}

	.carousel-button:hover {
		background-color: var(--helleborous);
		/* color: var(--dark); */
	}

	.carousel-button-prev {
		left: -25px;
	}

	.carousel-button-next {
		right: -25px;
	}

	.carousel-indicators {
		display: flex;
		justify-content: center;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}

	.indicator {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		border: 2px solid var(--dark);
		background-color: transparent;
		cursor: pointer;
		transition: all 0.2s;
		padding: 0;
	}

	.indicator:hover {
		background-color: var(--dark);
		opacity: 0.7;
	}

	.indicator.active {
		background-color: var(--dark);
	}

	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
	}

	@media (max-width: 768px) {
		.carousel-container {
			padding: 0 1rem;
		}

		.carousel-button {
			width: 40px;
			height: 40px;
		}

		.carousel-button-prev {
			left: -20px;
		}

		.carousel-button-next {
			right: -20px;
		}

		.announcement-card {
			min-height: 350px;
		}

		.card-image {
			height: 200px;
		}

		.card-content-wrapper {
			padding: 1.5rem;
		}

		.card-title {
			font-size: 1.4rem;
		}
	}
</style>
