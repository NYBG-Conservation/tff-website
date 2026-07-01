<script lang="ts">
	import '../../styles/all.css';
	import gsap from 'gsap';
	import { onMount } from 'svelte';
	import { slide } from 'svelte/transition';
	// import { active } from '$lib/stores.js';

	// console.log(active)

	let aboutitems = ['Methodology', 'Data', 'Muir web'];

	let abouttext = [0, 1, 2];

	// List of images in the watermarked_imgs folder (artist credit optional, shown when set)
	const images = [
		{ id: 'img-033', filename: 'BNY_nadir.png', artist: 'Eric Mehl' },
		{ id: 'img-032', filename: 'Manahatta-Website-30K.png', artist: 'Markley Boyer' },
		{ id: 'img-001', filename: '96335_MHNTA_CH1_000_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-002', filename: '96335_MHNTA_CH1_006_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-003', filename: '96335_MHNTA_CH1_024_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-004', filename: '96335_MHNTA_CH5_026_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-005', filename: '96335_MNHTA_CH1_003_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-006', filename: '96335_MNHTA_CH1_011_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-007', filename: '96335_MNHTA_CH1_017_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-008', filename: '96335_MNHTA_CH1_021_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-009', filename: '96335_MNHTA_CH5_026.jpg', artist: 'Markley Boyer' },
		{ id: 'img-010', filename: '96335_MNHTA_CH6_027_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-011', filename: 'BatteryParkCity_96335_MNHTA_CH1_005_V.jpg', artist: 'Markley Boyer' },
		{ id: 'img-012', filename: 'collectpond.jpg', artist: 'Markley Boyer' },
		{ id: 'img-013', filename: 'EmpireStateBuilding_96335_MNHTA_CH1_010_V.jpg', artist: 'Stephen Amiaga' },
		{ id: 'img-014', filename: 'Harlem_96335_MNHTA_CH1_016_V.jpg', artist: 'Stephen Amiaga' },
		{ id: 'img-015', filename: 'InwoodPark_96335_MNHTA_CH1_023_V.jpg', artist: 'Stephen Amiaga' },
		{ id: 'img-016', filename: 'LowerManhattan_96335_MNHTA_CH1_031_V.jpg', artist: 'Stephen Amiaga' },
		{ id: 'img-017', filename: 'LowerWestSide_96335_MNHTA_CH1_005_V.jpg', artist: 'Stephen Amiaga' },
		{ id: 'img-018', filename: 'MHNTA_split.jpg', artist: 'Markley Boyer and Yann Arthus Bertrand' },
		{ id: 'img-019', filename: 'Midtown_96335_MNHTA_CH6_0026_V.jpg', artist: 'Stephen Amiaga' },
		{ id: 'img-020', filename: 'RooseveltIsland_96335_MNHTA_CH1_020_V.jpg', artist: 'Stephen Amiaga' },
		{ id: 'img-021', filename: 'G2.jpg', artist: 'Markley Boyer' },
		{ id: 'img-022', filename: 'G28.jpg', artist: 'Markley Boyer' },
		{ id: 'img-023', filename: 'I10.jpg', artist: 'Markley Boyer' },
		{ id: 'img-024', filename: 'View 1.jpg', artist: 'Markley Boyer' },
		{ id: 'img-025', filename: 'View 2.jpg', artist: 'Markley Boyer' },
		{ id: 'img-026', filename: 'View 3.jpg', artist: 'Markley Boyer' },
		{ id: 'img-027', filename: 'View 4.jpg', artist: 'Markley Boyer' },
		{ id: 'img-028', filename: 'View 5.jpg', artist: 'Markley Boyer' },
		{ id: 'img-029', filename: 'View 6.jpg', artist: 'Markley Boyer' },
		{ id: 'img-030', filename: 'View 7.jpg', artist: 'Markley Boyer' },
		{ id: 'img-031', filename: 'Kimmelman-Collect-Pond.png', artist: 'Eric Mehl and Jesse Moy' }
	];

	
	const faqs: { question: string; answer: string }[] = [
		{
			question: 'Can I license your images?',
			answer: 'For licensing inquiries about our maps, visualizations, or other images from <i>Mannahatta</i>, <i>The Welikia Project</i>, and other projects, please contact us through the form below and fill out the associated request form. If you\'d like to view all available images, <a href="#image-licensing">view the gallery here</a>.'
		},
		{
			question: 'How can I access historical ecology data?',
			answer: 'Historical ecology data and map tools are available through our public platforms: the Welikia Map Explorer and Layers of the Past. Links to these resources are on the <a href="/research">research page</a>. For research partnerships or bulk data access, please reach out via the contact form below.'
		},
		{
			question: 'When is the book <i>Before New York</i> coming out?',
			answer: '<i>Before New York: The Natural Geography of the City, An Atlas and Gazetteer</i> will be published November 3, 2026. It is available now for <a href="https://www.nybgshop.org/collections/books/products/before-new-york-the-natural-geography-of-the-city-an-atlas-and-gazetteer" target="_blank" rel="noopener noreferrer">preorder</a>.'
		},
		{
			question: 'Do you offer internships or volunteer opportunities?',
			answer: 'We do not currently have any internship or volunteer opportunities available. For opportunities to work with other teams at NYBG, please reach out to <a href="mailto:james.vickers@nybg.org">James Vickers</a> within the NYBG Volunteer Services department.'
		}
	];
	let activeFaqIndex: number | null = null;

	function toggleFaq(index: number) {
		activeFaqIndex = activeFaqIndex === index ? null : index;
	}

	let currentImageIndex = 0;
	let selectedImageIds: string[] = [];
	let isModalOpen = false;
	let modalImageIndex = 0;
	let priceListAcknowledged = false;
	let isMobile = false;
	let selectedType = '';

	// Standalone page gallery (outside form) - separate index so it doesn’t affect form carousel
	let pageGalleryIndex = 0;
	let modalThumbStripEl: HTMLDivElement | null = null;
	function nextPageGalleryImage() {
		pageGalleryIndex = (pageGalleryIndex + 1) % images.length;
	}
	function previousPageGalleryImage() {
		pageGalleryIndex = (pageGalleryIndex - 1 + images.length) % images.length;
	}
	function openModalFromPageGallery() {
		modalImageIndex = pageGalleryIndex;
		isModalOpen = true;
		document.body.style.overflow = 'hidden';
	}

	function togglePageGallerySelection() {
		const id = images[pageGalleryIndex].id;
		if (selectedImageIds.includes(id)) {
			selectedImageIds = selectedImageIds.filter((x) => x !== id);
		} else {
			selectedImageIds = [...selectedImageIds, id];
		}
	}

	// Detect if user is on mobile (excluding tablets/iPads)
	function detectMobile() {
		if (typeof window === 'undefined') return false;

		const width = window.innerWidth;
		const userAgent = navigator.userAgent.toLowerCase();

		// Check if it's a tablet/iPad (these are okay)
		const isTablet =
			/ipad|tablet|android(?!.*mobile)/i.test(userAgent) || (width >= 768 && width < 1024);

		// Mobile phone: small screen and not a tablet
		isMobile = width < 768 && !isTablet;
	}

	function handleFormSubmit(event: Event) {
		const form = event.target as HTMLFormElement;
		const honeypot = form.querySelector('input[name="website"]') as HTMLInputElement;

		if (honeypot && honeypot.value !== '') {
			event.preventDefault();
			alert('Spam detected. Please try again.');
			return false;
		}
	}

	function nextImage() {
		currentImageIndex = (currentImageIndex + 1) % images.length;
	}

	function previousImage() {
		currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
	}

	function toggleImageSelection() {
		const currentImageId = images[currentImageIndex].id;
		if (selectedImageIds.includes(currentImageId)) {
			selectedImageIds = selectedImageIds.filter((id) => id !== currentImageId);
		} else {
			selectedImageIds = [...selectedImageIds, currentImageId];
		}
	}

	function unselectAll() {
		selectedImageIds = [];
	}

	function removeImageFromSelection(imageId: string) {
		selectedImageIds = selectedImageIds.filter((id) => id !== imageId);
	}

	function openModal() {
		modalImageIndex = currentImageIndex;
		isModalOpen = true;
		document.body.style.overflow = 'hidden';
	}

	function closeModal() {
		isModalOpen = false;
		document.body.style.overflow = '';
	}

	function setModalImage(index: number) {
		modalImageIndex = index;
	}

	function handleModalKeydown(event: KeyboardEvent) {
		if (!isModalOpen) return;
		if (event.key === 'Escape') {
			closeModal();
			return;
		}
		if (event.key === 'ArrowLeft') {
			modalImageIndex = (modalImageIndex - 1 + images.length) % images.length;
			event.preventDefault();
		} else if (event.key === 'ArrowRight') {
			modalImageIndex = (modalImageIndex + 1) % images.length;
			event.preventDefault();
		}
	}

	function getImageFilename(imageId: string): string {
		const image = images.find((img) => img.id === imageId);
		return image ? image.filename : imageId;
	}

	$: isCurrentImageSelected = selectedImageIds.includes(images[currentImageIndex].id);
	$: isPageGalleryImageSelected = selectedImageIds.includes(images[pageGalleryIndex].id);

	// Scroll active thumbnail into view when navigating in modal (e.g. arrow keys)
	$: if (isModalOpen && modalThumbStripEl && modalImageIndex >= 0) {
		const active = modalThumbStripEl.querySelector('.modal-thumb.active');
		if (active) active.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' });
	}
	$: messageLabel =
		selectedType === 'custom-image'
			? 'Please detail your custom image or rendering needs below, including the desired size, location, resolution, and any other specifications. We will respond to your inquiry as soon as possible.'
			: 'Your message:';

	onMount(() => {
		detectMobile();

		// Re-detect on window resize
		const handleResize = () => {
			detectMobile();
		};
		window.addEventListener('resize', handleResize);

		gsap.from('.content-body h1, .content-body h2', {
			duration: 0.8,
			yPercent: 36,
			ease: 'power4.out',
			stagger: 0.4
		});

		gsap.to('.content-body h1, .content-body h2', {
			opacity: 1,
			duration: 0.6,
			ease: 'power2.in',
			stagger: 0.2
			// delay: .5
		});

		gsap.from('.rest-content', {
			duration: 0.3,
			yPercent: 2,
			ease: 'power4.out',
			opacity: 0,
			delay: 0.5
		});
		gsap.to('.rest-content', { opacity: 1, duration: 1.8, ease: 'power2.out', delay: 0.5 });

		return () => {
			window.removeEventListener('resize', handleResize);
		};
	});

	// Showing/hiding the second dropdown based on the first dropdown selection
	function toggleSecondDropdown() {
		const typeDropdown = document.getElementById('typeDropdown') as HTMLSelectElement | null;
		const container = document.getElementById('generalDropdownContainer');
		const documentsContainer = document.getElementById('documentsContainer');

		if (!typeDropdown) return;

		const mainSelect = typeDropdown.value;
		selectedType = mainSelect;

		if (mainSelect === 'general') {
			if (container) container.style.display = 'block';
		} else {
			if (container) container.style.display = 'none';
		}

		if (mainSelect === 'image-license') {
			if (documentsContainer) documentsContainer.style.display = 'block';
		} else {
			if (documentsContainer) documentsContainer.style.display = 'none';
		}
	}

	function goToImageLicenseRequest() {
		selectedType = 'image-license';
		const container = document.getElementById('generalDropdownContainer');
		const documentsContainer = document.getElementById('documentsContainer');
		if (container) container.style.display = 'none';
		if (documentsContainer) documentsContainer.style.display = 'block';
		window.location.hash = 'contact-form';
		document.getElementById('contact-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
	}
</script>

<svelte:window on:keydown={handleModalKeydown} />

<div class="content-body">
	 
<h2>Frequently asked questions</h2>
<div class="faq">
	{#each faqs as faq, index}
		<div class="faq-item" class:is-open={activeFaqIndex === index}>
			<button
				type="button"
				class="faq-question"
				aria-expanded={activeFaqIndex === index}
				aria-controls={`faq-answer-${index}`}
				on:click={() => toggleFaq(index)}
			>
				{@html faq.question}
			</button>
			{#if activeFaqIndex === index}
				<div id={`faq-answer-${index}`} class="faq-answer" transition:slide={{ duration: 220 }}>
					<p>{@html faq.answer}</p>
				</div>
			{/if}
		</div>
	{/each}
</div>


	<h2 id="contact-form" class="contact-heading">Contact Us</h2>
	<form
		action="https://formspree.io/f/xovyvvao"
		method="POST"
		enctype="multipart/form-data"
		on:submit={handleFormSubmit}
	>
		<label>
			Your email:
			<input type="email" name="email" required />
		</label><br />
		<label>
			First name:
			<input type="text" name="first-name" required />
		</label><br />
		<label>
			Last name:
			<input type="text" name="last-name" required />
		</label><br />
		<label>
			Affiiliate institution:
			<input type="text" name="institution" />
		</label><br />
		<!-- Honeypot field - should be left empty by humans -->
		<label class="honeypot-field" aria-hidden="true">
			Leave this field empty:
			<input type="text" name="website" autocomplete="off" tabindex="-1" />
		</label>
		<label for="typeDropdown">What are you interested in?</label>
		<select
			id="typeDropdown"
			name="selectedType"
			bind:value={selectedType}
			on:change={toggleSecondDropdown}
			required
		>
			<option value="data-download">Data download request</option>
			<option value="image-license">Image licensing request</option>
			<option value="custom-image">Custom image request</option>
			<option value="feedback-suggestion">Feedback or suggestion</option>
			<option value="general">General inquiry</option>
		</select><br />

		<!-- Mobile warning for image licensing -->
		{#if isMobile && selectedType === 'image-license'}
			<div class="mobile-warning">
				<p>
					<strong>We recommend using a desktop or tablet device</strong> to submit image licensing requests.
					The image selection and document upload features may require a larger screen. Tablets and iPads
					are supported.
				</p>
			</div>
		{/if}

		<!-- Data download request message -->
		{#if selectedType === 'data-download'}
			<div class="data-download-message">
				<p>
					Data download requests are currently handled on a case-by-case basis. Please state the type of data, research extent, and intended use below and we will get back to you as soon as possible.
				</p>
			</div>
		{/if}

		<!-- General inquiry type dropdown -->
		<div id="generalDropdownContainer" style="display:none;">
			<label for="subOption">General inquiry type:</label>
			<select id="subOption" name="subOption" required={selectedType === 'general'}>
				<option value="tabling">Tabling request</option>
				<option value="speaking">Speaking request</option>
				<option value="workshop">Workshop request</option>
				<option value="questions">Questions about the project</option>
				<option value="other">Other</option>
			</select>
		</div>

		<!-- Image licensing: show synced selection (gallery + selection live below the form) -->
		{#if selectedType === 'image-license'}
			<div class="selected-images-summary">
				{#if selectedImageIds.length > 0}
					<p>Requesting licenses for the following selected images: [{selectedImageIds.join(', ')}]</p>
				{:else}
					<p class="selected-images-prompt">
						<svg class="selected-images-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
						<span>To begin, please select images <a href="#image-licensing">from the gallery below</a>.</span>
					</p>
				{/if}
			</div>
		{/if}

		<!-- Documents Section -->
		<div id="documentsContainer" style="display:none;">
			<h3>Required Documents</h3>
			<p>
				Below, we have included three standard documents for you to review, sign and submit in order
				to accelerate the turnaround time of your request being processed.
			</p>
			<p>
				Submitting does not guarantee approval of your request; once submitted, we will review your
				request and get back to you as soon as possible.
			</p>
			<p>
				If you would like a custom image or rendering beyond these listed, please submit a custom
				image request instead. If you have any questions, please include them in your message below.
			</p>
			<hr />
			<!-- Price List -->
			<div class="document-section">
				<h4>Licensing rates</h4>
				<p>
					Please review the price list of licensing rates below. Prices are estimates and final
					pricing may differ.
				</p>
				<a
					href="/documents/NYBG_Welikia_FY2026_PriceList.pdf"
					target="_blank"
					class="document-link"
					download
				>
					View price list
				</a>
				<label class="checkbox-label">
					<input
						type="checkbox"
						name="priceListAcknowledged"
						bind:checked={priceListAcknowledged}
						required={selectedType === 'image-license'}
					/>
					<span
						>I have reviewed the price list. I understand that prices listed are best estimates, and
						that final prices may differ.</span
					>
				</label>
			</div>

			<hr />
			<!-- License Agreement -->
			<div class="document-section">
				<h4>Image License Agreement</h4>
				<p>Please download, sign, and upload your signed image license agreement below.</p>
				<a
					href="/documents/Image_License_(single use).pdf"
					target="_blank"
					class="document-link"
					download
				>
					Download image license agreement
				</a><br />
				<label>
					Upload signed agreement:
					<input type="file" name="signedLicenseAgreement" accept=".pdf" required={selectedType === 'image-license'} />
				</label>
			</div>

			<!-- <hr /> -->
			<!-- Data Use Agreement -->
			<!-- <div class="document-section">
				<h4>Data Use Agreement</h4>
				<p>Please download, sign, and upload your signed data use agreement below.</p>
				<a
					href="/documents/Generic_Data_Use_Agreement_NYBG.docx"
					target="_blank"
					class="document-link"
					download
				>
					Download data use agreement
				</a><br />
				<label>
					Upload signed agreement:
					<input type="file" name="signedDataUseAgreement" accept=".docx,.pdf,.doc" required />
				</label>
			</div> -->
		</div>
		<br />

		<!-- Image Modal with thumbnail strip -->
		{#if isModalOpen}
			<div
				class="modal-overlay"
				on:click={closeModal}
				on:keydown={(e) => e.key === 'Enter' && closeModal()}
				role="dialog"
				aria-modal="true"
				aria-label="Image preview"
				tabindex="-1"
			>
				<div class="modal-content modal-content-with-strip" on:click|stopPropagation role="none">
					<button type="button" class="modal-close" on:click={closeModal} aria-label="Close modal">
						<svg
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="none"
							stroke="white"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M18 6L6 18M6 6l12 12" />
						</svg>
					</button>
					<button
						type="button"
						class="modal-arrow modal-arrow-left"
						on:click|stopPropagation={() => (modalImageIndex = (modalImageIndex - 1 + images.length) % images.length)}
						aria-label="Previous image"
					>
						<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M15 18l-6-6 6-6" />
						</svg>
					</button>
					<div class="modal-main-image">
						<img
							src="/watermarked_imgs/{images[modalImageIndex].filename}"
							alt="Image {modalImageIndex + 1}"
							class="modal-image"
						/>
						<p class="modal-image-credit">© {images[modalImageIndex].artist || 'NYBG'}</p>
					</div>
					<button
						type="button"
						class="modal-arrow modal-arrow-right"
						on:click|stopPropagation={() => (modalImageIndex = (modalImageIndex + 1) % images.length)}
						aria-label="Next image"
					>
						<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M9 18l6-6-6-6" />
						</svg>
					</button>
					<div class="modal-thumb-strip" bind:this={modalThumbStripEl} role="list" aria-label="Image thumbnails">
						{#each images as image, index}
							<button
								type="button"
								class="modal-thumb"
								class:active={modalImageIndex === index}
								on:click={() => setModalImage(index)}
								aria-label="View image {index + 1}"
								aria-current={modalImageIndex === index ? 'true' : undefined}
							>
								<img
									src="/watermarked_imgs/{image.filename}"
									alt=""
									loading="lazy"
								/>
							</button>
						{/each}
					</div>
				</div>
			</div>
		{/if}

		<label>
			{messageLabel}<br />
			<textarea name="message" required></textarea>
		</label><br />
		<!-- Hidden input for selected images -->
		<input type="hidden" name="selectedImages" value={JSON.stringify(selectedImageIds)} />
		<!-- your other form fields go here -->
		<button type="submit">Submit</button>
	</form>
</div><br/><br/>

	<!-- Standalone image licensing gallery (browse only; form carousel unchanged) -->
	<section id="image-licensing" class="standalone-image-gallery" aria-labelledby="licensing-gallery-heading">
		<h2 id="licensing-gallery-heading" >Images available for licensing</h2>
		<p class="standalone-gallery-intro">Browse our available images below (click an image to view it larger). To file your image license request, please fill out the form above with the selection "Image licensing request."</p>
		<div class="slider standalone-slider">
			<button
				type="button"
				class="arrow-button arrow-left"
				on:click={previousPageGalleryImage}
				aria-label="Previous image"
			>
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--dark)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M15 18l-6-6 6-6" />
				</svg>
			</button>
			<div class="slide-container">
				<div class="slide-image-wrap">
					<img
						src="/watermarked_imgs/{images[pageGalleryIndex].filename}"
						alt="Image {pageGalleryIndex + 1}"
						on:click={openModalFromPageGallery}
						style="cursor: pointer;"
					/>
					<p class="image-credit">© {images[pageGalleryIndex].artist || 'NYBG'}</p>
				</div>
			</div>
			<button
				type="button"
				class="arrow-button arrow-right"
				on:click={nextPageGalleryImage}
				aria-label="Next image"
			>
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--dark)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M9 18l6-6-6-6" />
				</svg>
			</button>
		</div>
		<button
			type="button"
			class={isPageGalleryImageSelected ? 'unselect-image-button' : 'select-image-button'}
			on:click={togglePageGallerySelection}
		>
			{isPageGalleryImageSelected ? 'Remove from cart' : 'Add to cart'}
		</button>
		<div class="selected-images-container">
			<p>Images in your cart: {selectedImageIds.length}</p>
			<div class="selected-images-tags">
				{#each selectedImageIds as imageId}
					<button
						type="button"
						class="image-tag"
						on:click={() => removeImageFromSelection(imageId)}
						aria-label="Remove {imageId}"
					>
						<span class="tag-id">{imageId}</span>
						<span class="tag-close">×</span>
					</button>
				{/each}
			</div>
		</div>
		<button
			type="button"
			class="request-images-button"
			on:click={goToImageLicenseRequest}
		>
			Request images
		</button>
	</section>

<style>

.selected-images-prompt span a{
	color: var(--sugar-pine);
}

p {font-family: 'GT Super Regular', serif;}

.faq {
		width: 42rem;
		max-width: 90%;
		margin: 0 auto 2rem;
	}

	.faq-item {
		border-bottom: 1px solid rgba(0, 0, 0, 0.15);
	}

	.faq-item:first-child {
		border-top: 1px solid rgba(0, 0, 0, 0.15);
	}

	.faq-question {
		display: block;
		width: 100%;
		max-width: none;
		height: auto;
		margin: 0;
		overflow: visible;
		text-align: left;
		font-family: 'GT Super Bold', serif;
		font-size: 1.1rem;
		color: var(--dark);
		padding: 1rem 2rem 1rem 0;
		cursor: pointer;
		position: relative;
		background: transparent;
		border: none;
	}

	.faq-question::after {
		content: '';
		position: absolute;
		right: 0;
		top: 50%;
		transform: translateY(-50%);
		width: 0.5rem;
		height: 0.5rem;
		border-right: 2px solid currentColor;
		border-bottom: 2px solid currentColor;
		transform: translateY(-60%) rotate(45deg);
		transition: transform 0.2s ease;
	}

	.faq-item.is-open .faq-question::after {
		transform: translateY(-40%) rotate(-135deg);
	}

	.faq-answer {
		padding: 0 0 1rem 0;
	}

	.faq-answer p {
		margin: 0;
	}

	.faq-answer p :global(a) {
		/* font-weight: 800; */
		color: var(--sugar-pine);
		text-decoration: underline;
		
		position: relative;
	}

	

	.faq-answer p :global(a:hover)::after {
		width: 100%;
	}

	.standalone-image-gallery {
		width: 42rem;
		max-width: 90%;
		margin: 0 auto 3rem;
		scroll-margin-top: 5rem;
	}

	.standalone-image-gallery h2 {
		margin-bottom: 0.5rem;
	}

	.standalone-gallery-intro {
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		color: var(--dark);
		opacity: 0.9;
		margin: 0 auto 1.25rem;
	}

	.standalone-slider {
		margin: 0 auto;
	}

	.request-images-button {
		margin: 1.25rem auto 0;
		display: block;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		font-weight: 600;
		padding: 0.75rem 1.5rem;
		border: 2px solid var(--dark);
		background-color: var(--helleborous);
		color: var(--dark);
		cursor: pointer;
		transition: opacity 0.2s, filter 0.2s;
	}

	.request-images-button:hover {
		filter: brightness(1.05);
	}

	.request-images-button:active {
		opacity: 0.9;
	}

	.selected-images-summary {
		margin: 1rem 0;
		font-family: 'GT Super Regular', serif;
		color: var(--dark);
	}

	.selected-images-summary p {
		margin: 0.5rem 0;
	}

	.selected-images-prompt {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.selected-images-icon {
		flex-shrink: 0;
		width: 1.25rem;
		height: 1.25rem;
		stroke: var(--dark);
		opacity: 0.9;
	}

	.selected-images-summary a {
		color: var(--dark);
		text-decoration: underline;
	}

	.selected-images-summary a:hover {
		opacity: 0.85;
	}

	* {
		box-sizing: border-box;
	}

	form label {
		font-size: 1rem;
	}

	hr {
		color: var(--dark);
		stroke: var(--dark);
		fill: var(--dark);
		border: 1px solid var(--dark);
		margin-bottom: 1.2rem;
	}

	.mobile-warning {
		margin: 1rem 0;
		padding: 1rem;
		background-color: rgba(228, 255, 178, 0.1);
		border: 2px solid var(--dark);
		color: var(--dark);
		font-family: 'GT Super Regular', serif;
	}

	.mobile-warning p {
		margin: 0;
		line-height: 1.5;
	}

	.mobile-warning strong {
		color: var(--dark);
	}

	.data-download-message {
		margin: 1rem 0;
		padding: 1rem;
		background-color: rgba(228, 255, 178, 0.1);
		border: 2px solid var(--dark);
		color: var(--dark);
		font-family: 'GT Super Regular', serif;
	}

	.data-download-message p {
		margin: 0;
		line-height: 1.5;
	}

	.slider {
		width: 100%;
		max-width: 500px;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		position: relative;
	}

	.slide-container {
		flex: 1;
		position: relative;
		width: 100%;
		height: 300px;
		display: flex;
		justify-content: center;
		align-items: center;
		border-radius: 10px;
		overflow: hidden;
	}

	.slide-image-wrap {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.slide-container img {
		max-width: 100%;
		max-height: 100%;
		width: auto;
		height: auto;
		object-fit: contain;
	}

	.image-credit {
		font-size: 0.8rem;
		color: var(--dark);
		opacity: 0.85;
		margin: 0;
	}

	.arrow-button {
		background: var(--light);
		/* border: 1px solid var(--dark); */
		/* border-radius: 50%; */
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		padding: 0;
		transition: opacity 0.2s;
		flex-shrink: 0;
	}

	.arrow-button:hover {
		opacity: 0.8;
	}

	.arrow-button:active {
		opacity: 0.6;
	}

	.arrow-button svg {
		display: block;
	}

	.select-image-button {
		margin: 1rem auto 0;
		display: block;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		font-weight: 600;
		padding: 0.75rem 1.5rem;
		border: 2px solid var(--dark);
		background-color: var(--helleborous);
		color: var(--dark);
		cursor: pointer;
		transition: opacity 0.2s, filter 0.2s;
	}

	.select-image-button:hover {
		filter: brightness(1.05);
	}

	.unselect-image-button {
		margin: 1rem auto 0;
		display: block;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		font-weight: 600;
		padding: 0.75rem 1.5rem;
		border: 2px solid var(--dark);
		background-color: var(--dark);
		color: white;
		cursor: pointer;
		transition: opacity 0.2s, filter 0.2s;
	}

	.unselect-image-button:hover {
		filter: brightness(1.15);
	}

	.unselect-all-button {
		margin: 0.5rem auto 0;
		display: block;
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		padding: 0.5rem 1rem;
		border: 1px solid var(--dark);
		background-color: transparent;
		color: var(--dark);
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.unselect-all-button:hover {
		opacity: 0.8;
	}

	.select-image-button:active,
	.unselect-image-button:active,
	.unselect-all-button:active {
		opacity: 0.9;
	}

	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		cursor: pointer;
	}

	.modal-content {
		position: relative;
		max-width: 100vw;
		max-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: default;
	}

	.modal-content-with-strip {
		flex-direction: column;
		max-height: 100vh;
		max-width: 100vw;
		width: 100%;
		padding-bottom: 0;
		overflow: hidden;
	}

	.modal-main-image {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 0;
		padding: 3rem 1rem 6rem;
	}

	.modal-image-credit {
		color: rgba(255, 255, 255, 0.85);
		font-size: 0.9rem;
		margin: 0.5rem 0 0;
		font-family: 'GT Super Regular', serif;
	}

	.modal-image-wrap {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.modal-image {
		max-width: 100%;
		max-height: calc(100vh - 140px);
		object-fit: contain;
	}

	.modal-close {
		position: absolute;
		top: 1rem;
		right: 1rem;
		background: rgba(0, 0, 0, 0.5);
		border: 1px solid rgba(255, 255, 255, 0.5);
		border-radius: 4px;
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		padding: 0;
		transition: opacity 0.2s, background 0.2s;
		z-index: 10;
	}

	.modal-close:hover {
		opacity: 0.9;
		background: rgba(0, 0, 0, 0.7);
	}

	.modal-close svg {
		display: block;
	}

	.modal-arrow {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		background: rgba(0, 0, 0, 0.5);
		border: 1px solid rgba(255, 255, 255, 0.5);
		border-radius: 4px;
		width: 48px;
		height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		padding: 0;
		transition: opacity 0.2s, background 0.2s;
		z-index: 10;
	}

	.modal-arrow:hover {
		opacity: 0.9;
		background: rgba(0, 0, 0, 0.7);
	}

	.modal-arrow svg {
		display: block;
	}

	.modal-arrow-left {
		left: 1rem;
	}

	.modal-arrow-right {
		right: 1rem;
	}

	.modal-thumb-strip {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		z-index: 1001;
		display: flex;
		flex-wrap: nowrap;
		gap: 0.5rem;
		padding: 0.75rem 1rem 1rem;
		background: rgba(0, 0, 0, 0.6);
		overflow-x: auto;
		overflow-y: hidden;
		justify-content: flex-start;
		align-items: center;
		min-height: 80px;
		max-width: 100%;
		min-width: 0;
		-webkit-overflow-scrolling: touch;
	}

	.modal-thumb-strip::-webkit-scrollbar {
		height: 6px;
	}

	.modal-thumb-strip::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.1);
	}

	.modal-thumb-strip::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.3);
		border-radius: 3px;
	}

	.modal-thumb {
		flex: 0 0 auto;
		width: 56px;
		height: 56px;
		padding: 0;
		border: 2px solid transparent;
		background: none;
		cursor: pointer;
		overflow: hidden;
		border-radius: 4px;
		opacity: 0.7;
		transition: opacity 0.2s, border-color 0.2s;
	}

	.modal-thumb:hover {
		opacity: 1;
	}

	.modal-thumb.active {
		border-color: white;
		opacity: 1;
	}

	.modal-thumb img {
		width: 100%;
		height: 100%;
		display: block;
		object-fit: cover;
	}

	.selected-images-container {
		margin-top: 1rem;
	}

	.selected-images-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin: 0.5rem 0;
	}

	.image-tag {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem 0.5rem;
		background-color: var(--light);
		border: 1px solid var(--dark);
		color: var(--dark);
		font-family: 'GT Super Regular', serif;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.2s;
		margin: 0;
		height: auto;
		/* border-radius: 4px; */
	}

	.image-tag:hover {
		background-color: var(--dark);
		color: var(--light);
	}

	.image-tag:active {
		opacity: 0.8;
	}

	.tag-id {
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.tag-close {
		font-size: 1.2rem;
		line-height: 1;
		font-weight: bold;
	}

	form {
		margin: auto;
		max-width: 500px;
		color: var(--dark);
	}

	.honeypot-field {
		position: absolute;
		left: -9999px;
		width: 1px;
		height: 1px;
		overflow: hidden;
		opacity: 0;
		pointer-events: none;
	}

	.honeypot-field input {
		position: absolute;
		left: -9999px;
	}

	#documentsContainer {
		margin: 2rem 0;
		padding: 1.5rem;
		border: 1px solid var(--dark);
		/* border-radius: 4px; */
	}

	#documentsContainer h3 {
		margin-top: 0;
		color: var(--dark);
		font-family: 'GT Super Regular', serif;
	}

	#documentsContainer h4 {
		margin-top: 1.5rem;
		margin-bottom: 0.5rem;
		color: var(--dark);
		font-family: 'GT Super Regular', serif;
		font-size: 1.1rem;
	}

	#documentsContainer h4:first-of-type {
		margin-top: 0;
	}

	.document-section:last-child {
		margin-bottom: 0;
	}

	.document-link {
		display: inline-block;
		margin: 0rem 0 1rem;
		/* padding: 0.5rem 1rem; */
		/* background-color: var(--dark);
		border: 1px solid var(--dark); */
		color: var(--dark);
		text-decoration: none;
		/* border-radius: 4px; */
		transition: all 0.2s;
	}

	.document-link:hover {
		background-color: var(--helleborous);
		color: var(--dark);
	}

	.checkbox-label {
		display: flex;
		align-items: flex-start;
		gap: 0.5rem;
		margin: 1rem 0;
		cursor: pointer;
	}

	.checkbox-label input[type='checkbox'] {
		margin: 0;
		width: auto;
		height: auto;
		flex-shrink: 0;
		margin-top: 0.2rem;
		cursor: pointer;
	}

	.checkbox-label span {
		flex: 1;
		line-height: 1.2;
	}

	input[type='file'] {
		margin: 0.8rem 0rem;
		vertical-align: middle;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		padding: 0.5rem;
		/* border: 1px solid white; */
		border: none;
		background-color: #0000001a;
		width: 100%;
		color: var(--dark);
		cursor: pointer;
		height: auto;
	}

	input[type='file']::file-selector-button {
		/* font-family: 'GT Super Regular', serif; */
		/* padding: 0.5rem 1rem; */
		/* border: 1px solid var(--dark); */
		/* background-color: var(--dark); */
		/* color: var(--dark); */
		cursor: pointer;
		/* margin-right: 1rem; */
		/* border-radius: 4px; */
		transition: all 0.2s;
	}

	input[type='file']::file-selector-button:hover {
		background-color: var(--dark);
		color: var(--light);
	}
	select,
	input {
		margin: 0.8rem 0rem;
		vertical-align: middle;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		padding: 0.5rem;
		border: 1px solid var(--dark);
		/* border-radius: 0.25rem; */
		background-color: white;
		/* color: #e4ffb2; */
		width: 100%;
		/* max-width: 250px; */
		height: 38px;
		overflow: hidden;
		color: var(--dark);
	}

	textarea {
		margin: 0.8rem 0;
		vertical-align: middle;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		padding: 0.5rem;
		border: 1px solid var(--dark);
		/* border-radius: 0.25rem; */
		background-color:white;
		/* color: #e4ffb2; */
		width: 100%;
		/* max-width: 400px; */
		height: 150px;
		overflow: hidden;
		color: var(--dark);
	}

	option {
		background-color: var(--light);
	}

	button {
		margin: 1rem 0.4rem;
		vertical-align: middle;
		font-family: 'GT Super Regular', serif;
		font-size: 1rem;
		/* padding: 0.5rem; */
		border: 1px solid black;
		/* border-radius: 0.25rem; */
		background-color: #0000001a;
		/* color: #e4ffb2; */
		/* width: 100%; */
		max-width: 250px;
		height: 50px;
		overflow: hidden;
	}
	strong {
		color: #e4ffb2;
	}

	.rest-content {
		opacity: 0;
	}

	.content-body {
		position: relative;
		width: 80%;
		margin: auto;
		color: var(--dark);
		margin-top: 2rem;
		font-size: 1.1rem;
		font-family: 'GT Super Regular', serif;
	}

	h1 {
		text-align: center;
		/* opacity: 0 */
	}

	h2 {
		font-family: 'NY Botanical Gothic', 'serif';
		text-align: center;
		/* opacity: 0 */
	}

	#contact-form.contact-heading {
		scroll-margin-top: 5rem;
	}

	@media (min-width: 768px) {
		.content-body {
			position: relative;
			width: 60%;
			margin: auto;
			color: var(--dark);
			margin-top: 2rem;
			font-size: 1.1rem;
			font-family: 'GT Super Regular', serif;
		}
	}

	@media (min-width: 968px) {
		.content-body {
			position: relative;
			width: 40%;
			margin: auto;
			color: var(--dark);
			margin-top: 2rem;
			font-size: 1.1rem;
			font-family: 'GT Super Regular', serif;
		}
	}
</style>
