<script lang="ts">
	const stats = [
		{ value: '400+', label: 'Years of NYC ecological history mapped' },
		{ value: '8', label: 'Active research projects' },
		{ value: '30+', label: "Community & gov't partners" },
		{ value: '5', label: 'Boroughs served' }
	];
</script>

<div class="stats">
	<div class="stats-inner">
		{#each stats as stat, i}
			<div class="stat">
				<span class="stat-value">{stat.value}</span>
				<span class="stat-label">{stat.label}</span>
			</div>
			{#if i < stats.length - 1}
				<div class="stat-divider" aria-hidden="true"></div>
			{/if}
		{/each}
	</div>
</div>

<style>
	.stats {
		background-color: var(--bg-light);
		padding: 2rem 20px;
		border-top: 1px solid rgba(0, 0, 0, 0.08);
	}

	.stats-inner {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		align-items: stretch;
		justify-content: space-between;
		gap: 1rem;
	}

	.stat {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		min-width: 0;
	}

	.stat-value {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.75rem, 3vw, 2.5rem);
		font-weight: 800;
		color: var(--dark);
		line-height: 1.1;
		display: block;
		margin-bottom: 0.35rem;
	}

	.stat-label {
		font-family: 'GT Super Regular', serif;
		font-size: 0.7rem;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--dark);
		opacity: 0.85;
		line-height: 1.3;
	}

	.stat-divider {
		width: 1px;
		background-color: rgba(0, 0, 0, 0.15);
		flex-shrink: 0;
	}

	@media (max-width: 768px) {
		.stats-inner {
			flex-wrap: wrap;
			justify-content: center;
			gap: 1.5rem;
		}

		.stat {
			flex: 0 1 calc(50% - 1rem);
		}

		.stat-divider {
			display: none;
		}
	}

	@media (max-width: 480px) {
		.stats {
			padding: 1.5rem 1rem;
		}

		.stat {
			flex: 1 1 100%;
		}
	}
</style>
