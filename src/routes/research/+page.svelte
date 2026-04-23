<script lang="ts">
	import { datasetRecords } from '$lib/data/datasetRecords';
	import { researchProjects, type ResearchProject } from '$lib/data/researchProjects';

	let activeProjectId: string | null = null;
	$: activeProject = researchProjects.find((project) => project.id === activeProjectId) ?? null;
	$: relatedDatasets = activeProject ? getRelatedDatasets(activeProject) : [];

	function openProject(projectId: string) {
		activeProjectId = projectId;
	}

	function closeProjectModal() {
		activeProjectId = null;
	}

	function handleEscapeKey(event: KeyboardEvent) {
		if (event.key === 'Escape' && activeProjectId) {
			closeProjectModal();
		}
	}

	function closeOnOverlayInteraction(event: MouseEvent | KeyboardEvent) {
		if ('target' in event && event.target === event.currentTarget) {
			closeProjectModal();
		}
	}

	function getRelatedDatasets(project: ResearchProject) {
		if (!project.datasetIds?.length) {
			return [];
		}

		return project.datasetIds
			.map((datasetId) => datasetRecords.find((record) => record.id === datasetId))
			.filter((record): record is (typeof datasetRecords)[number] => Boolean(record));
	}
</script>

<svelte:window on:keydown={handleEscapeKey} />

