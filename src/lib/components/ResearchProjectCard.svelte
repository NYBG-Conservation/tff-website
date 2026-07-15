<script lang="ts">
	export let title: string;
	export let summary: string;
	export let ongoing = true;
	export let leadName: string | undefined = undefined;
	export let href: string | undefined = undefined;
	export let onSelect: (() => void) | undefined = undefined;
</script>

{#if href}
	<a class="project-card" {href}>
		<div class="project-card-body">
			<span class="status-tag" class:ongoing class:concluded={!ongoing}>
				{ongoing ? 'Ongoing' : 'Concluded'}
			</span>
			<h2 class="project-title">{title}</h2>
			{#if leadName}
				<p class="project-lead">{leadName}</p>
			{/if}
			<p class="project-summary">{summary}</p>
			<span class="read-more-link">
				Read more
				<span class="read-more-arrow" aria-hidden="true">→</span>
			</span>
		</div>
	</a>
{:else}
	<button type="button" class="project-card" on:click={onSelect}>
		<div class="project-card-body">
			<span class="status-tag" class:ongoing class:concluded={!ongoing}>
				{ongoing ? 'Ongoing' : 'Concluded'}
			</span>
			<h2 class="project-title">{title}</h2>
			{#if leadName}
				<p class="project-lead">{leadName}</p>
			{/if}
			<p class="project-summary">{summary}</p>
			<span class="read-more-link">
				Read more
				<span class="read-more-arrow" aria-hidden="true">→</span>
			</span>
		</div>
	</button>
{/if}

<style>
	.project-card {
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.12);
		padding: 0;
		text-align: left;
		display: flex;
		flex-direction: column;
		min-height: 100%;
		box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
		cursor: pointer;
		font: inherit;
		color: inherit;
		text-decoration: none;
		transition:
			transform 0.18s ease,
			box-shadow 0.18s ease;
	}

	.project-card:hover,
	.project-card:focus-visible {
		transform: translateY(-2px);
		box-shadow: 0 8px 22px rgba(0, 0, 0, 0.12);
	}

	.project-card:focus-visible {
		outline: 2px solid #1e2f1e;
		outline-offset: 2px;
	}

	.project-card-body {
		padding: 0.95rem 1rem 1rem;
		display: flex;
		flex-direction: column;
		flex: 1;
		gap: 0.45rem;
	}

	.status-tag {
		display: inline-block;
		padding: 0.2rem 0.55rem;
		border-radius: 999px;
		font-family: 'Martian Mono', serif;
		font-size: 0.72rem;
		letter-spacing: 0.03em;
		text-transform: uppercase;
		line-height: 1.2;
		width: fit-content;
	}

	.status-tag.ongoing {
		background: #d8ead8;
		color: #1b4d1b;
	}

	.status-tag.concluded {
		background: #e8e8e8;
		color: #555;
	}

	.project-title {
		margin: 0;
		padding: 0;
		font-family: 'GT Super Regular', serif;
		font-size: clamp(1.15rem, 1.9vw, 1.6rem);
		line-height: 1.2;
		color: #111;
	}

	.project-lead {
		margin: 0;
		padding: 0;
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		line-height: 1.3;
		color: #555;
	}

	.project-summary {
		margin: 0;
		padding: 0.4rem 0 0.9rem;
		font-family: 'GT Super Regular', serif;
		font-size: 0.96rem;
		line-height: 1.4;
		color: #333;
	}

	.read-more-link {
		margin-top: auto;
		align-self: flex-end;
		padding: 0.15rem 0 0.1rem;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		color: #111;
		position: relative;
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
	}

	.read-more-link::after {
		content: '';
		position: absolute;
		left: 0;
		bottom: -1px;
		width: 0;
		height: 1.5px;
		background-color: #111;
		transition: width 0.22s ease;
	}

	.read-more-arrow {
		transition: transform 0.22s ease;
	}

	.project-card:hover .read-more-link::after,
	.project-card:focus-visible .read-more-link::after {
		width: 100%;
	}

	.project-card:hover .read-more-arrow,
	.project-card:focus-visible .read-more-arrow {
		transform: translateX(3px);
	}
</style>
