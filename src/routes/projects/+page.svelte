<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { createDataset, listDatasets, type Dataset, type DatasetInput } from '$lib/api/datasets';
	import {
		addProjectManager,
		createProject,
		listProjects,
		removeProjectManager,
		updateProject,
		type Project,
		type ProjectInput
	} from '$lib/api/projects';
	import {
		createProjectPublication,
		deleteProjectPublication,
		listProjectPublications,
		type ProjectPublication,
		type ProjectPublicationInput
	} from '$lib/api/projectPublications';
	import { getCurrentUser, type CurrentUser } from '$lib/api/accounts';
	import { FIGSHARE_DOI_GUIDE_URL } from '$lib/constants/figshare';
	import { createOrganization, listOrganizations, type Organization } from '$lib/api/organizations';

	let loading = true;
	let savingProject = false;
	let addingDataset = false;
	let addingPublication = false;
	let projects: Project[] = [];
	let organizations: Organization[] = [];
	let datasets: Dataset[] = [];
	let projectPublications: ProjectPublication[] = [];
	let selectedProjectId: number | null = null;
	let managerUsername = '';
	let message = '';
	let error = '';
	let currentUser: CurrentUser | null = null;
	let dataUploadChoice: 'upload_now' | 'upload_later' = 'upload_later';
	let creatingOrganization = false;
	let newOrganizationName = '';
	let newOrganizationContactEmail = '';

	let publicationForm: ProjectPublicationInput = {
		citation: '',
		title: '',
		publication_year: undefined,
		doi: '',
		url: '',
		featured: false,
		expose_on_public_api: false,
		sort_order: 0
	};

	let projectForm: ProjectInput = {
		short_title: '',
		summary: '',
		description: '',
		full_title: '',
		lead_name: '',
		lead_email: '',
		shared_publicly: false,
		start_date: '',
		end_date: '',
		ongoing: false,
		external_url: '',
		plans_own_doi: false,
		figshare_doi_url: '',
		institutional_partners: [],
		collection_frequency: '',
		update_frequency: '',
		last_updated_note: '',
		organization: 0
	};

	let datasetForm: DatasetInput = {
		title: '',
		description: '',
		cadence: 'annual',
		status: 'draft',
		data_type: 'tabular',
		project_id: '',
		project: undefined,
		expose_on_public_api: false,
		organization: 0,
		owner: 0,
		additional_research_partners: [],
		paper_links: [],
		metadata_schema_version: 1,
		metadata_fields: [],
		publications: []
	};

	$: selectedProject = projects.find((project) => project.id === selectedProjectId) ?? null;
	$: canEditSelected = !selectedProject || selectedProject.can_edit !== false;
	$: visibleDatasets = selectedProject
		? datasets.filter((dataset: { project?: number }) => dataset.project === selectedProject.id)
		: [];

	async function loadData() {
		loading = true;
		error = '';
		try {
			const [userResult, projectsResult, orgResult, datasetResult] = await Promise.all([
				getCurrentUser(),
				listProjects(),
				listOrganizations(),
				listDatasets()
			]);
			currentUser = userResult;
			projects = projectsResult;
			organizations = orgResult;
			datasets = datasetResult;
			if (organizations.length > 0 && !projectForm.organization) {
				projectForm.organization = organizations[0].id;
				datasetForm.organization = organizations[0].id;
			}
			applyProjectFromUrl();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load project dashboard data.';
		} finally {
			loading = false;
		}
	}

	function selectProject(project: Project) {
		selectedProjectId = project.id;
		projectForm = {
			...project,
			institutional_partners: project.institutional_partners ?? []
		};
		datasetForm = {
			...datasetForm,
			project: project.id,
			project_id: project.slug,
			organization: project.organization
		};
		void loadProjectPublications(project.id);
		message = '';
		error = '';
	}

	function applyProjectFromUrl() {
		const param = $page.url.searchParams.get('project');
		if (!param || projects.length === 0) return;

		const match =
			projects.find((project) => project.slug === param) ??
			projects.find((project) => String(project.id) === param);

		if (match && selectedProjectId !== match.id) {
			selectProject(match);
		}
	}

	async function loadProjectPublications(projectId: number) {
		try {
			projectPublications = await listProjectPublications(projectId);
		} catch (err) {
			projectPublications = [];
			error = err instanceof Error ? err.message : 'Failed to load project publications.';
		}
	}

	function resetProjectForm() {
		selectedProjectId = null;
		projectPublications = [];
		dataUploadChoice = 'upload_later';
		projectForm = {
			short_title: '',
			summary: '',
			description: '',
			full_title: '',
			lead_name: '',
			lead_email: '',
			shared_publicly: false,
			start_date: '',
			end_date: '',
			ongoing: false,
			external_url: '',
			plans_own_doi: false,
			figshare_doi_url: '',
			institutional_partners: [],
			collection_frequency: '',
			update_frequency: '',
			last_updated_note: '',
			organization: organizations[0]?.id ?? 0
		};
	}

	async function saveProject() {
		savingProject = true;
		message = '';
		error = '';
		try {
			const payload: ProjectInput = {
				...projectForm,
				institutional_partners: projectForm.institutional_partners ?? []
			};
			if (selectedProject) {
				await updateProject(selectedProject.id, payload);
				message = 'Project updated.';
			} else {
				const createdProject = await createProject(payload);
				if (dataUploadChoice === 'upload_now' && datasetForm.title.trim()) {
					await createDataset({
						...datasetForm,
						project: createdProject.id,
						project_id: createdProject.slug,
						organization: createdProject.organization,
						owner: currentUser?.id ?? 0
					});
					message = 'Project and initial dataset created.';
				} else {
					message = 'Project created.';
				}
				resetProjectForm();
			}
			await loadData();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to save project.';
		} finally {
			savingProject = false;
		}
	}

	let partnerSelectId = 0;

	function addInstitutionalPartner() {
		if (!partnerSelectId) return;
		const current = projectForm.institutional_partners ?? [];
		if (!current.includes(partnerSelectId)) {
			projectForm.institutional_partners = [...current, partnerSelectId];
		}
		partnerSelectId = 0;
	}

	function removeInstitutionalPartner(orgId: number) {
		projectForm.institutional_partners = (projectForm.institutional_partners ?? []).filter(
			(id) => id !== orgId
		);
	}

	function partnerName(orgId: number): string {
		return organizations.find((org) => org.id === orgId)?.name ?? `Organization #${orgId}`;
	}

	async function handleAddManager() {
		if (!selectedProject || !managerUsername.trim()) return;
		error = '';
		message = '';
		try {
			await addProjectManager(selectedProject.id, managerUsername.trim());
			managerUsername = '';
			message = 'Team member added.';
			await loadData();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to add team member.';
		}
	}

	async function handleRemoveManager(userId: number) {
		if (!selectedProject) return;
		error = '';
		message = '';
		try {
			await removeProjectManager(selectedProject.id, userId);
			message = 'Team member removed.';
			await loadData();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to remove team member.';
		}
	}

	async function addDatasetToProject() {
		if (!selectedProject) return;
		addingDataset = true;
		error = '';
		message = '';
		try {
			await createDataset({
				...datasetForm,
				project: selectedProject.id,
				project_id: selectedProject.slug,
				organization: selectedProject.organization,
				owner: currentUser?.id ?? selectedProject.owner
			});
			message = 'Dataset added to project.';
			datasetForm = { ...datasetForm, title: '', description: '' };
			await loadData();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to create dataset.';
		} finally {
			addingDataset = false;
		}
	}

	async function addPublicationToProject() {
		if (!selectedProject) return;
		addingPublication = true;
		error = '';
		message = '';
		try {
			await createProjectPublication(selectedProject.id, {
				...publicationForm,
				publication_year: publicationForm.publication_year || undefined
			});
			message = 'Publication added to project.';
			publicationForm = {
				citation: '',
				title: '',
				publication_year: undefined,
				doi: '',
				url: '',
				featured: false,
				expose_on_public_api: false,
				sort_order: 0
			};
			await loadProjectPublications(selectedProject.id);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to add publication.';
		} finally {
			addingPublication = false;
		}
	}

	async function handleDeletePublication(publicationId: number) {
		if (!selectedProject) return;
		error = '';
		message = '';
		try {
			await deleteProjectPublication(selectedProject.id, publicationId);
			message = 'Publication removed.';
			await loadProjectPublications(selectedProject.id);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to remove publication.';
		}
	}

	async function addOrganizationOption() {
		if (!newOrganizationName.trim()) return;
		creatingOrganization = true;
		error = '';
		try {
			const created = await createOrganization({
				name: newOrganizationName.trim(),
				contact_email: newOrganizationContactEmail.trim() || undefined
			});
			organizations = [...organizations, created].sort((a, b) => a.name.localeCompare(b.name));
			projectForm.organization = created.id;
			newOrganizationName = '';
			newOrganizationContactEmail = '';
			message = 'Organization added.';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to create organization.';
		} finally {
			creatingOrganization = false;
		}
	}

	onMount(loadData);
