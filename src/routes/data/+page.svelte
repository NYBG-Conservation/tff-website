<script lang="ts">
	import { goto } from '$app/navigation';
	import { onDestroy, onMount } from 'svelte';
	import { slide } from 'svelte/transition';
	import { getCurrentUser } from '$lib/api/accounts';
	import type { PublicDatasetFile, PublicDatasetRecord, PublicResearchProject } from '$lib/api/public';
	import { djangoAdminDatasetUrl } from '$lib/api/djangoAdmin';
	import { fileDisplayTitle, fileTypeLabel } from '$lib/utils/fileTypes';

	type SortColumn = 'title' | 'organization' | 'project_slug' | 'cadence' | 'status' | 'last_updated';
	type SortDirection = 'asc' | 'desc';

	export let data;

	$: researchProjects = data.researchProjects as PublicResearchProject[];
	$: datasetRecords = data.datasetRecords as PublicDatasetRecord[];
	$: initialProjectSlug = data.projectSlug as string;
	$: apiError = data.apiError as string | null;

	let browserAuthenticated: boolean | null = null;
	$: isAuthenticated = browserAuthenticated ?? (data.isAuthenticated as boolean);

	let expandedDatasetId: number | null = null;
	let isMobile = false;

	let searchQuery = '';
	let filterOrganization = 'all';
	let filterCadence = 'all';
	let filterStatus = 'all';
	let filterProject = 'all';
	let sortColumn: SortColumn = 'title';
	let sortDirection: SortDirection = 'asc';

	$: filterProject = initialProjectSlug || filterProject;

	$: organizations = [...new Set(datasetRecords.map((record) => record.organization))].sort();
	$: cadences = [...new Set(datasetRecords.map((record) => record.cadence))].sort();
	$: statuses = [...new Set(datasetRecords.map((record) => record.status))].sort();

	$: projectOptions = researchProjects
		.filter((project) => datasetRecords.some((record) => record.project_slug === project.slug))
		.sort((a, b) => a.title.localeCompare(b.title));

	$: filteredRecords = datasetRecords.filter((record) => {
		const query = searchQuery.trim().toLowerCase();
		const projectTitle =
			researchProjects.find((project) => project.slug === record.project_slug)?.title ?? '';

		if (filterProject !== 'all' && record.project_slug !== filterProject) {
			return false;
		}
		if (filterOrganization !== 'all' && record.organization !== filterOrganization) {
			return false;
		}
		if (filterCadence !== 'all' && record.cadence !== filterCadence) {
			return false;
		}
		if (filterStatus !== 'all' && record.status !== filterStatus) {
			return false;
		}
		if (!query) {
			return true;
		}

		return [record.title, record.description ?? '', record.organization, projectTitle, record.project_slug]
			.join(' ')
			.toLowerCase()
			.includes(query);
	});

	$: visibleRecords = [...filteredRecords].sort((a, b) => compareRecords(a, b, sortColumn, sortDirection));

	$: hasActiveFilters =
		searchQuery.trim() !== '' ||
		filterOrganization !== 'all' ||
		filterCadence !== 'all' ||
		filterStatus !== 'all' ||
		filterProject !== 'all';

	function projectTitleFor(slug: string): string {
		if (!slug) return '—';
		return researchProjects.find((project) => project.slug === slug)?.title ?? slug;
	}

	function compareRecords(
		a: PublicDatasetRecord,
		b: PublicDatasetRecord,
		column: SortColumn,
		direction: SortDirection
	): number {
		let result = 0;

		if (column === 'last_updated') {
			result = a.last_updated.localeCompare(b.last_updated);
		} else if (column === 'project_slug') {
			result = projectTitleFor(a.project_slug).localeCompare(projectTitleFor(b.project_slug));
		} else {
			result = String(a[column] ?? '').localeCompare(String(b[column] ?? ''));
		}

		return direction === 'asc' ? result : -result;
	}

	function toggleSort(column: SortColumn) {
		if (sortColumn === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
			return;
		}

		sortColumn = column;
		sortDirection = column === 'last_updated' ? 'desc' : 'asc';
	}

	function sortAriaSort(column: SortColumn): 'ascending' | 'descending' | 'none' {
		if (sortColumn !== column) return 'none';
		return sortDirection === 'asc' ? 'ascending' : 'descending';
	}

	function onProjectFilterChange(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value;
		filterProject = value;
		const path = value === 'all' ? '/data' : `/data?project=${encodeURIComponent(value)}`;
		goto(path, { replaceState: true, keepFocus: true, noScroll: true });
	}

	function clearFilters() {
		searchQuery = '';
		filterOrganization = 'all';
		filterCadence = 'all';
		filterStatus = 'all';
		filterProject = 'all';
		if (initialProjectSlug) {
			goto('/data', { replaceState: true, keepFocus: true, noScroll: true });
		}
	}

	function toggleExpanded(datasetId: number) {
		expandedDatasetId = expandedDatasetId === datasetId ? null : datasetId;
	}

	function handleRowKeydown(event: KeyboardEvent, datasetId: number) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			toggleExpanded(datasetId);
		}
	}

	function detectMobile() {
		if (typeof window === 'undefined') return;

		const width = window.innerWidth;
		const userAgent = navigator.userAgent.toLowerCase();
		const isTablet =
			/ipad|tablet|android(?!.*mobile)/i.test(userAgent) || (width >= 768 && width < 1024);

		isMobile = width < 768 && !isTablet;
	}

	function fileDownloadEnabled(file: PublicDatasetFile): boolean {
		return file.download_available && Boolean(file.download_url) && !isMobile;
	}

	function hasDownloadableFiles(files: PublicDatasetFile[] | undefined): boolean {
		return Boolean(files?.some((file) => file.download_available && file.download_url));
	}

	onMount(() => {
		detectMobile();
		window.addEventListener('resize', detectMobile);

		if (!data.isAuthenticated) {
			void getCurrentUser()
				.then((user) => {
					browserAuthenticated = Boolean(user?.id);
				})
				.catch(() => {
					browserAuthenticated = false;
				});
		}
	});

	onDestroy(() => {
		if (typeof window !== 'undefined') {
			window.removeEventListener('resize', detectMobile);
		}
	});
