<script lang="ts">
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	function formatDate(dateString?: string): string {
		if (!dateString?.trim()) return '';
		const s = dateString.trim();
		try {
			// CSV uses US format (M/D/YYYY or MM-DD-YYYY). new Date(string) is unreliable on Safari/mobile.
			const parts = s.split(/[-\/]/).map((p) => parseInt(p, 10));
			if (parts.length >= 3 && parts.every((n) => !isNaN(n))) {
				const [month, day, year] = parts;
				const date = new Date(year, month - 1, day);
				if (!isNaN(date.getTime())) {
					return date.toLocaleDateString('en-US', {
						year: 'numeric',
						month: 'long',
						day: 'numeric'
					});
				}
			}
			// Fallback for ISO or other formats
			const date = new Date(s);
			return isNaN(date.getTime()) ? s : date.toLocaleDateString('en-US', {
				year: 'numeric',
				month: 'long',
				day: 'numeric'
			});
		} catch {
			return s;
		}
	}
</script>

<div class="press-content">
	{#if data.pressItems && data.pressItems.length > 0}
		<div class="press-list">
			{#each data.pressItems as item}
				{#if item.link}
					<a
						href={item.link}
						target="_blank"
						rel="noopener noreferrer"
						class="press-item"
					>
						<div class="press-header">
							<h2 class="press-title">{@html item.title}</h2>
							{#if item.publication || item.date}
								<div class="press-meta">
									{#if item.publication}
										<span class="publication">{item.publication}</span>
									{/if}
									{#if item.date}
										<span class="date">{formatDate(item.date)}</span>
									{/if}
								</div>
							{/if}
						</div>
						{#if item.description}
							<p class="press-description">{item.description}</p>
						{/if}
						<span class="press-link">Read more <span class="arrow">→</span></span>
					</a>
				{:else}
					<article class="press-item">
						<div class="press-header">
							<h2 class="press-title">{@html item.title}</h2>
							{#if item.publication || item.date}
								<div class="press-meta">
									{#if item.publication}
										<span class="publication">{item.publication}</span>
									{/if}
									{#if item.date}
										<span class="date">{formatDate(item.date)}</span>
									{/if}
								</div>
							{/if}
						</div>
						{#if item.description}
							<p class="press-description">{item.description}</p>
						{/if}
					</article>
				{/if}
			{/each}
		</div>
	{:else}
		<p class="no-press">No press items available at this time.</p>
	{/if}
</div>

<style>
	.press-content {
		width: 100%;
		max-width: 900px;
		margin: 2rem auto;
		padding: 0 2rem;
	}

	.press-list {
		display: flex;
		flex-direction: column;
		gap: 2.5rem;
	}

	.press-item {
		background-color: white;
		padding: 1.4rem;
		border: 1px solid #ccc;
		transition: border-color 0.2s ease;
		display: block;
		text-decoration: none;
		color: var(--dark);
		cursor: pointer;
	}

	.press-item:hover {
		border-color: #999;
	}


	.press-title {
		font-family: 'GT Super Bold', serif;
		font-size: 1.2rem;
		margin: 0 0 0.4rem 0;
		color: var(--dark);
		line-height: 1.2;
	}

	.press-meta {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		color: var(--dark);
		opacity: 0.8;
	}

	.publication {
		font-weight: 600;
	}

	.date {
		font-style: italic;
	}

	.press-description {
		font-family: 'GT Super Regular', serif;
		line-height: 1.6;
		margin: .4rem 0;
		color: var(--dark);
		font-size: 1rem;
	}

	.press-link {
		display: inline-flex;
		align-items: center;
		margin-top: .6rem;
		color: var(--dark);
		text-decoration: none;
		font-family: 'GT Super Regular', serif;
		font-weight: 600;
		position: relative;
		padding-bottom: 4px;
		transition: color 0.3s ease;
		width: fit-content;
		gap: 0.25rem;
	}

	.press-link .arrow {
		display: inline-block;
		transition: transform 0.3s ease;
	}

	.press-item:hover .press-link .arrow {
		transform: translateX(2px);
	}

	.press-link::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		width: 0;
		height: 2px;
		background-color: var(--dark);
		transition: width 0.3s ease;
	}

	.press-item:hover .press-link::after {
		width: 100%;
	}

	.no-press {
		font-family: 'GT Super Regular', serif;
		font-size: 1.15rem;
		text-align: center;
		color: var(--dark);
		margin: 3rem auto;
	}

	@media (max-width: 768px) {
		.press-content {
			padding: 0 1rem;
		}

		.press-item {
			padding: 1.5rem;
		}

		.press-title {
			font-size: 1.4rem;
		}
	}
</style>

