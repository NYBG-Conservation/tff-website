<script lang="ts">
	import '../styles/all.css';
	import { page } from '$app/stores';

	$: status = $page.status;
	$: message = $page.error?.message;
</script>

<div class="error-page">
	<h1>This page does not exist!</h1>
	{#if status === 404}
		<p class="error-message">The page you're looking for couldn't be found.</p>
	{:else if message}
		<p class="error-message">{message}</p>
	{/if}
	<p class="error-link"><a href="/">Return to home</a></p>
</div>

<style>
	.error-page {
		min-height: 60vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		padding: 2rem;
		background-color: var(--bg-light);
	}

	.error-page h1 {
		font-family: 'NY Botanical Gothic', serif;
		font-size: 3rem;
		color: var(--dark);
		margin: 0 0 1rem;
	}

	.error-message {
		font-family: 'GT Super Regular', serif;
		font-size: 1.25rem;
		color: var(--dark);
		margin: 0 0 1.5rem;
		max-width: 28rem;
	}

	.error-link {
		margin: 0;
	}

	.error-link a {
		font-family: 'GT Super Regular', serif;
		font-size: 1.1rem;
		color: black;
		border: 2px solid black;
		/* background-color: var(--dark); */
		padding: 0.5rem 1rem;
		text-decoration: none;
		/* border-radius: 4px; */
	}

	.error-link a:hover {
		/* text-decoration: underline; */
		background-color: black;
		color: var(--helleborous);
	}

	@media (max-width: 768px) {
		.error-page h1 {
			font-size: 2.25rem;
		}
		.error-message {
			font-size: 1.1rem;
		}
	}
</style>
