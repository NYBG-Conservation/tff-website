<script lang="ts">
	import type { PublicDatasetRecord, PublicPublicationRecord, PublicResearchProject } from '$lib/api/public';
	import { djangoAdminHomeUrl } from '$lib/api/djangoAdmin';
	import { FIGSHARE_DOI_GUIDE_URL } from '$lib/constants/figshare';
	import AccordianList from '$lib/components/AccordianList.svelte';
	import ResearchProjectCard from '$lib/components/ResearchProjectCard.svelte';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	export let data;

	$: researchProjects = data.researchProjects as PublicResearchProject[];
	$: publicDatasets = data.publicDatasets as PublicDatasetRecord[];
	$: featuredPublications = data.featuredPublications as PublicPublicationRecord[];
	$: publicPublications = data.publicPublications as PublicPublicationRecord[];
	$: apiError = data.apiError as string | null;

	let activeProjectSlug: string | null = null;
	$: activeProject = researchProjects.find((project) => project.slug === activeProjectSlug) ?? null;
	$: relatedDatasets = activeProject ? getRelatedDatasets(activeProject) : [];
	$: relatedPublications = activeProject ? getRelatedPublications(activeProject) : [];

	let searchQuery = '';
	let filterStatus: 'all' | 'ongoing' | 'concluded' = 'all';
	let filterOrganization = 'all';
	let sortBy: 'curated' | 'title-asc' | 'title-desc' = 'curated';

	$: organizations = [
		...new Set(researchProjects.map((project) => project.organization_name).filter((name): name is string => Boolean(name)))
	].sort((a, b) => a.localeCompare(b));

	$: filteredProjects = researchProjects.filter((project) => {
		if (filterStatus === 'ongoing' && !project.ongoing) return false;
		if (filterStatus === 'concluded' && project.ongoing) return false;
		if (filterOrganization !== 'all' && project.organization_name !== filterOrganization) return false;
		const query = searchQuery.trim().toLowerCase();
		if (!query) return true;
		return [
			project.title,
			project.full_title ?? '',
			project.summary ?? '',
			project.lead_name ?? '',
			project.organization_name ?? '',
			...(project.institutional_partners ?? [])
		]
			.join(' ')
			.toLowerCase()
			.includes(query);
	});

	$: visibleProjects = [...filteredProjects].sort((a, b) => {
		if (sortBy === 'title-asc') return a.title.localeCompare(b.title);
		if (sortBy === 'title-desc') return b.title.localeCompare(a.title);
		return (a.public_sort_order ?? 0) - (b.public_sort_order ?? 0) || a.title.localeCompare(b.title);
	});

	$: hasActiveFilters =
		searchQuery.trim() !== '' || filterStatus !== 'all' || filterOrganization !== 'all' || sortBy !== 'curated';

	function clearFilters() {
		searchQuery = '';
		filterStatus = 'all';
		filterOrganization = 'all';
		sortBy = 'curated';
	}

	function openProject(projectSlug: string) {
		activeProjectSlug = projectSlug;
	}

	function applyProjectFromUrl() {
		const slug = $page.url.searchParams.get('project');
		if (!slug) return;
		if (researchProjects.some((project) => project.slug === slug)) {
			openProject(slug);
		}
	}

	onMount(() => {
		applyProjectFromUrl();
	});

	function closeProjectModal() {
		activeProjectSlug = null;
	}

	function handleEscapeKey(event: KeyboardEvent) {
		if (event.key === 'Escape' && activeProjectSlug) {
			closeProjectModal();
		}
	}

	function closeOnOverlayInteraction(event: MouseEvent | KeyboardEvent) {
		if ('target' in event && event.target === event.currentTarget) {
			closeProjectModal();
		}
	}

	function getRelatedDatasets(project: PublicResearchProject) {
		const linkedIds = new Set(project.datasetIds ?? []);
		return publicDatasets.filter(
			(record) => linkedIds.has(String(record.id)) || record.project_slug === project.slug
		);
	}

	function getRelatedPublications(project: PublicResearchProject) {
		return publicPublications.filter((record) => record.project_slug === project.slug);
	}

	const visitingResearchResources = [
		{
			label: 'On-site Research Agreement Form and Release',
			href: 'https://www.nybg.org/content/uploads/2023/03/NYBG-On-site-Research-Release-Form-1.pdf'
		},
		{
			label: 'Plant Material Collections Agreement Form and Release',
			href: 'https://www.nybg.org/content/uploads/2023/03/Plant-Material-Distribution-Agreement-1-1.pdf'
		},
		{
			label: 'Thain Family Forest Program 2008–2025',
			href: 'https://www.nybg.org/content/uploads/2017/04/Forest-Plan-2016.pdf'
		},
		{
			label: 'NYBG Plant Tracker',
			href: 'https://www.nybg.org/gardens/planttracker/'
		},
		{
			label: 'NYBG Gardens & Collections',
			href: 'https://www.nybg.org/gardens/gardens-collections/'
		}
	];

	const additionalResourcesHtml = `<ul class="resource-list">${visitingResearchResources
		.map(
			(resource) =>
				`<li><a href="${resource.href}" target="_blank" rel="noopener noreferrer">${resource.label}</a></li>`
		)
		.join('')}</ul>`;
