<script lang="ts">
	import { page } from '$app/stores';
	import { claimResearchApplicationInvite } from '$lib/api/researchApplicationInvites';
	import { djangoAdminHomeUrl } from '$lib/api/djangoAdmin';

	$: token = $page.params.token || '';

	let username = '';
	let password = '';
	let passwordConfirm = '';
	let submitting = false;
	let errorMessage = '';
	let success: { username: string; adminLoginUrl: string; detail: string } | null = null;

	function formatApiErrors(body: unknown): string {
		if (!body || typeof body !== 'object') {
			return 'Could not create your account. Please try again.';
		}
		const record = body as Record<string, unknown>;
		if (typeof record.detail === 'string') {
			return record.detail;
		}
		if (Array.isArray(record.detail)) {
			return record.detail.map(String).join(' ');
		}
		const parts: string[] = [];
		for (const [key, value] of Object.entries(record)) {
			const text = Array.isArray(value) ? value.map(String).join(' ') : String(value);
			parts.push(key === 'detail' ? text : `${key}: ${text}`);
		}
		return parts.length ? parts.join(' ') : 'Please correct the form and try again.';
	}

	async function handleSubmit(event: Event) {
		event.preventDefault();
		errorMessage = '';
		if (!token) {
			errorMessage = 'Missing invite token. Use the link from your approval email.';
			return;
		}
		if (password !== passwordConfirm) {
			errorMessage = 'Passwords do not match.';
			return;
		}
		submitting = true;
		try {
			const result = await claimResearchApplicationInvite({
				token,
				username: username.trim(),
				password,
				password_confirm: passwordConfirm
			});
			success = {
				username: result.username,
				adminLoginUrl: result.admin_login_url || djangoAdminHomeUrl(),
				detail: result.detail
			};
		} catch (err) {
			const body = err && typeof err === 'object' && 'body' in err ? (err as { body: unknown }).body : null;
			errorMessage = formatApiErrors(body);
		} finally {
			submitting = false;
		}
	}
</script>

<section class="claim-page">
	<header class="page-header">
		<p class="eyebrow"><a href="/research">Research</a> / Create account</p>
		<h1 class="page-title">Create your research portal account</h1>
		<p class="lede">
			Choose a username and password. Your approved project will be created automatically. Sign in
			with your <strong>username</strong> (not email) at Django admin.
		</p>
	</header>

	{#if success}
		<div class="success-panel" role="status">
			<h2 class="section-heading">Account ready</h2>
			<p>{success.detail}</p>
			<p>Username: <strong>{success.username}</strong></p>
			<p>
				<a class="submit-button" href={success.adminLoginUrl}>Open Django admin login</a>
			</p>
			<p><a href="/research">Return to Research</a></p>
		</div>
	{:else}
		<form class="claim-form" on:submit={handleSubmit}>
			{#if errorMessage}
				<p class="form-error" role="alert">{errorMessage}</p>
			{/if}

			<section class="form-section">
				<div class="grid">
					<label class="full">
						<span>Username *</span>
						<input required autocomplete="username" bind:value={username} />
					</label>
					<label>
						<span>Password *</span>
						<input type="password" required autocomplete="new-password" bind:value={password} />
					</label>
					<label>
						<span>Confirm password *</span>
						<input
							type="password"
							required
							autocomplete="new-password"
							bind:value={passwordConfirm}
						/>
					</label>
				</div>
			</section>

			<div class="actions">
				<button type="submit" class="submit-button" disabled={submitting || !token}>
					{submitting ? 'Creating…' : 'Create account'}
				</button>
				<a class="back-link" href="/research">Cancel</a>
			</div>
		</form>
	{/if}
</section>

<style>
	.claim-page {
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

	input {
		font: inherit;
		padding: 0.55rem 0.65rem;
		border: 1px solid rgba(30, 47, 30, 0.35);
		background: #fff;
		color: #111;
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
		text-decoration: none;
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

	.back-link {
		font-family: 'GT Super Regular', serif;
		color: #1e2f1e;
	}

	.success-panel {
		padding: 1.5rem 1.35rem;
		border: 1px solid rgba(30, 47, 30, 0.25);
		background: rgba(200, 181, 0, 0.1);
		font-family: 'GT Super Regular', serif;
		line-height: 1.55;
	}

	.success-panel .submit-button {
		margin: 0.5rem 0;
	}

	@media (max-width: 640px) {
		.grid {
			grid-template-columns: 1fr;
		}
	}
</style>