<section class="research-content">
	<!-- <h1 class="page-title">Research in the Thain Family Forest</h1> -->
	<p class="intro-paragraph">
		The Thain Family Forest is a living laboratory with several ongoing research projects focused on
		understanding the impacts of the urban environment on the Forest and evaluating ecological
		restoration projects.
	</p><br/>
	<p class="intro-paragraph">
		Research in the Forest is conducted by staff, students, and volunteers. Visiting researchers,
		including students, are welcome to conduct research in the Forest; please visit the Visiting
		Research page for more information.
	</p>
	<p class="intro-paragraph">
		<a class="admin-login-link" href="http://localhost:8000/admin/login/?next=/admin/">
			Researcher / Admin Login
		</a>
	</p>

	<h2 class="section-heading">Ongoing Research Projects</h2>

	<div class="project-grid">
		{#each researchProjects as project}
			<button type="button" class="project-card" on:click={() => openProject(project.id)}>
				<img src={project.image} alt={project.title} loading="lazy" />
				<div class="project-card-body">
					<h2 class="project-title">{project.title}</h2>
					<p class="project-summary">{project.summary}</p>
					<span class="read-more-link">
						Read more
						<span class="read-more-arrow" aria-hidden="true">→</span>
					</span>
				</div>
			</button>
		{/each}
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
				id={`project-details-${activeProject.id}`}
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
					{#each activeProject.descriptionParagraphs as paragraph}
						<p>{paragraph}</p>
					{/each}
					<div class="related-datasets">
						<h4>Related datasets</h4>
						{#if relatedDatasets.length > 0}
							<ul>
								{#each relatedDatasets as dataset}
									<li>
										<a href={`/data?project=${activeProject.id}`}>{dataset.title}</a>
									</li>
								{/each}
							</ul>
						{:else}
							<p class="empty-related">No linked datasets yet.</p>
						{/if}
					</div>
				</div>
			</div>
		</div>
	{/if}

	<section class="publications">
		<h2 class="section-heading">Selected Publications from Research in the Thain Family Forest</h2>
		<ul>
			<li>
				Atha, D., J.A. Schuler, S.L. Tobing. 2014. Corydalis incisa (Fumariaceae) in Bronx and
				Westchester Counties, New York. <em>Phytoneuron</em> 96: 1-6.
			</li>
			<li>
				Munshi-South, J. and C. Nagy. 2014. Urban park characteristics, genetic variation, and
				historical demography of white-footed mouse (<em>Peromyscus leucopus</em>) populations in New
				York City. <em>PeerJ</em> 2:e310; DOI 10.7717/peerj.310.
			</li>
			<li>
				Rachlin J.W., B.E. Warkentine, A. Pappantoniou. 2007. An Evaluation of the Ichthyofauna of the
				Bronx River, a Resilient Urban Waterway. <em>Northeastern Naturalist</em> 14(4):531-544.
			</li>
			<li>
				Gregg, J. W., C.G. Jones, and T.E. Dawson. 2003. Urbanization on Tree Growth in the Vicinity of
				New York City. <em>Nature</em> 424:183-187.
			</li>
			<li>
				McDonnell, M.J., S.T.A. Pickett, P. Groffman, P. Bohlen, R. Pouyat, W.C. Zipperer, and R.W.
				Parmelee. 1997. Ecosystem Processes along an urban-to-rural gradient. <em>Urban Ecosystems</em>
				1: 21-36.
			</li>
			<li>
				McDonnell, M.J. and S.T.A. Pickett. 1990. Ecosystem Structure and Function along Urban-Rural
				Gradients: An Unexploited Opportunity for Ecology. <em>Ecology</em> 71(4): 1232-1237.
			</li>
			<li>
				Rudnicky, J.L. and M. J. McDonnell. 1989. Forty-Eight Years of Canopy Change in a
				Hardwood-Hemlock Forest in New York City. <em>Bulletin of the Torrey Botanical Club</em>
				116(1): 52-64.
			</li>
			<li>
				White, C.S. and M.J. McDonnell. 1988. Nitrogen Cycling Processes and Soil Characteristics in an
				Urban versus Rural Forest. <em>Biogeochemistry</em> 5(2): 243-262.
			</li>
			<li>Leonardi L. 1987. The Bryophytes of The New York Botanical Garden Forest. <em>Evansia</em> 4: 8-11.</li>
			<li>
				Honkala, D.A. and J.B. McAninch. 1980. The New York Botanical Garden Hemlock Forest Project Part
				I. NYBG Institutional Report.
			</li>
			<li>
				Honkala, D.A. and J.B. McAninch. 1981. The New York Botanical Garden Hemlock Forest Project Part
				II. NYBG Institutional Report.
			</li>
			<li>
				Moore, B., H.M. Richards, H.A. Gleason, and A.B. Stout. 1924. Hemlock and its environment.
				<em>Bulletin of The New York Botanical Garden</em> 12(45):325-350.
			</li>
			<li>
				Britton, N.L. 1906. The Hemlock Grove on the banks of the Bronx River and what it signifies.
				<em>Contributions from The New York Botanical Garden</em> 88:5-13.
			</li>
			<li>
				Howe, M.A. and E.G. Britton. 1899. Lists of Plants in the Grounds, 1898.
				<em>Bulletin of The New York Botanical Garden</em> 1(4): 195-203.
			</li>
		</ul>
	</section>
</section>

<style>
	.research-content {
		max-width: 1400px;
		margin: 2rem auto;
		padding: 0 1rem 3rem;
	}

	.intro-paragraph {
		font-family: 'GT Super Regular', serif;
		font-size: 1.05rem;
		line-height: 1.55;
		margin: auto;
		color: #222;
		max-width: 1100px;

	}

	.admin-login-link {
		color: #111;
		text-decoration: none;
		position: relative;
		display: inline-flex;
		align-items: center;
	}

	.admin-login-link::after {
		content: '';
		position: absolute;
		bottom: -1px;
		left: 0;
		width: 0;
		height: 1.5px;
		background-color: #111;
		transition: width 0.22s ease;
	}

	.admin-login-link:hover::after,
	.admin-login-link:focus-visible::after {
		width: 100%;
	}

	.section-heading {
		font-family: 'NY Botanical Gothic', serif;
		font-size: clamp(1.35rem, 2.2vw, 2rem);
		text-transform: uppercase;
		line-height: 1.1;
		margin: 2rem 0 1rem;
		color: #1e2f1e;
	}

	.project-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1.5rem;
	}

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
		transition: transform 0.18s ease, box-shadow 0.18s ease;
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

	.project-card img {
		width: 100%;
		aspect-ratio: 4 / 3;
		object-fit: cover;
		display: block;
		background: #f4f4f4;
	}

	.project-card-body {
		padding: 0.95rem 1rem 1rem;
		display: flex;
		flex-direction: column;
		flex: 1;
	}

	.project-title {
		margin: 0;
		padding: 0;
		font-family: 'GT Super Regular', serif;
		font-size: clamp(1.15rem, 1.9vw, 1.6rem);
		line-height: 1.2;
		color: #111;
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

	.related-datasets a {
		font-family: 'GT Super Regular', serif;
		color: #1b3d1b;
	}

	.empty-related {
		margin-bottom: 0;
		color: #555;
	}

	.publications {
		max-width: 1100px;
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
			max-width: 700px;
		}

		.publications {
			max-width: 700px;
		}
	}
</style>