<script lang="ts">
	import { onMount } from 'svelte';
	import EventCard from '$lib/components/EventCard.svelte';

	type EventItem = {
		title: string;
		dates: string[];
		startTime?: string;
		endTime?: string;
		location?: string;
		description?: string;
		link?: string;
	};

	export let events: EventItem[] = [];

	function parseEventDateMs(dateStr: string): number | null {
		const parts = dateStr.trim().split(/[\/\-]/).map((p) => parseInt(p, 10));
		if (parts.length < 3 || parts.some((n) => isNaN(n))) return null;
		const [month, day, year] = parts;
		const date = new Date(year, month - 1, day);
		return isNaN(date.getTime()) ? null : date.getTime();
	}

	function earliestDateMs(event: EventItem): number {
		let min = Infinity;
		for (const d of event.dates) {
			const t = parseEventDateMs(d);
			if (t !== null && t < min) min = t;
		}
		return min === Infinity ? Number.MAX_SAFE_INTEGER : min;
	}

	$: sortedEvents = [...events].sort((a, b) => earliestDateMs(a) - earliestDateMs(b));

	let scrollContainer: HTMLDivElement;
	let canScrollLeft = false;
	let canScrollRight = false;

	function checkScrollability() {
		if (!scrollContainer) return;
		canScrollLeft = scrollContainer.scrollLeft > 0;
		canScrollRight =
			scrollContainer.scrollLeft < scrollContainer.scrollWidth - scrollContainer.clientWidth - 1;
		
		// Check if content fits - if so, center it; otherwise align left for proper scrolling
		const shouldCenter = scrollContainer.scrollWidth <= scrollContainer.clientWidth;
		scrollContainer.style.justifyContent = shouldCenter ? 'center' : 'flex-start';
	}

	function scrollLeft() {
		if (!scrollContainer) return;
		scrollContainer.scrollBy({ left: -400, behavior: 'smooth' });
	}

	function scrollRight() {
		if (!scrollContainer) return;
		scrollContainer.scrollBy({ left: 400, behavior: 'smooth' });
	}

	onMount(() => {
		if (scrollContainer) {
			// Use requestAnimationFrame to ensure DOM is fully rendered
			requestAnimationFrame(() => {
				checkScrollability();
				// Always start at the beginning to show first card fully
				scrollContainer.scrollLeft = 0;
			});
			
			scrollContainer.addEventListener('scroll', checkScrollability);
			// Check on resize
			const resizeObserver = new ResizeObserver(() => {
				// Small delay to ensure layout is complete
				setTimeout(() => {
					checkScrollability();
					// If content no longer overflows, reset scroll position
					if (scrollContainer.scrollWidth <= scrollContainer.clientWidth) {
						scrollContainer.scrollLeft = 0;
					}
				}, 0);
			});
			resizeObserver.observe(scrollContainer);
			return () => {
				scrollContainer.removeEventListener('scroll', checkScrollability);
				resizeObserver.disconnect();
			};
		}
	});
</script>

{#if sortedEvents.length > 0}
	<div class="events-section">
		<h2 class="events-title">Upcoming Events</h2>
		<div class="events-container">
			{#if canScrollLeft}
				<button
					type="button"
					class="scroll-button scroll-button-left"
					on:click={scrollLeft}
					aria-label="Scroll events left"
				>
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M15 18l-6-6 6-6" />
					</svg>
				</button>
			{/if}

			<div class="events-row" bind:this={scrollContainer} on:scroll={checkScrollability}>
				{#each sortedEvents as event}
					<EventCard event={event} />
				{/each}
			</div>

			{#if canScrollRight}
				<button
					type="button"
					class="scroll-button scroll-button-right"
					on:click={scrollRight}
					aria-label="Scroll events right"
				>
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M9 18l6-6-6-6" />
					</svg>
				</button>
			{/if}
		</div>
	</div>
{/if}

<style>
	.events-section {
		width: 100%;
		max-width: 1200px;
		margin: 3rem auto;
		padding: 0 2rem;
	}

	.events-title {
		font-family: 'NY Botanical Gothic', serif;
		font-size: 2rem;
		color: var(--dark);
		margin: 0 0 1.5rem 0;
		text-align: center;
	}

	.events-container {
		position: relative;
		width: 100%;
		overflow: hidden;
		padding: 0 2rem;
	}

	.events-row {
		display: flex;
		justify-content: flex-start;
		gap: 1.5rem;
		overflow-x: auto;
		overflow-y: hidden;
		scroll-behavior: smooth;
		scrollbar-width: thin; /* Firefox - show thin scrollbar */
		scrollbar-color: var(--dark) transparent; /* Firefox scrollbar colors */
		-ms-overflow-style: -ms-autohiding-scrollbar; /* IE and Edge */
		padding: 1rem .4rem;
		width: 100%;
		/* Ensure cards don't overflow container */
		box-sizing: border-box;
	}

	.events-row::-webkit-scrollbar {
		height: 8px; /* Chrome, Safari, Opera - show scrollbar */
	}

	.events-row::-webkit-scrollbar-track {
		background: transparent;
	}

	.events-row::-webkit-scrollbar-thumb {
		background-color: var(--dark);
		border-radius: 4px;
		opacity: 0.5;
	}

	.events-row::-webkit-scrollbar-thumb:hover {
		opacity: 0.8;
	}

	

	.scroll-button {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		border: 2px solid var(--dark);
		color: var(--dark);
		width: 50px;
		height: 50px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.2s;
		z-index: 10;
		padding: 0;
	}

	.scroll-button:hover {
		background-color: var(--helleborous);
		color: var(--dark);
	}

	.scroll-button-left {
		left: 10px;
	}

	.scroll-button-right {
		right: 10px;
	}

	@media (max-width: 768px) {
		.events-section {
			padding: 0 1rem;
		}

		.events-title {
			font-size: 1.6rem;
		}

		.scroll-button {
			width: 40px;
			height: 40px;
		}

		.scroll-button-left {
			left: 5px;
		}

		.scroll-button-right {
			right: 5px;
		}

		.events-row {
			/* On mobile, ensure proper scrolling */
			-webkit-overflow-scrolling: touch;
		}
	}

	/* For very small screens, ensure scrollbar is visible */
	@media (max-width: 480px) {
		.events-row {
			padding-bottom: 1.5rem; /* Extra space for scrollbar */
		}
	}
</style>

