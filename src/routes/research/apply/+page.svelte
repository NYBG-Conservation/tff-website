<script lang="ts">
	import {
		submitResearchApplication,
		type ResearchCollectionType,
		type ResearchProjectType
	} from '$lib/api/researchApplications';

	type FormState = {
		website: string;
		applicant_name: string;
		title_position: string;
		institution: string;
		email: string;
		phone: string;
		address: string;
		co_pi: string;
		project_title: string;
		project_type: ResearchProjectType | '';
		description: string;
		anticipated_start_date: string;
		anticipated_end_date: string;
		desired_species: string;
		collection_type: ResearchCollectionType;
		research_location: string;
		plant_tracker_notes: string;
		abiotic_variables: string;
		biotic_variables: string;
		funding_sources: string;
		wildlife_permits: string;
		nybg_infrastructure: string;
		site_visits: string;
		visitor_impacts: string;
		research_sensitivity: string;
		resources: string;
		publications: string;
		additional_comments: string;
		attestation_name: string;
		attestation_date: string;
	};

	const emptyForm = (): FormState => ({
		website: '',
		applicant_name: '',
		title_position: '',
		institution: '',
		email: '',
		phone: '',
		address: '',
		co_pi: '',
		project_title: '',
		project_type: '',
		description: '',
		anticipated_start_date: '',
		anticipated_end_date: '',
		desired_species: '',
		collection_type: '',
		research_location: '',
		plant_tracker_notes: '',
		abiotic_variables: '',
		biotic_variables: '',
		funding_sources: '',
		wildlife_permits: '',
		nybg_infrastructure: '',
		site_visits: '',
		visitor_impacts: '',
		research_sensitivity: '',
		resources: '',
		publications: '',
		additional_comments: '',
		attestation_name: '',
		attestation_date: ''
	});

	let form = emptyForm();
	let submitting = false;
	let submittedId: number | null = null;
	let errorMessage = '';
	let fieldErrors: Record<string, string> = {};

	$: isPlant = form.project_type === 'Plant_material_collections';
	$: isOnsite = form.project_type === 'onsite_research';

	function formatApiErrors(body: unknown): { message: string; fields: Record<string, string> } {
		const fields: Record<string, string> = {};
		if (!body || typeof body !== 'object') {
			return { message: 'Submission failed. Please try again.', fields };
		}
		const record = body as Record<string, unknown>;
		if (typeof record.detail === 'string') {
			return { message: record.detail, fields };
		}
		const parts: string[] = [];
		for (const [key, value] of Object.entries(record)) {
			const text = Array.isArray(value) ? value.map(String).join(' ') : String(value);
			fields[key] = text;
			parts.push(`${key}: ${text}`);
		}
		return {
			message: parts.length ? parts.join(' ') : 'Please correct the highlighted fields.',
			fields
		};
	}

	async function handleSubmit(event: Event) {
		event.preventDefault();
		errorMessage = '';
		fieldErrors = {};
		if (!form.project_type) {
			errorMessage = 'Please select a project type.';
			return;
		}
		submitting = true;
		try {
			const payload = {
				...form,
				project_type: form.project_type as ResearchProjectType,
				collection_type: form.collection_type || undefined,
				start_date: form.anticipated_start_date || undefined,
				end_date: form.anticipated_end_date || undefined
			};
			const result = await submitResearchApplication(payload);
			submittedId = result.id;
			form = emptyForm();
		} catch (err) {
			const body = err && typeof err === 'object' && 'body' in err ? (err as { body: unknown }).body : null;
			const formatted = formatApiErrors(body);
			errorMessage = formatted.message;
			fieldErrors = formatted.fields;
		} finally {
			submitting = false;
		}
	}
</script>