</script>

<svelte:window on:keydown={handleEscapeKey} />

<section class="research-content">
	<section class="page-section" aria-labelledby="research-overview-heading">
		<!-- <h2 id="research-overview-heading" class="section-heading">Research in the Thain Family Forest</h2> -->
		<div class="section-body">
			<p class="body-paragraph">
				The Thain Family Forest is a living laboratory—the largest uncut expanse of New York City's
				original wooded landscape. For thousands of years this old-growth forest has changed, adapted,
				and survived. Today it supports long-term studies of urban ecology, forest health, biodiversity,
				and the outcomes of restoration work across NYBG's 50-acre woodland.
			</p>
			<p class="body-paragraph">
				Research in the Forest helps us understand how cities shape natural systems, track how the
				woodland responds to disturbance and management, and share what we learn with students,
				visitors, and the broader scientific community. Explore active and past projects below, along
				with selected publications from decades of work in the Forest. To learn how to conduct research in the Forest, please see the <a href="#conducting-research-heading">Visiting Research</a> section.
			</p>
		</div>
	</section>

	<section class="page-section" aria-labelledby="project-directory-heading">
		<div class="research-main-column">
	<h2 id="project-directory-heading" class="section-heading">Project Directory</h2>

	{#if apiError}
		<p class="api-error">Research project data is temporarily unavailable. ({apiError})</p>
	{/if}

	<div class="filters-panel">
		<div class="filters-row">
			<label class="filter-field">
				<span class="filter-label">Search</span>
				<input
					type="search"
					placeholder="Search projects…"
					bind:value={searchQuery}
					aria-label="Search projects"
				/>
			</label>
			<label class="filter-field">
				<span class="filter-label">Status</span>
				<select bind:value={filterStatus} aria-label="Filter by status">
					<option value="all">All statuses</option>
					<option value="ongoing">Ongoing</option>
					<option value="concluded">Concluded</option>
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
				<span class="filter-label">Sort</span>
				<select bind:value={sortBy} aria-label="Sort projects">
					<option value="curated">Curated order</option>
					<option value="title-asc">Title A–Z</option>
					<option value="title-desc">Title Z–A</option>
				</select>
			</label>
		</div>
		<div class="filters-meta">
			<p class="results-count">
				{visibleProjects.length}
				{visibleProjects.length === 1 ? 'project' : 'projects'}
			</p>
			{#if hasActiveFilters}
				<button type="button" class="clear-filters" on:click={clearFilters}>Clear filters</button>
			{/if}
		</div>
	</div>

	<div class="project-grid">
		{#if visibleProjects.length === 0}
			<p class="empty-directory">No projects match the current filters.</p>
		{:else}
			{#each visibleProjects as project}
				<ResearchProjectCard
					title={project.title}
					summary={project.summary || project.full_title || ''}
					ongoing={project.ongoing}
					leadName={project.lead_name}
					onSelect={() => openProject(project.slug)}
				/>
			{/each}
		{/if}
	</div>

	{#if activeProject}
		<div
			class="modal-overlay"
			role="button"
			tabindex="0"
			aria-label="Close details modal"
			on:click={closeOnOverlayInteraction}
			on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && closeOnOverlayInteraction(event)}
		>
			<div
				id={`project-details-${activeProject.slug}`}
				class="detail-modal"
				role="dialog"
				aria-modal="true"
				aria-labelledby="project-modal-title"
			>
				<div class="modal-header">
					<h3 id="project-modal-title">{activeProject.title}</h3>
					<button type="button" class="modal-close" aria-label="Close project details" on:click={closeProjectModal}>
						×
					</button>
				</div>
				<div class="modal-body">
					<dl class="project-metadata">
						<div class="metadata-item">
							<dt>Status</dt>
							<dd>
								<span
									class="status-tag"
									class:ongoing={activeProject.ongoing}
									class:concluded={!activeProject.ongoing}
								>
									{activeProject.ongoing ? 'Ongoing' : 'Concluded'}
								</span>
							</dd>
						</div>
						{#if activeProject.organization_name}
							<div class="metadata-item">
								<dt>Lead institution</dt>
								<dd>{activeProject.organization_name}</dd>
							</div>
						{/if}
						{#if activeProject.institutional_partners?.length}
							<div class="metadata-item">
								<dt>Partner institutions</dt>
								<dd>
									<ul class="metadata-list">
										{#each activeProject.institutional_partners as partner}
											<li>{partner}</li>
										{/each}
									</ul>
								</dd>
							</div>
						{/if}
						{#if activeProject.lead_name}
							<div class="metadata-item">
								<dt>Project lead</dt>
								<dd>
									{#if activeProject.lead_email}
										<a href={`mailto:${activeProject.lead_email}`}>{activeProject.lead_name}</a>
									{:else}
										{activeProject.lead_name}
									{/if}
								</dd>
							</div>
						{/if}
					</dl>

					{#if activeProject.descriptionParagraphs.length === 0}
						<p class="empty-related">Project details will be published soon.</p>
					{:else}
						{#each activeProject.descriptionParagraphs as paragraph}
							<p>{paragraph}</p>
						{/each}
					{/if}
					<div class="related-datasets">
						<h4>Project files</h4>
						{#if activeProject.project_files?.length}
							<ul>
								{#each activeProject.project_files as file}
									<li>
										<span class="file-kind">{file.file_kind}</span>
										{#if file.download_url}
											<a href={file.download_url} target="_blank" rel="noopener noreferrer"
												>{file.title}</a
											>
										{:else}
											{file.title}
										{/if}
									</li>
								{/each}
							</ul>
						{:else}
							<p class="empty-related">No public project files yet.</p>
						{/if}
					</div>
					<div class="related-datasets">
						<h4>Related datasets</h4>
						{#if relatedDatasets.length > 0}
							<ul>
								{#each relatedDatasets as dataset}
									<li>
										<a href={`/data?project=${activeProject.slug}`}>{dataset.title}</a>
									</li>
								{/each}
							</ul>
						{:else}
							<p class="empty-related">No linked datasets yet.</p>
						{/if}
					</div>
					<div class="related-publications">
						<h4>Related publications</h4>
						{#if relatedPublications.length > 0}
							<ul>
								{#each relatedPublications as publication}
									<li>
										{#if publication.url}
											<a href={publication.url} target="_blank" rel="noopener noreferrer">
												{@html publication.citation}
											</a>
										{:else}
											<span>{@html publication.citation}</span>
										{/if}
									</li>
								{/each}
							</ul>
						{:else}
							<p class="empty-related">No linked publications yet.</p>
						{/if}
					</div>
				</div>
			</div>
		</div>
	{/if}
<br/><br/>

	<section class="page-section" aria-labelledby="conducting-research-heading">
		<h2 id="conducting-research-heading" class="section-heading">Conducting Research</h2>
		<div class="section-body">
			<p class="body-paragraph">
				Research in the Thain Family Forest is carried out by NYBG staff, graduate students,
				undergraduate interns, volunteers, and visiting scientists. Projects range from long-term
				ecological monitoring to focused studies on plants, soils, wildlife, and Bronx River health.
			</p>
			<p class="body-paragraph">
				Visiting researchers and students are welcome to propose on-site work in the Forest and across
				NYBG's living collections. Use the resources below to apply, review required agreements, and
				learn more about the Garden's collections.
			</p>

			<p class="body-paragraph">
				When you are ready to share data, you may reserve a DOI via Figshare (or another repository)
				and link the deposit from your project record. Upload data to the deposit as it becomes
				available, then attach files or the deposit URL under project files.
				<a href={FIGSHARE_DOI_GUIDE_URL} target="_blank" rel="noopener noreferrer">
					How to reserve a DOI in Figshare
				</a>.
			</p>

			<p class="staff-login-note">
				NYBG staff and approved researchers can manage projects and datasets in
				<a href={djangoAdminHomeUrl()}>Django admin</a>.
			</p>

			<div class="application-callout">
				<h3 class="subsection-heading">NYBG Living Collections Research Application</h3>
				<p class="body-paragraph">
					At NYBG, we encourage the use of our living collections for scientific research and
					educational purposes. If you are interested in conducting on-site research or requesting
					plant material for educational or research purposes, please complete the application below.
					Please note, applications must be submitted two weeks prior to the anticipated start date of
					the project. If your application is accepted, you will be asked to complete an agreement form.
				</p>
				<a class="apply-button" href="/research/apply">
					Apply for on-site research
				</a>

			<div class="resources-accordion">
				<AccordianList
					theme="light"
					type="files"
					items={['Additional resources']}
					text={[additionalResourcesHtml]}
				/>
			</div>
			</div>



		</div>
	</section>
<br><br/>
	<section class="publications">
		<h2 class="section-heading">Publication Archive</h2>
		{#if featuredPublications.length === 0}
			<p class="empty-related">Publications will be published here soon.</p>
		{:else}
			<ul>
				{#each featuredPublications as publication}
					<li>
						{#if publication.url}
							<a href={publication.url} target="_blank" rel="noopener noreferrer">
								{@html publication.citation}
							</a>
						{:else}
							{@html publication.citation}
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	</section>
	</div>
	</section>
</section>

<style>
	.research-content {
		max-width: 1400px;
		margin: 2rem auto;
		padding: 0 1rem 3rem;
	}

	.api-error {
		font-family: 'GT Super Regular', serif;
		color: #7a1e1e;
		margin: 0 0 1rem;
	}

	.research-main-column {
		max-width: 1100px;
		margin-left: auto;
		margin-right: auto;
		width: 100%;
	}

	.page-section {
		max-width: 1100px;
		margin: 0 auto 2.5rem;
	}

	.body-paragraph {
		font-family: 'GT Super Regular', serif;
		font-size: 1.05rem;
		line-height: 1.6;
		margin: 0 0 1rem;
		color: #222;
	}

	.subsection-heading {
		font-family: 'GT Super Bold', serif;
		font-size: 1.05rem;
		margin: 1.5rem 0 0.65rem;
		color: #1e2f1e;
	}

	.application-callout {
		margin: 1.5rem 0;
		padding: 1.25rem 1.35rem;
		border: 1px solid rgba(0, 0, 0, 0.12);
		background: rgba(200, 181, 0, 0.08);
	}

	.application-callout .body-paragraph:last-of-type {
		margin-bottom: 1.1rem;
	}

	.application-callout .subsection-heading {
		margin-top: 0;
	}

	.apply-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.7rem 1.25rem;
		border: 1px solid #1e2f1e;
		background: #1e2f1e;
		color: #fff;
		font-family: 'GT Super Bold', serif;
		font-size: 0.95rem;
		text-decoration: none;
		cursor: pointer;
	}

	.apply-button:hover,
	.apply-button:focus-visible {
		background: #fff;
		color: #1e2f1e;
	}

	.resources-accordion {
		margin-top: 1.5rem;
	}

	.staff-login-note {
		margin: 1.5rem 0 0;
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		color: #555;
	}

	.section-heading {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.35rem, 2.2vw, 2rem);
		text-transform: uppercase;
		line-height: 1.1;
		margin: 0 0 1rem;
		color: #1e2f1e;
	}

	.page-section .section-heading {
		margin-top: 0;
	}

	#project-directory-heading {
		margin-top: 0;
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

	.project-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1.5rem;
	}

	.empty-directory {
		grid-column: 1 / -1;
		margin: 0;
		font-family: 'GT Super Regular', serif;
		color: #555;
	}

	.filters-panel {
		margin-bottom: 1rem;
		padding: 1rem;
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.12);
	}

	.filters-row {
		display: grid;
		grid-template-columns: minmax(180px, 1.6fr) repeat(3, minmax(130px, 1fr));
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

	.project-metadata {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.85rem 1.25rem;
		margin: 0 0 1.25rem;
		padding: 0 0 1.1rem;
		border-bottom: 1px solid rgba(0, 0, 0, 0.1);
	}

	.metadata-item {
		margin: 0;
	}

	.project-metadata dt {
		font-family: 'GT Super Bold', serif;
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #5a5a5a;
		margin: 0 0 0.2rem;
	}

	.project-metadata dd {
		margin: 0;
		font-family: 'GT Super Regular', serif;
		font-size: 0.98rem;
		color: #222;
	}

	.metadata-list {
		margin: 0;
		padding-left: 1.1rem;
	}

	.metadata-list li {
		margin-bottom: 0.2rem;
	}

	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
		z-index: 1200;
	}

	.detail-modal {
		width: min(920px, 95vw);
		max-height: 88vh;
		overflow-y: auto;
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.15);
		box-shadow: 0 16px 38px rgba(0, 0, 0, 0.25);
		animation: modal-slide-up 240ms cubic-bezier(0.22, 1, 0.36, 1);
	}

	@keyframes modal-slide-up {
		from {
			opacity: 0;
			transform: translateY(18px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.modal-header {
		position: sticky;
		top: 0;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.95rem 1rem 0.75rem;
		background: #fff;
		border-bottom: 1px solid rgba(0, 0, 0, 0.12);
	}

	.modal-header h3 {
		font-family: 'GT Super Bold', serif;
		font-size: 1.25rem;
		margin: 0;
		color: #111;
	}

	.modal-close {
		border: none;
		background: transparent;
		font-size: 1.8rem;
		line-height: 1;
		cursor: pointer;
		padding: 0 0.2rem;
		color: #111;
	}

	.modal-body {
		padding: 1rem;
	}

	.modal-body p {
		font-family: 'GT Super Regular', serif;
		font-size: 1.02rem;
		line-height: 1.6;
		margin: 0 0 0.8rem;
		color: #222;
	}

	.related-datasets h4 {
		font-family: 'GT Super Bold', serif;
		font-size: 1rem;
		margin: 1rem 0 0.4rem;
	}

	.related-datasets ul {
		margin: 0;
		padding-left: 1.25rem;
	}

	.related-datasets .file-kind {
		display: inline-block;
		margin-right: 0.45rem;
		font-family: 'Martian Mono', serif;
		font-size: 0.68rem;
		letter-spacing: 0.02em;
		text-transform: uppercase;
		color: #5a5a5a;
	}

	.related-publications {
		margin-top: 1.25rem;
	}

	.related-publications ul {
		margin: 0;
		padding-left: 1.25rem;
	}

	.related-publications li {
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		line-height: 1.5;
		margin-bottom: 0.6rem;
	}

	.empty-related {
		margin-bottom: 0;
		color: #555;
	}

	.publications ul {
		margin: 0;
		padding-left: 1.25rem;
	}

	.publications li {
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		line-height: 1.55;
		margin-bottom: 0.75rem;
		color: #222;
	}

	@media (max-width: 900px) {
		.project-grid {
			grid-template-columns: 1fr;
		}

		.filters-row {
			grid-template-columns: 1fr;
		}

		.project-metadata {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 640px) {
		.modal-overlay {
			padding: 0.5rem;
			align-items: flex-start;
			padding-top: max(0.5rem, env(safe-area-inset-top));
			padding-bottom: max(0.5rem, env(safe-area-inset-bottom));
		}

		.detail-modal {
			width: 100%;
			max-height: calc(100vh - 1rem);
			max-height: calc(100dvh - 1rem);
			max-height: calc(100svh - 1rem);
		}

		.modal-header h3 {
			font-size: 1.05rem;
			padding-right: 0.5rem;
		}
	}
</style>