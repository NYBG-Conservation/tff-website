<script lang="ts">
    import Card from '$lib/components/Card.svelte';
    import type { Project, Tag } from '$lib/types/project';
    import { tagColors } from '$lib/types/project';
    import { fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    import bluezones from '$lib/assets/project-photos/blue-zones-opengraph.jpeg';
    import bny from '$lib/assets/project-photos/bny-thumb.png';
    import bxrw from '$lib/assets/project-photos/bxrw-thumb.png';
    import lotp from '$lib/assets/project-photos/lotp-thumb.png';
    import cloudburst from '$lib/assets/project-photos/cloudburst-thumb.png';
    import mannahatta from '$lib/assets/project-photos/mannahatta-thumb.png';
    import visionmaker from '$lib/assets/project-photos/visionmaker-thumb.png';
    import welikia from '$lib/assets/project-photos/welikia-thumb.png';

    const modes: Tag[] = ['Digital tool', 'Book', 'Partnership'];
    const themes: Tag[] = ['Historical ecology', 'Environmental governance', 'Ecological democracy', 'Active restoration'];

    let selectedFilters = $state<Set<Tag>>(new Set());

    function toggleFilter(tag: Tag) {
        const newSet = new Set(selectedFilters);
        if (newSet.has(tag)) {
            newSet.delete(tag);
        } else {
            newSet.add(tag);
        }
        selectedFilters = newSet;
    }

    function matchesFilters(project: Project): boolean {
        if (selectedFilters.size === 0) return true;
        
        // Project must have ALL selected tags (AND logic)
        return Array.from(selectedFilters).every(tag => project.tags.includes(tag));
    }

    const projects: Project[] = [
        {
            imgurl: bluezones,
            title: 'Blue Zones of New York City',
            desc: 'An ongoing environmental analysis of where the city used to flood, continues to flood today, and is projected to flood in the future.',
            tags: ['Digital tool', 'Historical ecology', "Environmental governance"],
            link: '/blue-zones'
        },
        {
            imgurl: welikia,
            title: 'The Welikia Project & Map Explorer',
            desc: "Explore the block-by-block historical landscape of New York City, as it was 400 years ago.",
            tags: ['Digital tool', 'Historical ecology'],
            link: 'https://www.welikia.org/'
        },
        {
            imgurl: bny,
            title: 'Before New York: An Atlas and Gazetteer',
            desc: "A book about the historical placenames of New York City, forthcoming in Fall 2026 from Abrams.",
            tags: ['Book', 'Historical ecology'],
            link: 'https://www.abramsbooks.com/product/before-new-york_9781419760051/'
        },
        {
            imgurl: bxrw,
            title: 'Bronx River Watershed Restoration',
            desc: "Working with local government, non-profit, and academic partners to increase the biodiversity and resilience of the Bronx River watershed.",
            tags: ['Active restoration', 'Partnership'],
            link: 'https://www.nybg.org/about/sustainability/protect-restore/bronx-river-watershed-health-and-resilience/'
        },
        {
            imgurl: lotp,
            title: 'Layers of the Past',
            desc: "View, search and filter the nearly 200 historical maps that underlie The Welikia Project.",
            tags: ['Digital tool', 'Historical ecology'],
            link: 'https://www.layersofthepast.org/'
        },
        {
            imgurl: mannahatta,
            title: 'Mannahatta: A Natural History of New York City',
            desc: "A book reconstructing the ecological history of Manhattan through period maps, archeological discoveries, and computational geography to create pictures and descriptions of Manhattan from 1609 to the present day.",
            tags: ['Book', 'Historical ecology'],
            link: 'https://store.abramsbooks.com/products/mannahatta'
        },
        {
            imgurl: cloudburst,
            title: 'Cloudburst Management',
            desc: "Working with the NYC Department of Environmental Protection to increase NYC's flood resilience.",
            tags: ['Partnership', 'Environmental governance']
        },
        {
            imgurl: visionmaker,
            title: 'Visionmaker NYC',
            desc: "Envisioning a more biodiverse, resilient city through a digital planning platform.",
            tags: ['Digital tool', 'Ecological democracy'],
            imageBackground: '#E9F8FF',
            link: 'https://visionmaker.us/nyc/'
        },




    ];

    let filteredProjects = $derived(projects.filter(matchesFilters));
</script>

<p class="filter-instructions">FILTER BY: </p>
<div class="filter-section">
    <div class="filter-category">
        <h3 class="filter-category-title">MODES</h3>
        <div class="filter-tags">
            {#each modes as tag}
                <button 
                    type="button"
                    class="filter-tag" 
                    class:active={selectedFilters.has(tag)}
                    style="background-color: {selectedFilters.has(tag) ? tagColors[tag] : 'transparent'}"
                    onclick={() => toggleFilter(tag)}
                >
                    {tag}
                </button>
            {/each}
        </div>
    </div>
    
    <div class="filter-category">
        <h3 class="filter-category-title">THEMES</h3>
        <div class="filter-tags">
            {#each themes as tag}
                <button 
                    type="button"
                    class="filter-tag" 
                    class:active={selectedFilters.has(tag)}
                    style="background-color: {selectedFilters.has(tag) ? tagColors[tag] : 'transparent'}"
                    onclick={() => toggleFilter(tag)}
                >
                    {tag}
                </button>
            {/each}
        </div>
    </div>
</div>

<div class="projects-container">
    {#each filteredProjects as project (project.title)}
        <div transition:fly={{ y: 20, duration: 300, easing: quintOut }}>
            <Card {project} />
        </div>
    {/each}
</div>

<style>
    .filter-instructions {
        font-family: 'Martian Mono';
        font-size: .8rem;
        font-weight: 600;
        color: #000;
        text-align: left;
        width: 90%;
        max-width: 1000px;
        margin: 2rem auto 0.75rem auto;
    }
    .filter-section {
        width: 90%;
        max-width: 1000px;
        margin: 0rem auto;
        padding: 1rem 0;
        border-bottom: 1px solid #ddd;
        display: flex;
        gap: 3rem;
        align-items: flex-start;
    }

    .filter-category {
        flex: 1;
    }

    .filter-category-title {
        font-family: 'Martian Mono';
        font-size: .8rem;
        font-weight: 600;
        margin: 0 0 0.75rem 0;
        color: #000;
    }

    .filter-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }

    .filter-tag {
        display: flex;
        height: 2rem;
        padding: 0rem 0.7075rem;
        justify-content: center;
        align-items: center;
        border-radius: 12.5rem;
        font-size: 0.8rem;
        font-family: 'Martian Mono';
        letter-spacing: -.05em;
        border: 1px solid #ccc;
        background-color: transparent;
        color: #000;
        cursor: pointer;
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    .filter-tag:hover {
        border-color: #999;
    }

    .filter-tag:not(.active):hover {
        background-color: #f2f2f2;
    }

    .filter-tag.active:hover {
        filter: brightness(0.96);
    }

    .projects-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
        gap: 2rem;
        width: 90%;
        max-width: 1000px;
        margin: 2rem auto;
    }

    .projects-container > div {
        transition: opacity 0.2s ease;
    }

    /* Tablet styles */
    @media (max-width: 768px) {
        .filter-section {
            width: 95%;
            padding: 1rem;
            gap: 2rem;
        }

        .projects-container {
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
            width: 95%;
        }
    }

    /* Mobile styles */
    @media (max-width: 480px) {
        .filter-section {
            width: 100%;
            padding: 1rem;
            flex-direction: column;
            gap: 1.5rem;
        }

        .filter-category {
            width: 100%;
        }

        .filter-tags {
            gap: 0.5rem;
        }

        .filter-tag {
            font-size: 0.75rem;
            height: 1.8rem;
            padding: 0rem 0.6rem;
        }

        .projects-container {
            grid-template-columns: 1fr;
            gap: 1.5rem;
            width: 100%;
            padding: 0 1rem;
        }
    }
</style>