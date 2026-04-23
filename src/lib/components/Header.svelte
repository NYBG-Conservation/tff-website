<script lang="ts">
    import { page } from '$app/stores';

    const pageTitles: Record<string, string> = {
        '/': 'Urban Conservation Hub',
        '/about': 'About the Forest',
        '/research': 'Ongoing research',
        '/visit': 'Visit the Forest',
        '/education': 'Education',
        '/data': 'Data & Archives',
        '/contact': 'Contact'
    };

    $: title = pageTitles[$page.url.pathname] || '';
</script>

{#if title !== ''}
<div class="header">
    <h1 class="header-title">{title}</h1>
</div>
{/if}

<style>
    .header {
        display: flex;
        justify-content: center;
        text-align: center;
        padding: 2.75rem 20px 3rem;
        max-width: min(1200px, 100%);
        margin: 0 auto;
    }

    .header-title {
        font-family: 'NY Botanical Gothic', serif;
        font-size: clamp(2rem, 5vw, 3.5rem);
        margin: 0;
        color: #111;
        letter-spacing: 0.02em;
        line-height: 1.15;
    }

    @media (max-width: 768px) {
        .header {
            padding: 2rem 15px 2.25rem;
        }
    }

    @media (max-width: 480px) {
        .header {
            padding: 1.5rem 15px 2rem;
        }

        .header-title {
            font-size: 1.85rem;
        }
    }
</style>