</script>

<section class="projects-page">
	<h1>Project Workflow Dashboard</h1>
	<p class="subtitle">
		Create and manage projects, add team members, and attach datasets under each project.
	</p>

	{#if loading}
		<p>Loading project workspace...</p>
	{:else}
		{#if error}<p class="error">{error}</p>{/if}
		{#if message}<p class="message">{message}</p>{/if}

		<div class="grid">
			<div class="panel">
				<div class="panel-header">
					<h2>Projects</h2>
					<button type="button" on:click={resetProjectForm}>New project</button>
				</div>
				<ul class="project-list">
					{#each projects as project}
						<li>
							<button
								type="button"
								class:selected={selectedProjectId === project.id}
								on:click={() => selectProject(project)}
							>
								<strong>{project.short_title}</strong>
								<span class="project-meta">
									{project.lead_name}{#if project.organization_name} · {project.organization_name}{/if}
								</span>
							</button>
						</li>
					{/each}
				</ul>
			</div>

			<div class="panel">
				<h2>{selectedProject ? (canEditSelected ? 'Edit Project' : 'View Project') : 'Create Project'}</h2>
				{#if selectedProject && !canEditSelected}
					<p class="hint">
						You can view this organization project, but only owners and team members can edit it or
						manage its datasets.
					</p>
				{/if}
				<fieldset class="project-fields" disabled={selectedProject && !canEditSelected}>
				<div class="form-grid">
					<label>Short title<input bind:value={projectForm.short_title} /></label>
					{#if selectedProject?.slug}
						<p class="slug-note">Public URL slug: <code>{selectedProject.slug}</code> (set from title when created)</p>
					{:else}
						<p class="slug-note">Slug is generated automatically from the short title when you save.</p>
					{/if}
					<label>Summary<textarea rows="2" bind:value={projectForm.summary} /></label>
					<label>Description<textarea rows="4" bind:value={projectForm.description} placeholder="Separate paragraphs with a blank line" /></label>
					<label>Full title<input bind:value={projectForm.full_title} /></label>

					<h3 class="form-section-heading">Project lead</h3>
					<label>Lead name<input bind:value={projectForm.lead_name} required /></label>
					<label>Lead email<input type="email" bind:value={projectForm.lead_email} required /></label>
					<label>
						Organization
						<select bind:value={projectForm.organization} required>
							<option value={0} disabled>Select organization</option>
							{#each organizations as org}
								<option value={org.id}>{org.name}</option>
							{/each}
						</select>
					</label>

					<label>Start date<input type="date" bind:value={projectForm.start_date} /></label>
					<label>End date<input type="date" bind:value={projectForm.end_date} /></label>
					<label>External URL<input type="url" bind:value={projectForm.external_url} /></label>
					<label class="checkbox">
						<input type="checkbox" bind:checked={projectForm.plans_own_doi} />
						I plan to publish this data with my own DOI
					</label>
					<p class="field-note">
						Check this to create the project without a Figshare reservation (e.g. journal, Dryad, Zenodo DOI).
						You can still paste a doi.org or Figshare URL below when you have it.
					</p>
					<label>
						Figshare item URL or reserved DOI
						<input
							type="url"
							bind:value={projectForm.figshare_doi_url}
							placeholder="https://figshare.com/articles/..."
							required={!selectedProject && !projectForm.plans_own_doi}
						/>
					</label>
					<p class="field-note">
						{#if projectForm.plans_own_doi}
							Optional while using your own DOI. Prefer a doi.org link when available.
						{:else}
							Required for new projects unless you opt out above. Reserve a DOI first —
							<a href={FIGSHARE_DOI_GUIDE_URL} target="_blank" rel="noopener noreferrer">
								How to reserve a DOI in Figshare
							</a>.
						{/if}
					</p>
					<label>Collection frequency<input bind:value={projectForm.collection_frequency} /></label>
					<label>Update frequency<input bind:value={projectForm.update_frequency} /></label>
					<label class="checkbox">
						<input type="checkbox" bind:checked={projectForm.shared_publicly} />
						Shared publicly
					</label>
					<p class="field-note">
						If enabled, this project can be shown on the public Thain Family Forest website.
					</p>
					<label class="checkbox">
						<input type="checkbox" bind:checked={projectForm.ongoing} />
						Ongoing
					</label>
				</div>
				<div class="organization-creator">
					<label>
						Add new organization
						<input placeholder="Organization name" bind:value={newOrganizationName} />
					</label>
					<label>
						Organization contact email (optional)
						<input type="email" placeholder="contact@example.org" bind:value={newOrganizationContactEmail} />
					</label>
					<button
						type="button"
						on:click={addOrganizationOption}
						disabled={creatingOrganization || !newOrganizationName.trim()}
					>
						{creatingOrganization ? 'Adding...' : 'Add organization'}
					</button>
				</div>
				<label class="full-width">
					Institutional partners
					<select bind:value={partnerSelectId}>
						<option value={0}>Select an organization to add…</option>
						{#each organizations as org}
							<option value={org.id} disabled={(projectForm.institutional_partners ?? []).includes(org.id)}>
								{org.name}
							</option>
						{/each}
					</select>
				</label>
				<div class="partner-actions">
					<button
						type="button"
						on:click={addInstitutionalPartner}
						disabled={!partnerSelectId || !canEditSelected}
					>
						Add partner
					</button>
				</div>
				<ul class="partner-list">
					{#each projectForm.institutional_partners ?? [] as orgId}
						<li>
							<span>{partnerName(orgId)}</span>
							{#if canEditSelected}
								<button type="button" on:click={() => removeInstitutionalPartner(orgId)}>Remove</button>
							{/if}
						</li>
					{/each}
				</ul>
				<p class="field-note">
					Partners come from Organizations. Use “Add new organization” above if yours is missing, then add it
					here.
				</p>
				<label class="full-width">
					Last updated note
					<textarea rows="2" bind:value={projectForm.last_updated_note}></textarea>
				</label>
				{#if !selectedProject}
					<div class="initial-dataset">
						<div class="upload-choice">
							<label>
								<input
									type="radio"
									name="data-upload-choice"
									value="upload_now"
									checked={dataUploadChoice === 'upload_now'}
									on:change={() => (dataUploadChoice = 'upload_now')}
								/>
								I'd like to upload associated data
							</label>
							<label>
								<input
									type="radio"
									name="data-upload-choice"
									value="upload_later"
									checked={dataUploadChoice === 'upload_later'}
									on:change={() => (dataUploadChoice = 'upload_later')}
								/>
								I'll upload data later
							</label>
						</div>
						{#if dataUploadChoice === 'upload_now'}
							<div class="dataset-form">
								<input placeholder="Initial dataset title" bind:value={datasetForm.title} />
								<textarea
									rows="2"
									placeholder="Initial dataset description"
									bind:value={datasetForm.description}
								></textarea>
								<div class="inline">
									<select bind:value={datasetForm.cadence}>
										<option value="annual">Annual</option>
										<option value="one_off">One-off</option>
										<option value="continuous">Continuous</option>
									</select>
									<select bind:value={datasetForm.status}>
										<option value="draft">Draft</option>
										<option value="active">Active</option>
										<option value="archived">Archived</option>
									</select>
								</div>
								<label class="checkbox">
									<input type="checkbox" bind:checked={datasetForm.expose_on_public_api} />
									Expose this dataset via website API
								</label>
							</div>
						{/if}
					</div>
				{/if}
				<div class="actions">
					<button
						type="button"
						on:click={saveProject}
						disabled={!canEditSelected || savingProject || !projectForm.short_title || !projectForm.lead_name?.trim() || !projectForm.lead_email?.trim() || !projectForm.organization || (!selectedProject && !projectForm.plans_own_doi && !projectForm.figshare_doi_url?.trim())}
					>
						{savingProject ? 'Saving...' : selectedProject ? 'Save changes' : 'Create project'}
					</button>
				</div>
				</fieldset>
			</div>
		</div>

		{#if selectedProject && canEditSelected}
			<div class="grid lower">
				<div class="panel">
					<h2>Team members</h2>
					<p class="hint">
						Project owners and NYBG staff can add team members by username. Team members can view and
						edit this project and all of its datasets.
					</p>
					<div class="manager-input">
						<input placeholder="username" bind:value={managerUsername} />
						<button type="button" on:click={handleAddManager}>Add</button>
					</div>
					<ul class="manager-list">
						{#each selectedProject.managers ?? [] as manager}
							<li class="team-member-row">
								<span class="team-member-name">{manager.username}</span>
								<span class="team-member-meta">Added by {manager.added_by_username || '—'}</span>
							</li>
						{/each}
						{#if !(selectedProject.managers ?? []).length}
							<li class="team-member-row empty">No team members yet.</li>
						{/if}
					</ul>
				</div>

				<div class="panel">
					<h2>Datasets for {selectedProject.short_title}</h2>
					<p class="upload-governance">
						<strong>Data deposit:</strong> Upload associated files to your project's Figshare item
						(<a href={FIGSHARE_DOI_GUIDE_URL} target="_blank" rel="noopener noreferrer">reserve a DOI</a>).
						Link files here: up to 100 MB direct upload; 100 MB–1 GB prefer external links; above 1 GB use
						Figshare or another external URL. Publications may be uploaded or linked via DOI/URL.
					</p>
					<div class="dataset-form">
						<input placeholder="Dataset title" bind:value={datasetForm.title} />
						<textarea rows="2" placeholder="Dataset description" bind:value={datasetForm.description}></textarea>
						<div class="inline">
							<select bind:value={datasetForm.cadence}>
								<option value="annual">Annual</option>
								<option value="one_off">One-off</option>
								<option value="continuous">Continuous</option>
							</select>
							<select bind:value={datasetForm.status}>
								<option value="draft">Draft</option>
								<option value="active">Active</option>
								<option value="archived">Archived</option>
							</select>
						</div>
						<label class="checkbox">
							<input type="checkbox" bind:checked={datasetForm.expose_on_public_api} />
							Expose this dataset via website API
						</label>
						<button
							type="button"
							on:click={addDatasetToProject}
							disabled={addingDataset || !datasetForm.title}
						>
							{addingDataset ? 'Adding...' : 'Add dataset'}
						</button>
					</div>
					<ul class="dataset-list">
						{#if visibleDatasets.length === 0}
							<li>No datasets linked yet.</li>
						{:else}
							{#each visibleDatasets as dataset}
								<li>{dataset.title}</li>
							{/each}
						{/if}
					</ul>
				</div>
			</div>

			<div class="panel publications-panel">
				<h2>Publications for {selectedProject.short_title}</h2>
				<p class="hint">
					Add formatted citations for papers and reports linked to this project. Use basic HTML such as
					<code>&lt;em&gt;</code> for journal titles. Mark a publication as featured to include it in the
					site-wide Selected Publications list on <code>/research</code>.
				</p>
				<div class="publication-form">
					<textarea
						rows="3"
						placeholder="Full citation (HTML allowed for italics)"
						bind:value={publicationForm.citation}
					></textarea>
					<div class="inline">
						<input
							type="number"
							placeholder="Year"
							bind:value={publicationForm.publication_year}
						/>
						<input placeholder="DOI (optional)" bind:value={publicationForm.doi} />
					</div>
					<input placeholder="URL (optional)" bind:value={publicationForm.url} />
					<label class="checkbox">
						<input type="checkbox" bind:checked={publicationForm.expose_on_public_api} />
						Show on public website
					</label>
					<label class="checkbox">
						<input type="checkbox" bind:checked={publicationForm.featured} />
						Include in Selected Publications list
					</label>
					<button
						type="button"
						on:click={addPublicationToProject}
						disabled={addingPublication || !publicationForm.citation.trim()}
					>
						{addingPublication ? 'Adding...' : 'Add publication'}
					</button>
				</div>
				<ul class="publication-list">
					{#if projectPublications.length === 0}
						<li>No publications linked yet.</li>
					{:else}
						{#each projectPublications as publication}
							<li>
								<div class="publication-item">
									<p>{@html publication.citation}</p>
									<div class="publication-meta">
										{#if publication.publication_year}
											<span>{publication.publication_year}</span>
										{/if}
										{#if publication.featured}
											<span>Featured</span>
										{/if}
										{#if publication.expose_on_public_api}
											<span>Public</span>
										{/if}
									</div>
									<button type="button" on:click={() => handleDeletePublication(publication.id)}>
										Remove
									</button>
								</div>
							</li>
						{/each}
					{/if}
				</ul>
			</div>
		{/if}
	{/if}
</section>

<style>
	.projects-page {
		max-width: 1300px;
		margin: 2rem auto;
		padding: 0 1rem 2rem;
		font-family: 'GT Super Regular', serif;
		overflow-x: clip;
	}

	h1 {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.5rem, 2.5vw, 2.2rem);
		margin: 0 0 0.4rem;
	}

	.subtitle {
		margin-top: 0;
		color: #333;
	}

	.grid {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 2fr);
		gap: 1rem;
	}

	.lower {
		margin-top: 1rem;
		/* Stack team members + datasets so forms never blow past page width */
		grid-template-columns: minmax(0, 1fr);
	}

	.panel {
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.15);
		padding: 1rem;
		min-width: 0;
		overflow-x: clip;
	}

	.project-fields {
		border: 0;
		margin: 0;
		padding: 0;
		min-width: 0;
	}

	.project-fields:disabled {
		opacity: 0.85;
	}

	.panel-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.project-list,
	.manager-list,
	.dataset-list,
	.publication-list {
		list-style: none;
		padding: 0;
		margin: 0.7rem 0 0;
	}

	.publications-panel {
		margin-top: 1rem;
	}

	.publication-form {
		display: grid;
		gap: 0.6rem;
	}

	.publication-item {
		display: grid;
		gap: 0.35rem;
		padding: 0.6rem 0;
		border-bottom: 1px solid rgba(0, 0, 0, 0.08);
	}

	.publication-item p {
		margin: 0;
	}

	.publication-meta {
		display: flex;
		gap: 0.6rem;
		font-size: 0.8rem;
		color: #5a5a5a;
	}

	.project-list,
	.manager-list,
	.dataset-list {
		list-style: none;
		padding: 0;
		margin: 0.7rem 0 0;
	}

	.project-list button {
		width: 100%;
		text-align: left;
		padding: 0.6rem;
		border: 1px solid rgba(0, 0, 0, 0.15);
		background: #fff;
		margin-bottom: 0.5rem;
		display: flex;
		justify-content: space-between;
	}

	.project-list button.selected {
		background: rgba(200, 181, 0, 0.15);
	}

	.project-meta {
		display: block;
		font-size: 0.8rem;
		color: #5a5a5a;
	}

	.slug-note {
		grid-column: 1 / -1;
		margin: 0;
		font-size: 0.9rem;
		color: #555;
	}

	.slug-note code {
		font-size: 0.85rem;
	}

	.form-section-heading {
		grid-column: 1 / -1;
		margin: 1.25rem 0 0.25rem;
		font-family: 'GT Super Bold', serif;
		font-size: 1rem;
		color: #1e2f1e;
	}

	.form-grid {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 0.6rem;
	}

	label {
		display: grid;
		gap: 0.2rem;
		font-size: 0.92rem;
		min-width: 0;
	}

	.full-width {
		margin-top: 0.6rem;
	}

	input,
	textarea,
	select {
		padding: 0.45rem;
		font: inherit;
		border: 1px solid rgba(0, 0, 0, 0.2);
		width: 100%;
		max-width: 100%;
		min-width: 0;
		box-sizing: border-box;
	}

	.checkbox {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.checkbox input {
		width: auto;
	}

	.actions,
	.manager-input {
		margin-top: 0.75rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.manager-input input {
		flex: 1 1 12rem;
		min-width: 0;
	}

	.initial-dataset {
		margin-top: 0.9rem;
		padding-top: 0.8rem;
		border-top: 1px solid rgba(0, 0, 0, 0.08);
	}

	.upload-choice {
		display: grid;
		gap: 0.4rem;
	}

	.upload-choice label {
		display: flex;
		align-items: center;
		gap: 0.45rem;
	}

	.upload-choice input {
		width: auto;
	}

	.organization-creator {
		margin-top: 0.8rem;
		padding: 0.7rem;
		border: 1px dashed rgba(0, 0, 0, 0.2);
		display: grid;
		gap: 0.45rem;
	}

	.field-note {
		margin: 0;
		font-size: 0.85rem;
		color: #444;
	}

	.dataset-form {
		margin-top: 0.45rem;
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 0.55rem;
	}

	.inline {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 0.45rem;
	}

	button {
		padding: 0.45rem 0.7rem;
		border: 1px solid rgba(0, 0, 0, 0.2);
		background: #fff;
		cursor: pointer;
	}

	.manager-list li,
	.dataset-list li,
	.partner-list li {
		padding: 0.45rem 0;
		border-top: 1px solid rgba(0, 0, 0, 0.08);
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	.partner-list {
		list-style: none;
		padding: 0;
		margin: 0.5rem 0 0;
	}

	.partner-actions {
		margin-top: 0.45rem;
	}

	.team-member-row {
		flex-direction: column;
		align-items: flex-start;
		gap: 0.15rem;
	}

	.team-member-name {
		font-family: 'GT Super Bold', serif;
	}

	.team-member-meta {
		font-size: 0.85rem;
		color: #5a5a5a;
	}

	.team-member-row.empty {
		color: #666;
		font-family: 'GT Super Regular', serif;
	}

	.upload-governance {
		font-size: 0.92rem;
		line-height: 1.5;
		padding: 0.6rem;
		background: rgba(34, 80, 34, 0.08);
		border-left: 3px solid #1f4d1f;
	}

	.hint {
		font-size: 0.9rem;
		color: #444;
	}

	.error {
		background: #ffe7e7;
		border: 1px solid #ffb7b7;
		padding: 0.6rem;
	}

	.message {
		background: #e8f8e8;
		border: 1px solid #b7dcb7;
		padding: 0.6rem;
	}

	@media (max-width: 980px) {
		.grid,
		.lower {
			grid-template-columns: 1fr;
		}

		.form-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