<section class="apply-page">
	<header class="page-header">
		<p class="eyebrow"><a href="/research">Research</a> / Apply</p>
		<h1 class="page-title">Living Collections Research Application</h1>
		<p class="lede">
			Submit at least two weeks before your anticipated start date. If approved, NYBG will send
			agreement forms and next steps by email. Questions:
			<a href="mailto:forest@nybg.org">forest@nybg.org</a>.
		</p>
	</header>

	{#if submittedId}
		<div class="success-panel" role="status">
			<h2 class="section-heading">Application received</h2>
			<p>
				Thank you. Your application (#{submittedId}) was submitted. Forest staff will follow up by
				email.
			</p>
			<p>
				<a href="/research">Return to Research</a>
				·
				<button type="button" class="linkish" on:click={() => (submittedId = null)}>
					Submit another
				</button>
			</p>
		</div>
	{:else}
		<form class="apply-form" on:submit={handleSubmit} novalidate>
			{#if errorMessage}
				<p class="form-error" role="alert">{errorMessage}</p>
			{/if}

			<!-- Honeypot -->
			<label class="hp" aria-hidden="true">
				Website
				<input type="text" name="website" tabindex="-1" autocomplete="off" bind:value={form.website} />
			</label>

			<section class="form-section" aria-labelledby="applicant-heading">
				<h2 id="applicant-heading" class="section-heading">Applicant</h2>
				<div class="grid">
					<label>
						<span>PI / applicant name *</span>
						<input required bind:value={form.applicant_name} class:invalid={!!fieldErrors.applicant_name} />
					</label>
					<label>
						<span>Title / position</span>
						<input bind:value={form.title_position} />
					</label>
					<label class="full">
						<span>Affiliated institution *</span>
						<input required bind:value={form.institution} class:invalid={!!fieldErrors.institution} />
					</label>
					<label>
						<span>Email *</span>
						<input type="email" required bind:value={form.email} class:invalid={!!fieldErrors.email} />
					</label>
					<label>
						<span>Phone</span>
						<input type="tel" bind:value={form.phone} />
					</label>
					<label class="full">
						<span>Address</span>
						<textarea rows="2" bind:value={form.address}></textarea>
					</label>
					<label class="full">
						<span>Co-PI information</span>
						<textarea rows="2" bind:value={form.co_pi} placeholder="Names and affiliations"></textarea>
					</label>
				</div>
			</section>

			<section class="form-section" aria-labelledby="project-heading">
				<h2 id="project-heading" class="section-heading">Project</h2>
				<div class="grid">
					<label class="full">
						<span>Project title *</span>
						<input required bind:value={form.project_title} class:invalid={!!fieldErrors.project_title} />
					</label>
					<label class="full">
						<span>Project type *</span>
						<select required bind:value={form.project_type} class:invalid={!!fieldErrors.project_type}>
							<option value="">Select…</option>
							<option value="Plant_material_collections">Plant material collections</option>
							<option value="onsite_research">On-site research</option>
						</select>
					</label>
					<label class="full">
						<span>Project description / abstract *</span>
						<textarea
							required
							rows="5"
							bind:value={form.description}
							class:invalid={!!fieldErrors.description}
						></textarea>
					</label>
					<label>
						<span>Anticipated start date</span>
						<input type="date" bind:value={form.anticipated_start_date} />
					</label>
					<label>
						<span>Anticipated end date</span>
						<input type="date" bind:value={form.anticipated_end_date} />
					</label>
				</div>
			</section>

			{#if isPlant}
				<section class="form-section" aria-labelledby="collection-heading">
					<h2 id="collection-heading" class="section-heading">Plant material collection</h2>
					<p class="hint">
						Search living collections with
						<a href="https://www.nybg.org/gardens/planttracker/" target="_blank" rel="noopener noreferrer"
							>NYBG Plant Tracker</a
						>.
					</p>
					<div class="grid">
						<label class="full">
							<span>Desired species for collection *</span>
							<textarea
								required
								rows="3"
								bind:value={form.desired_species}
								class:invalid={!!fieldErrors.desired_species}
							></textarea>
						</label>
						<label>
							<span>Collection type</span>
							<select bind:value={form.collection_type}>
								<option value="">Select…</option>
								<option value="on-site_collection">On-site collection</option>
								<option value="off-site_collection">Off-site collection</option>
								<option value="other">Other / not applicable</option>
							</select>
						</label>
						<label class="full">
							<span>Plant Tracker notes</span>
							<textarea rows="2" bind:value={form.plant_tracker_notes}></textarea>
						</label>
					</div>
				</section>
			{/if}

			{#if isOnsite}
				<section class="form-section" aria-labelledby="location-heading">
					<h2 id="location-heading" class="section-heading">On-site research logistics</h2>
					<p class="hint">
						Identify Garden locations with
						<a href="https://www.nybg.org/gardens/planttracker/" target="_blank" rel="noopener noreferrer"
							>NYBG Plant Tracker</a
						>.
					</p>
					<div class="grid">
						<label class="full">
							<span>Desired location of research *</span>
							<textarea
								required
								rows="3"
								bind:value={form.research_location}
								class:invalid={!!fieldErrors.research_location}
							></textarea>
						</label>
						<label class="full">
							<span>Abiotic variables</span>
							<textarea rows="2" bind:value={form.abiotic_variables}></textarea>
						</label>
						<label class="full">
							<span>Biotic variables</span>
							<textarea rows="2" bind:value={form.biotic_variables}></textarea>
						</label>
						<label class="full">
							<span>Wildlife research permits</span>
							<textarea rows="2" bind:value={form.wildlife_permits}></textarea>
						</label>
						<label class="full">
							<span>NYBG research infrastructure needed</span>
							<textarea rows="2" bind:value={form.nybg_infrastructure}></textarea>
						</label>
						<label class="full">
							<span>Site visits</span>
							<textarea rows="2" bind:value={form.site_visits}></textarea>
						</label>
						<label class="full">
							<span>Visitor impacts</span>
							<textarea rows="2" bind:value={form.visitor_impacts}></textarea>
						</label>
						<label class="full">
							<span>Research sensitivity</span>
							<textarea rows="2" bind:value={form.research_sensitivity}></textarea>
						</label>
					</div>
				</section>
			{/if}

			{#if form.project_type}
				<section class="form-section" aria-labelledby="ops-heading">
					<h2 id="ops-heading" class="section-heading">Funding, resources &amp; publications</h2>
					<div class="grid">
						<label class="full">
							<span>Funding sources</span>
							<textarea rows="2" bind:value={form.funding_sources}></textarea>
						</label>
						<label class="full">
							<span>Resources</span>
							<textarea rows="2" bind:value={form.resources}></textarea>
						</label>
						<label class="full">
							<span>Publications</span>
							<textarea rows="2" bind:value={form.publications}></textarea>
						</label>
						<label class="full">
							<span>Additional comments</span>
							<textarea rows="3" bind:value={form.additional_comments}></textarea>
						</label>
					</div>
				</section>
			{/if}

			<section class="form-section" aria-labelledby="attest-heading">
				<h2 id="attest-heading" class="section-heading">Attestation</h2>
				<p class="hint">
					Include your name and today’s date to confirm this application was completed by the PI.
				</p>
				<div class="grid">
					<label>
						<span>PI name *</span>
						<input
							required
							bind:value={form.attestation_name}
							class:invalid={!!fieldErrors.attestation_name}
						/>
					</label>
					<label>
						<span>Date *</span>
						<input
							type="date"
							required
							bind:value={form.attestation_date}
							class:invalid={!!fieldErrors.attestation_date}
						/>
					</label>
				</div>
			</section>

			<div class="actions">
				<button type="submit" class="submit-button" disabled={submitting}>
					{submitting ? 'Submitting…' : 'Submit application'}
				</button>
				<a class="back-link" href="/research">Cancel</a>
			</div>
		</form>
	{/if}
</section>

<style>
	.apply-page {
		max-width: 820px;
		margin: 2rem auto 4rem;
		padding: 0 1rem;
	}

	.page-header {
		margin-bottom: 2rem;
	}

	.eyebrow {
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		margin: 0 0 0.5rem;
		color: #444;
	}

	.eyebrow a {
		color: #1e2f1e;
	}

	.page-title {
		font-family: 'GT Super Bold', serif;
		font-size: clamp(1.6rem, 3vw, 2.1rem);
		margin: 0 0 0.75rem;
		color: #1e2f1e;
		line-height: 1.2;
	}

	.lede {
		font-family: 'GT Super Regular', serif;
		font-size: 1.05rem;
		line-height: 1.55;
		margin: 0;
		color: #222;
	}

	.section-heading {
		font-family: 'GT Super Bold', serif;
		font-size: 1.15rem;
		margin: 0 0 1rem;
		color: #1e2f1e;
	}

	.form-section {
		margin: 0 0 2rem;
		padding: 1.25rem 1.35rem;
		border: 1px solid rgba(0, 0, 0, 0.12);
		background: rgba(200, 181, 0, 0.06);
	}

	.hint {
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		margin: -0.35rem 0 1rem;
		color: #333;
	}

	.grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.9rem 1rem;
	}

	label {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		font-family: 'GT Super Regular', serif;
		font-size: 0.92rem;
		color: #1e2f1e;
	}

	label.full {
		grid-column: 1 / -1;
	}

	input,
	select,
	textarea {
		font: inherit;
		padding: 0.55rem 0.65rem;
		border: 1px solid rgba(30, 47, 30, 0.35);
		background: #fff;
		color: #111;
	}

	input.invalid,
	select.invalid,
	textarea.invalid {
		border-color: #7a1e1e;
	}

	.hp {
		position: absolute;
		left: -10000px;
		top: auto;
		width: 1px;
		height: 1px;
		overflow: hidden;
	}

	.form-error {
		font-family: 'GT Super Regular', serif;
		color: #7a1e1e;
		background: rgba(122, 30, 30, 0.08);
		padding: 0.75rem 1rem;
		margin: 0 0 1.25rem;
	}

	.actions {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 1rem;
	}

	.submit-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.7rem 1.25rem;
		border: 1px solid #1e2f1e;
		background: #1e2f1e;
		color: #fff;
		font-family: 'GT Super Bold', serif;
		font-size: 0.95rem;
		cursor: pointer;
	}

	.submit-button:hover:not(:disabled),
	.submit-button:focus-visible:not(:disabled) {
		background: #fff;
		color: #1e2f1e;
	}

	.submit-button:disabled {
		opacity: 0.65;
		cursor: wait;
	}

	.back-link,
	.linkish {
		font-family: 'GT Super Regular', serif;
		color: #1e2f1e;
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		text-decoration: underline;
		font-size: 0.95rem;
	}

	.success-panel {
		padding: 1.5rem 1.35rem;
		border: 1px solid rgba(30, 47, 30, 0.25);
		background: rgba(200, 181, 0, 0.1);
		font-family: 'GT Super Regular', serif;
		line-height: 1.55;
	}

	@media (max-width: 640px) {
		.grid {
			grid-template-columns: 1fr;
		}
	}
</style>
