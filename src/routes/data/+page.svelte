<script lang="ts">
	import { page } from '$app/stores';
	import { datasetRecords } from '$lib/data/datasetRecords';
	import { researchProjects } from '$lib/data/researchProjects';

	$: selectedProjectId = $page.url.searchParams.get('project') ?? '';
	$: selectedProject = researchProjects.find((project) => project.id === selectedProjectId);
	$: visibleDatasets = selectedProjectId
		? datasetRecords.filter((dataset) => dataset.projectId === selectedProjectId)
		: datasetRecords;
</script>

<section class="research-content">
	<p class="placeholder-note">
		Dataset records are manually wired and can be filtered by project.
	</p>
	{#if selectedProject}
		<p class="active-filter">
			Showing datasets linked to <strong>{selectedProject.title}</strong>.
			<a href="/data">Clear filter</a>
		</p>
	{/if}

	<div class="table-wrap">
		<table class="research-table">
			<thead>
				<tr>
					<th>Dataset</th>
					<th>Organization</th>
					<th>Cadence</th>
					<th>Status</th>
					<th>Last Updated</th>
				</tr>
			</thead>
			<tbody>
				{#if visibleDatasets.length === 0}
					<tr>
						<td colspan="5" class="empty-row">No research records available for this project yet.</td>
					</tr>
				{:else}
					{#each visibleDatasets as dataset}
						<tr>
							<td>{dataset.title}</td>
							<td>{dataset.organization}</td>
							<td>{dataset.cadence}</td>
							<td>{dataset.status}</td>
							<td>{dataset.lastUpdated}</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</section>

<style>
	.research-content {
		max-width: 1100px;
		margin: 2rem auto;
		padding: 0 1rem 2rem;
	}

	.placeholder-note {
		font-family: 'GT Super Regular', serif;
		margin: 0 0 1rem 0;
		color: #222;
	}

	.active-filter {
		font-family: 'GT Super Regular', serif;
		margin: 0 0 1rem 0;
		color: #222;
	}

	.active-filter a {
		margin-left: 0.4rem;
	}

	.table-wrap {
		overflow-x: auto;
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.15);
	}

	.research-table {
		width: 100%;
		border-collapse: collapse;
		min-width: 650px;
	}

	.research-table th,
	.research-table td {
		padding: 0.75rem 0.85rem;
		text-align: left;
		border-bottom: 1px solid rgba(0, 0, 0, 0.12);
		font-family: 'GT Super Regular', serif;
	}

	.research-table th {
		font-family: 'GT Super Bold', serif;
		background: #f4f4f4;
	}

	.empty-row {
		text-align: center;
		color: #666;
	}
</style>