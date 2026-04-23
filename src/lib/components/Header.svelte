<script lang="ts">
    import { page } from '$app/stores';

    const pageTitles: Record<string, string> = {
        '/': 'Urban Conservation Hub',
        '/about': 'About the Team',
        '/research': 'Tools & Research',
        '/education': 'Education',
        '/contact': 'Contact',
        '/press': 'Press',
    };

    const pageColors: Record<string, string> = {
        '/about': '#FEC3F9',
        '/research': '#B1F6FF',
        '/education': '#FFE694',
        '/contact': 'var(--helleborous)',
        '/press': '#FF956E',
        '/': 'var(--helleborous)',
    };

    const pageTaglines: Record<string, string> = {
        '/about': 'Founded in 2023, the NYBG Urban Conservation program believes that cities are an important part of the solution to our environmental crises, with enormous capacity to simultaneously improve human lives and minimize human impact on the environment.',
        '/research': "Our team draws on research in historical ecology to support scientific and public platforms, partnerships, and books for helping New Yorkers reimagine the city and adapt to a changing climate.",
        '/education': 'Explore educational resources and teaching modules for utilizing our tools and research in the classroom and beyond.',
        '/contact': 'Get in touch with our team with general inquiries, image licensing requests, press inquiries, and more by filling out the form below.',
        '/press': 'A selection of articles and media coverage of our work to date. For press inquiries, please reach out through our contact form.',
        '/': 'Explore our work'
    };

    $: title = pageTitles[$page.url.pathname] || '';
    $: color = pageColors[$page.url.pathname] || 'var(--helleborous)';
    $: tagline = pageTaglines[$page.url.pathname] || '';
</script>

{#if title !== ''}
<div class="header">
    <h1 class="header-title" style="--outline-color: {color};">{title}</h1>
    {#if tagline}
        <div class="header-tagline-wrap">
            <span class="header-accent" style="background-color: {color};"></span>
            <p class="header-tagline">{tagline}</p>
        </div>
    {/if}
</div>
{/if}

<style>
    .header {
        display: grid;
        grid-template-columns: minmax(200px, 420px) minmax(200px, 380px);
        gap: 4rem;
        align-items: end;
        justify-content: center;
        justify-items: start;
        padding: 3.5rem 20px 4rem;
        width: fit-content;
        max-width: min(1200px, 100%);
        margin: 0 auto;
    }

    .header-title {
        font-family: 'NY Botanical Gothic', serif;
        font-size: 3.75rem;
        margin: 0;
        color: black;
        -webkit-text-stroke: 2px var(--outline-color);
        letter-spacing: 0.02em;
        line-height: 1.15;
        max-width: 420px;
    }

    .header-tagline-wrap {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        max-width: 380px;
    }

    .header-accent {
        display: block;
        width: 2.5rem;
        height: 2px;
        flex-shrink: 0;
    }

    .header-tagline {
        font-family: 'GT Super Regular', serif;
        font-size: 0.95rem;
        color: white;
        margin: 0;
        text-align: left;
        line-height: 1.5;
    }

    @media (max-width: 768px) {
        .header {
            grid-template-columns: 1fr;
            width: 100%;
            gap: 1.25rem;
            padding: 2rem 15px 2.25rem;
        }

        .header-title {
            font-size: 2.25rem;
        }

        .header-tagline-wrap {
            max-width: 100%;
        }

        .header-tagline {
            font-size: 0.9rem;
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
