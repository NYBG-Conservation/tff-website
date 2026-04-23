<script lang="ts">
	import educationImage from '$lib/assets/project-photos/image.png';
	import bronxRiverImage from '$lib/assets/project-photos/bxrw-thumb.png';

	interface EducationResource {
		title: string;
		description: string;
		image: string;
		link: string;
	}

	const resources: EducationResource[] = [
		{
			title: 'The Welkia Project: Teaching Modules',
			description:
				'A set of twelve classes, organized into three educational modules for teaching students about the historical ecology of New York City.',
			image: educationImage,
			link: 'https://www.welikia.org/resources'
		},
		{
			title: 'Bronx River Watershed Health & Resilience Program',
			description:
				'We co-develop public-facing programming across NYBG that builds knowledge, skills, and long-term stewardship across the Bronx River Watershed.',
			image: bronxRiverImage,
			link: 'https://www.nybg.org/about/sustainability/protect-restore/bronx-river-watershed-health-and-resilience/'
		}
	];
</script>

<div class="education-content">
	<div class="resources-grid">
		{#each resources as resource, index}
			<a
				href={resource.link}
				target="_blank"
				rel="noopener noreferrer"
				class="resource-item"
				class:reversed={index % 2 === 1}
			>
				<div class="resource-image">
					<img src={resource.image} alt={resource.title} />
				</div>
				<div class="resource-text">
					<h2 class="resource-title">{resource.title}</h2>
					<p class="resource-description">{resource.description}</p>
					<span class="resource-link">Learn more <span class="arrow">→</span></span>
				</div>
			</a>
		{/each}
	</div>
</div>

<style>
	.education-content {
		width: 100%;
		max-width: 1200px;
		margin: 2rem auto;
		padding: 0 2rem;
	}

	.resources-grid {
		display: flex;
		flex-direction: column;
		gap: 3rem;
	}

	.resource-item {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		align-items: center;
		text-decoration: none;
		color: var(--dark);
		background-color: white;
		border: 1px solid #ccc;
		overflow: hidden;
		transition: border-color 0.2s ease;
	}

	.resource-item:hover {
		border-color: #999;
	}

	.resource-item.reversed .resource-image {
		order: 2;
	}

	.resource-item.reversed .resource-text {
		order: 1;
	}

	.resource-image {
		width: 100%;
		height: 300px;
		overflow: hidden;
		background-color: var(--light);
	}

	.resource-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 0.3s ease;
	}

	.resource-item:hover .resource-image img {
		transform: scale(1.05);
	}

	.resource-text {
		padding: 2rem;
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.resource-title {
		font-family: 'NY Botanical Gothic', serif;
		font-size: 1.8rem;
		margin: 0 0 1rem 0;
		color: var(--dark);
		line-height: 1.2;
	}

	.resource-description {
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		line-height: 1.6;
		margin: 0 0 1.5rem 0;
		color: var(--dark);
	}

	.resource-link {
		font-family: 'GT Super Regular', serif;
		font-weight: 600;
		color: var(--dark);
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		width: fit-content;
		position: relative;
		padding-bottom: 4px;
	}

	.resource-link .arrow {
		display: inline-block;
		transition: transform 0.3s ease;
	}

	.resource-item:hover .resource-link .arrow {
		transform: translateX(2px);
	}

	.resource-link::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		width: 0;
		height: 2px;
		background-color: var(--dark);
		transition: width 0.3s ease;
	}

	.resource-item:hover .resource-link::after {
		width: 100%;
	}

	@media (max-width: 768px) {
		.education-content {
			padding: 0 1rem;
		}

		.resources-grid {
			gap: 2rem;
		}

		.resource-item {
			grid-template-columns: 1fr;
			gap: 0;
		}

		.resource-item.reversed .resource-image {
			order: 1;
		}

		.resource-item.reversed .resource-text {
			order: 2;
		}

		.resource-image {
			height: 250px;
		}

		.resource-text {
			padding: 1.5rem;
		}

		.resource-title {
			font-size: 1.5rem;
		}
	}
</style>
