<script lang="ts">
	import { createDataset, getMetadataFieldTypes, listDatasets, type MetadataField } from '$lib/api/datasets';
	import { ensureCsrfCookie } from '$lib/api/client';
	import { onMount } from 'svelte';

	let loading = true;
	let saving = false;
	let error = '';
	let datasets: Awaited<ReturnType<typeof listDatasets>> = [];
	let fieldTypes: Awaited<ReturnType<typeof getMetadataFieldTypes>> = [];

	let title = '';
	let description = '';
	let cadence: 'annual' | 'one_off' | 'continuous' = 'annual';
	let organization = 1;
	let metadataFields: MetadataField[] = [];

	function addMetadataField() {
		metadataFields = [
			...metadataFields,
			{
				key: '',
				label: '',
				field_type: 'text',
				unit: '',
				required: false,
				allowed_values: [],
				sort_order: metadataFields.length
			}
		];
	}

	function updateMetadataField(index: number, key: keyof MetadataField, value: unknown) {
		metadataFields = metadataFields.map((field, i) => (i === index ? { ...field, [key]: value } : field));
	}

	async function refreshData() {
		loading = true;
		error = '';
		try {
			datasets = await listDatasets();
			fieldTypes = await getMetadataFieldTypes();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load datasets';
		} finally {
			loading = false;
		}
	}

	async function submitDataset() {
		saving = true;
		error = '';
		try {
			await ensureCsrfCookie();
			await createDataset({
				title,
				description,
				cadence,
				status: 'draft',
				organization,
				additional_research_partners: [],
				paper_links: [],
				metadata_schema_version: 1,
				metadata_fields: metadataFields.filter((field) => field.key && field.label),
				metadata_values: []
			});
			title = '';
			description = '';
			metadataFields = [];
			await refreshData();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to create dataset';
		} finally {
			saving = false;
		}
	}

	onMount(async () => {
		await refreshData();
	});
</script>

<section class="researcher-datasets">
	<h1>Researcher Datasets</h1>
	<p class="intro">
		Create and manage datasets with flexible metadata definitions. The backend enforces ownership-based edit
		permissions.
	</p>

	{#if error}
		<p class="error">{error}</p>
	{/if}

	<div class="layout">
		<form
			class="create-form"
			on:submit|preventDefault={() => {
				void submitDataset();
			}}
		>
			<h2>Create Dataset</h2>
			<label>
				Title
				<input bind:value={title} required />
			</label>
			<label>
				Description
				<textarea bind:value={description} rows={3}></textarea>
			</label>
			<label>
				Cadence
				<select bind:value={cadence}>
					<option value="annual">Annual</option>
					<option value="one_off">One-off</option>
					<option value="continuous">Continuous</option>
				</select>
			</label>
			<label>
				Organization ID
				<input type="number" min="1" bind:value={organization} required />
			</label>

			<div class="metadata-builder">
				<div class="metadata-header">
					<h3>Metadata Fields</h3>
					<button type="button" on:click={addMetadataField}>Add field</button>
				</div>
				{#each metadataFields as field, index}
					<div class="metadata-row">
						<input
							placeholder="key (e.g. canopy_percent)"
							value={field.key}
							on:input={(e) => updateMetadataField(index, 'key', (e.target as HTMLInputElement).value)}
						/>
						<input
							placeholder="label"
							value={field.label}
							on:input={(e) => updateMetadataField(index, 'label', (e.target as HTMLInputElement).value)}
						/>
						<select
							value={field.field_type}
							on:change={(e) =>
								updateMetadataField(index, 'field_type', (e.target as HTMLSelectElement).value)}
						>
							{#each fieldTypes as type}
								<option value={type.value}>{type.label}</option>
							{/each}
						</select>
					</div>
				{/each}
			</div>

			<button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Create Dataset'}</button>
		</form>

		<div class="datasets-panel">
			<h2>Accessible Datasets</h2>
			{#if loading}
				<p>Loading datasets…</p>
			{:else if datasets.length === 0}
				<p>No datasets yet.</p>
			{:else}
				<ul>
					{#each datasets as dataset}
						<li>
							<strong>{dataset.title}</strong>
							<span>{dataset.cadence}</span>
							<span>Owner: {dataset.owner_username}</span>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	</div>
</section>

<style>
	.researcher-datasets {
		max-width: 1100px;
		margin: 0 auto;
		padding: 2rem 1rem 4rem;
	}

	.intro {
		margin-bottom: 1.2rem;
		font-family: 'GT Super Regular', serif;
	}

	.error {
		color: #8a1c1c;
		font-family: 'GT Super Regular', serif;
	}

	.layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}

	.create-form,
	.datasets-panel {
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.12);
		padding: 1rem;
	}

	label {
		display: grid;
		gap: 0.4rem;
		margin-bottom: 0.85rem;
	}

	input,
	textarea,
	select,
	button {
		font: inherit;
		padding: 0.45rem 0.55rem;
	}

	.metadata-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.metadata-row {
		display: grid;
		grid-template-columns: 1fr 1fr 0.8fr;
		gap: 0.45rem;
		margin-bottom: 0.45rem;
	}

	.datasets-panel ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.65rem;
	}

	.datasets-panel li {
		border: 1px solid rgba(0, 0, 0, 0.12);
		padding: 0.55rem;
		display: grid;
		gap: 0.1rem;
	}

	@media (max-width: 900px) {
		.layout {
			grid-template-columns: 1fr;
		}
	}
</style>
