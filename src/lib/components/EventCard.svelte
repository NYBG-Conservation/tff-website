<script lang="ts">
export let event: Event;
    

interface Event {
    title: string;
    dates: string[];
    startTime?: string;
    endTime?: string;
    location?: string;
    description?: string;
    link?: string;
    action?: string;
}
	function formatDate(dateString: string): string {
		try {
			const date = new Date(dateString);
			return date.toLocaleDateString('en-US', {
				month: 'short',
				day: 'numeric'
			});
		} catch {
			return dateString;
		}
	}

	function formatMultipleDates(dateStrings: string[]): string {
		if (dateStrings.length === 0) return '';
		if (dateStrings.length === 1) return formatDate(dateStrings[0]);

		try {
			// Parse all dates
			const dates = dateStrings
				.map((ds) => {
					try {
						return new Date(ds);
					} catch {
						return null;
					}
				})
				.filter((d): d is Date => d !== null);

			if (dates.length === 0) return dateStrings.join(', ');

			// Group dates by month and year
			const groups: Map<string, number[]> = new Map();

			dates.forEach((date) => {
				const month = date.toLocaleDateString('en-US', { month: 'short' });
				const year = date.getFullYear();
				const day = date.getDate();
				const key = `${month} ${year}`;

				if (!groups.has(key)) {
					groups.set(key, []);
				}
				groups.get(key)!.push(day);
			});

			// Format each group
			const formattedGroups: string[] = [];
			groups.forEach((days, monthYear) => {
				days.sort((a, b) => a - b);
				const daysStr = days.join(', ');
				formattedGroups.push(`${monthYear.split(' ')[0]} ${daysStr}`);
			});

			return formattedGroups.join('; ');
		} catch {
			// Fallback to individual formatting
			return dateStrings.map((ds) => formatDate(ds)).join(', ');
		}
	}

	function formatTimeRange(startTime?: string, endTime?: string): string {
		if (!startTime && !endTime) return '';
		if (startTime && endTime) {
			return `${startTime} - ${endTime}`;
		}
		return startTime || endTime || '';
	}

	$: hasLink = event.link && event.action !== 'none';
	$: linkText = event.action === 'register' ? 'Register here' : 'Learn more';
</script>

{#if hasLink}
	<a href={event.link} target="_blank" rel="noopener noreferrer" class="event-card">
		<div class="event-date">
			{formatMultipleDates(event.dates)}
		</div>
		<h3 class="event-title">{event.title}</h3>
		{#if event.startTime || event.endTime}
			<p class="event-meta">
				{formatTimeRange(event.startTime, event.endTime)}
			</p>
		{/if}
		{#if event.location}
			<p class="event-meta event-location">
				<span class="location-icon" aria-hidden="true">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
				</span>
				{event.location}
			</p>
		{/if}
		{#if event.description}
			<p class="event-description">{event.description}</p>
		{/if}
		<span class="event-link">{linkText}<span class="arrow">→</span></span>
	</a>
{:else}
	<div class="event-card">
		<div class="event-date">
			{formatMultipleDates(event.dates)}
		</div>
		<h3 class="event-title">{event.title}</h3>
		{#if event.startTime || event.endTime}
			<p class="event-meta">
				{formatTimeRange(event.startTime, event.endTime)}
			</p>
		{/if}
		{#if event.location}
			<p class="event-meta event-location">
				<span class="location-icon" aria-hidden="true">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
				</span>
				{event.location}
			</p>
		{/if}
		{#if event.description}
			<p class="event-description">{event.description}</p>
		{/if}
	</div>
{/if}

<style>
	.event-card {
		min-width: 300px;
		width: 300px;
		max-width: calc(100vw - 4rem); /* Ensure card doesn't exceed viewport minus padding */
		background-color: white;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		color: var(--dark);
		flex-shrink: 0;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
		transition: box-shadow 0.2s ease;
		text-decoration: none;
	}

	a.event-card {
		cursor: pointer;
	}

	a.event-card:hover {
		box-shadow: 0 8px 12px rgba(0, 0, 0, 0.25);
	}

	@media (max-width: 480px) {
		.event-card {
			min-width: 280px;
			width: 280px;
			max-width: calc(100vw - 3rem);
		}
	}

	.event-date {
		font-family: 'GT Super Regular', serif;
		color: #6b7280;
		font-weight: 600;
		margin-bottom: 0.5rem;
		font-size: 1rem;
	}

	.event-title {
		font-family: 'GT Super Regular', serif;
		font-size: 1.4rem;
		margin: 0 0 1rem 0;
		color: var(--dark);
		line-height: 1.2;
	}

	.event-meta {
		font-family: 'GT Super Regular', serif;
		margin: 0.25rem 0;
		font-size: 1rem;
		color: var(--dark);
		line-height: 1.2;
	}

	.event-location {
		display: flex;
		align-items: center;
		gap: 0.35rem;
	}

	.location-icon {
		display: inline-flex;
		flex-shrink: 0;
		color: var(--dark);
	}

	.event-description {
		font-family: 'GT Super Regular', serif;
		line-height: 1.3;
		margin: 1rem 0;
		flex: 1;
		font-size: 1rem;
		color: var(--dark);
	}

	.event-link {
		display: inline-flex;
		align-items: center;
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
		gap: 0.25rem;
	}

	.event-link::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		width: 0;
		height: 2px;
		background-color: var(--dark);
		transition: width 0.3s ease;
	}

	.event-link:hover::after,
	a.event-card:hover .event-link::after {
		width: 100%;
	}

	.arrow {
		display: inline-block;
		transition: transform 0.3s ease;
	}

	.event-link:hover .arrow,
	a.event-card:hover .event-link .arrow {
		transform: translateX(2px);
	}
</style>