</script>

<section class="data-content">
	{#if apiError}
		<p class="api-error">Dataset records are temporarily unavailable. ({apiError})</p>
	{/if}

	<div class="filters-panel">
		<div class="filters-row">
			<label class="filter-field filter-search">
				<span class="filter-label">Search</span>
				<input
					type="search"
					placeholder="Search datasets…"
					bind:value={searchQuery}
					aria-label="Search datasets"
				/>
			</label>

			<label class="filter-field">
				<span class="filter-label">Project</span>
				<select value={filterProject} on:change={onProjectFilterChange} aria-label="Filter by project">
					<option value="all">All projects</option>
					{#each projectOptions as project}
						<option value={project.slug}>{project.title}</option>
					{/each}
				</select>
			</label>

			<label class="filter-field">
				<span class="filter-label">Organization</span>
				<select bind:value={filterOrganization} aria-label="Filter by organization">
					<option value="all">All organizations</option>
					{#each organizations as organization}
						<option value={organization}>{organization}</option>
					{/each}
				</select>
			</label>

			<label class="filter-field">
				<span class="filter-label">Cadence</span>
				<select bind:value={filterCadence} aria-label="Filter by cadence">
					<option value="all">All cadences</option>
					{#each cadences as cadence}
						<option value={cadence}>{cadence}</option>
					{/each}
				</select>
			</label>

			<label class="filter-field">
				<span class="filter-label">Status</span>
				<select bind:value={filterStatus} aria-label="Filter by status">
					<option value="all">All statuses</option>
					{#each statuses as status}
						<option value={status}>{status}</option>
					{/each}
				</select>
			</label>
		</div>

		<div class="filters-meta">
			<p class="results-count">
				Showing {visibleRecords.length} of {datasetRecords.length} datasets
			</p>
			{#if hasActiveFilters}
				<button type="button" class="clear-filters" on:click={clearFilters}>Clear filters</button>
			{/if}
		</div>
	</div>

	<div class="table-wrap">
		<table class="data-table">
			<thead>
				<tr>
					<th class="expand-col" aria-hidden="true"></th>
					<th aria-sort={sortAriaSort('title')}>
						<button type="button" class="sort-button" on:click={() => toggleSort('title')}>
							Dataset
							{#if sortColumn === 'title'}
								<span class="sort-indicator" aria-hidden="true">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th aria-sort={sortAriaSort('project_slug')}>
						<button type="button" class="sort-button" on:click={() => toggleSort('project_slug')}>
							Project
							{#if sortColumn === 'project_slug'}
								<span class="sort-indicator" aria-hidden="true">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th aria-sort={sortAriaSort('organization')}>
						<button type="button" class="sort-button" on:click={() => toggleSort('organization')}>
							Organization
							{#if sortColumn === 'organization'}
								<span class="sort-indicator" aria-hidden="true">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th aria-sort={sortAriaSort('cadence')}>
						<button type="button" class="sort-button" on:click={() => toggleSort('cadence')}>
							Cadence
							{#if sortColumn === 'cadence'}
								<span class="sort-indicator" aria-hidden="true">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th aria-sort={sortAriaSort('status')}>
						<button type="button" class="sort-button" on:click={() => toggleSort('status')}>
							Status
							{#if sortColumn === 'status'}
								<span class="sort-indicator" aria-hidden="true">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
					<th aria-sort={sortAriaSort('last_updated')}>
						<button type="button" class="sort-button" on:click={() => toggleSort('last_updated')}>
							Last updated
							{#if sortColumn === 'last_updated'}
								<span class="sort-indicator" aria-hidden="true">{sortDirection === 'asc' ? '↑' : '↓'}</span>
							{/if}
						</button>
					</th>
				</tr>
			</thead>
			<tbody>
				{#if datasetRecords.length === 0}
					<tr>
						<td colspan="7" class="empty-row">No public datasets are available yet.</td>
					</tr>
				{:else if visibleRecords.length === 0}
					<tr>
						<td colspan="7" class="empty-row">No datasets match the current filters.</td>
					</tr>
				{:else}
					{#each visibleRecords as dataset (dataset.id)}
						<tr
							class="data-row"
							class:expanded={expandedDatasetId === dataset.id}
							on:click={() => toggleExpanded(dataset.id)}
							on:keydown={(event) => handleRowKeydown(event, dataset.id)}
							tabindex="0"
							role="button"
							aria-expanded={expandedDatasetId === dataset.id}
							aria-controls={`dataset-detail-${dataset.id}`}
						>
							<td class="expand-cell" aria-hidden="true">
								<span class="expand-icon">{expandedDatasetId === dataset.id ? '▾' : '▸'}</span>
							</td>
							<td class="dataset-title">{dataset.title}</td>
							<td>{projectTitleFor(dataset.project_slug)}</td>
							<td>{dataset.organization}</td>
							<td>{dataset.cadence}</td>
							<td>{dataset.status}</td>
							<td>{dataset.last_updated}</td>
						</tr>
						{#if expandedDatasetId === dataset.id}
							<tr class="detail-row">
								<td colspan="7" id={`dataset-detail-${dataset.id}`}>
									<div class="detail-panel" transition:slide={{ duration: 220 }}>
										{#if dataset.description}
											<p class="detail-description">{dataset.description}</p>
										{/if}

										<dl class="detail-metadata">
											{#if dataset.data_type}
												<div class="detail-item">
													<dt>Data type</dt>
													<dd>{dataset.data_type}</dd>
												</div>
											{/if}
											<div class="detail-item">
												<dt>Project</dt>
												<dd>{projectTitleFor(dataset.project_slug)}</dd>
											</div>
											<div class="detail-item">
												<dt>Organization</dt>
												<dd>{dataset.organization}</dd>
											</div>
											<div class="detail-item">
												<dt>Cadence</dt>
												<dd>{dataset.cadence}</dd>
											</div>
											<div class="detail-item">
												<dt>Status</dt>
												<dd>{dataset.status}</dd>
											</div>
											<div class="detail-item">
												<dt>Last updated</dt>
												<dd>{dataset.last_updated}</dd>
											</div>
										</dl>

										{#if dataset.metadata_fields?.length}
											<div class="detail-section">
												<h3>Metadata schema</h3>
												<ul class="detail-list">
													{#each dataset.metadata_fields as field}
														<li>
															<strong>{field.label}</strong>
															<span>
																{field.field_type}
																{#if field.unit}
																	({field.unit})
																{/if}
																{#if field.required}
																	· required
																{/if}
															</span>
														</li>
													{/each}
												</ul>
											</div>
										{/if}

										{#if dataset.files?.length}
											<div class="detail-section">
												<h3>Public files</h3>
												{#if isMobile && hasDownloadableFiles(dataset.files)}
													<p class="mobile-download-note">
														Data files are large. Download links are available on desktop.
													</p>
												{/if}
												<ul class="file-list">
													{#each dataset.files as file}
														<li class="file-item">
															{#if fileDownloadEnabled(file)}
																<a
																	class="file-title file-download-link"
																	href={file.download_url}
																	target="_blank"
																	rel="noopener noreferrer"
																	on:click|stopPropagation
																>
																	{fileDisplayTitle(file.file_name)}
																</a>
															{:else}
																<span class="file-title">{fileDisplayTitle(file.file_name)}</span>
															{/if}
															<span class="file-type">{fileTypeLabel(file.file_name)}</span>
														</li>
													{/each}
												</ul>
											</div>
										{/if}

										<div class="detail-actions">
											<a
												class="manage-link"
												href={djangoAdminDatasetUrl(dataset.id)}
												on:click|stopPropagation
												target="_blank"
											>
												Manage dataset entry →
											</a>
											{#if !isAuthenticated}
												<p class="detail-note">
													Sign in with your researcher account to edit this dataset. Access is
													limited to project owners and team members.
												</p>
											{/if}
										</div>
									</div>
								</td>
							</tr>
						{/if}
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</section>

<style>
	.data-content {
		max-width: 1100px;
		margin: 0 auto;
		padding: 0 1rem 2rem;
		overflow-x: clip;
	}

	.api-error {
		font-family: 'GT Super Regular', serif;
		color: #7a1e1e;
		margin: 0 0 1rem;
	}

	.filters-panel {
		margin-bottom: 1rem;
		padding: 1rem;
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.12);
	}

	.filters-row {
		display: grid;
		grid-template-columns: minmax(180px, 1.4fr) repeat(4, minmax(130px, 1fr));
		gap: 0.75rem;
	}

	.filter-field {
		display: grid;
		gap: 0.3rem;
		font-family: 'GT Super Regular', serif;
	}

	.filter-label {
		font-family: 'GT Super Bold', serif;
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #5a5a5a;
	}

	.filter-field input,
	.filter-field select {
		width: 100%;
		padding: 0.5rem 0.55rem;
		border: 1px solid rgba(0, 0, 0, 0.18);
		background: #fff;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		color: #222;
	}

	.filters-meta {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		margin-top: 0.85rem;
	}

	.results-count {
		margin: 0;
		font-family: 'GT Super Regular', serif;
		font-size: 0.92rem;
		color: #555;
	}

	.clear-filters {
		border: 1px solid rgba(0, 0, 0, 0.18);
		background: #fff;
		padding: 0.4rem 0.75rem;
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		cursor: pointer;
	}

	.clear-filters:hover,
	.clear-filters:focus-visible {
		background: rgba(200, 181, 0, 0.12);
	}

	.table-wrap {
		overflow-x: auto;
		max-width: 100%;
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.15);
		-webkit-overflow-scrolling: touch;
	}

	.data-table {
		width: 100%;
		border-collapse: collapse;
		table-layout: fixed;
	}

	.expand-col,
	.expand-cell {
		width: 2rem;
		padding-right: 0;
	}

	.data-table th:nth-child(2),
	.data-table td:nth-child(2) {
		width: 34%;
	}

	.data-table th:nth-child(3),
	.data-table td:nth-child(3) {
		width: 14%;
	}

	.data-table th:nth-child(4),
	.data-table td:nth-child(4) {
		width: 16%;
	}

	.data-table th:nth-child(5),
	.data-table td:nth-child(5) {
		width: 10%;
	}

	.data-table th:nth-child(6),
	.data-table td:nth-child(6) {
		width: 10%;
	}

	.data-table th:nth-child(7),
	.data-table td:nth-child(7) {
		width: 12%;
	}

	.expand-icon {
		display: inline-block;
		width: 1rem;
		color: #555;
		font-size: 0.85rem;
	}

	.data-row {
		cursor: pointer;
		transition: background 0.15s ease;
	}

	.data-row:hover,
	.data-row.expanded,
	.data-row:focus-visible {
		background: rgba(200, 181, 0, 0.1);
	}

	.data-row:focus-visible {
		outline: 2px solid #1e2f1e;
		outline-offset: -2px;
	}

	.detail-row td {
		padding: 0;
		border-bottom: 1px solid rgba(0, 0, 0, 0.12);
		background: #faf9f6;
		/* Allow fixed-layout table cells to shrink so detail content wraps */
		max-width: 0;
	}

	.detail-panel {
		padding: 1rem 1.1rem 1.15rem 2.6rem;
		min-width: 0;
		max-width: 100%;
		box-sizing: border-box;
	}

	.detail-description {
		margin: 0 0 1rem;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		line-height: 1.6;
		color: #222;
	}

	.detail-metadata {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.75rem 1rem;
		margin: 0 0 1rem;
	}

	.detail-item {
		margin: 0;
	}

	.detail-metadata dt {
		font-family: 'GT Super Bold', serif;
		font-size: 0.76rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #5a5a5a;
		margin: 0 0 0.15rem;
	}

	.detail-metadata dd {
		margin: 0;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		color: #222;
	}

	.detail-section h3 {
		margin: 0 0 0.45rem;
		font-family: 'GT Super Bold', serif;
		font-size: 0.95rem;
		color: #1e2f1e;
	}

	.detail-list {
		margin: 0 0 1rem;
		padding-left: 1.1rem;
	}

	.detail-list li {
		margin-bottom: 0.35rem;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		line-height: 1.45;
	}

	.file-list {
		list-style: none;
		margin: 0 0 1rem;
		padding: 0;
		border-top: 1px solid rgba(0, 0, 0, 0.08);
		max-width: 100%;
	}

	.file-item {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 0.15rem;
		padding: 0.55rem 0;
		border-bottom: 1px solid rgba(0, 0, 0, 0.08);
		min-width: 0;
		max-width: 100%;
	}

	.file-title {
		font-family: 'GT Super Bold', serif;
		font-size: 0.95rem;
		color: #1e2f1e;
		max-width: 100%;
		overflow-wrap: anywhere;
		word-break: break-word;
	}

	.file-download-link {
		text-decoration: underline;
		text-underline-offset: 0.12em;
	}

	.file-type {
		font-family: 'GT Super Regular', serif;
		font-size: 0.88rem;
		color: #666;
		max-width: 100%;
	}

	.mobile-download-note {
		margin: 0 0 0.65rem;
		font-family: 'GT Super Regular', serif;
		font-size: 0.92rem;
		color: #555;
	}

	.detail-actions {
		margin-top: 0.5rem;
		padding-top: 0.85rem;
		/* border-top: 1px solid rgba(0, 0, 0, 0.1); */
	}

	.manage-link {
		display: inline-flex;
		align-items: center;
		font-family: 'GT Super Bold', serif;
		font-size: 0.95rem;
		text-decoration: none;
	}

	.detail-note {
		margin: 0;
		font-family: 'GT Super Regular', serif;
		font-size: 0.92rem;
		color: #555;
	}

	.data-table th,
	.data-table td {
		padding: 0.75rem 0.85rem;
		text-align: left;
		border-bottom: 1px solid rgba(0, 0, 0, 0.12);
		font-family: 'GT Super Regular', serif;
		vertical-align: top;
		overflow-wrap: anywhere;
		word-break: break-word;
	}

	.data-table th {
		background: #f4f4f4;
	}

	.sort-button {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0;
		border: none;
		background: transparent;
		font-family: 'GT Super Bold', serif;
		font-size: inherit;
		color: inherit;
		cursor: pointer;
	}

	.sort-button:hover,
	.sort-button:focus-visible {
		color: var(--sugar-pine);
	}

	.sort-indicator {
		font-size: 0.85rem;
		line-height: 1;
	}

	.dataset-title {
		font-family: 'GT Super Bold', serif;
	}

	.empty-row {
		text-align: center;
		color: #666;
	}

	@media (max-width: 900px) {
		.filters-row {
			grid-template-columns: 1fr 1fr;
		}

		.filter-search {
			grid-column: 1 / -1;
		}

		.detail-metadata {
			grid-template-columns: 1fr 1fr;
		}
	}

	@media (max-width: 560px) {
		.filters-row {
			grid-template-columns: 1fr;
		}

		.filters-meta {
			flex-direction: column;
			align-items: flex-start;
		}

		.detail-metadata {
			grid-template-columns: 1fr;
		}

		.detail-panel {
			padding-left: 1.1rem;
		}
	}

	@media (max-width: 720px) {
		.data-table {
			min-width: 36rem;
		}
	}
</style>
