<script lang="ts">
    import type { Project } from '$lib/types/project';
    import { tagColors } from '$lib/types/project';

    interface Props {
        project: Project;
    }

    let { project }: Props = $props();
</script>

{#if project.link}
    <a href={project.link} target="_blank" rel="noopener noreferrer" class="card">
        <div class="card-image-wrap" style={project.imageBackground ? `background-color: ${project.imageBackground}` : ''}>
            <img src={project.imgurl} alt={project.title} class="card-image" />
        </div>
        <div class="card-content">
            <h3 class="card-title">{project.title}</h3>
            <p class="card-desc">{project.desc}</p>
            <span class="card-link">View project <span class="arrow">→</span></span>
            <div class="card-tags">
                {#each project.tags as tag}
                    <span class="tag" style="background-color: {tagColors[tag]}">{tag}</span>
                {/each}
            </div>
        </div>
    </a>
{:else}
    <div class="card">
        <div class="card-image-wrap" style={project.imageBackground ? `background-color: ${project.imageBackground}` : ''}>
            <img src={project.imgurl} alt={project.title} class="card-image" />
        </div>
        <div class="card-content">
            <h3 class="card-title">{project.title}</h3>
            <p class="card-desc">{project.desc}</p>
            <div class="card-tags">
                {#each project.tags as tag}
                    <span class="tag" style="background-color: {tagColors[tag]}">{tag}</span>
                {/each}
            </div>
        </div>
    </div>
{/if}

<style>
    .card {
        display: flex;
        flex-direction: column;
        overflow: hidden;
        background-color: white;
        padding: 1rem;
        height: 100%;
        border: 1px solid #ccc;
    }

    a.card {
        text-decoration: none;
        color: inherit;
        cursor: pointer;
    }

    .card-image-wrap {
        width: 100%;
        overflow: hidden;
        padding: 0;
    }

    .card-image {
        width: 100%;
        height: auto;
        display: block;
    }

    .card-content {
        /* padding: 1rem; */
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }

    .card-title {
        margin: 0 0 0.75rem 0;
        font-size: 1.25rem;
        font-weight: 700;
        font-family: 'GT Super Regular';
        line-height: 1.2;
    }

    .card-desc {
        margin: 0 0 0.5rem 0;
        line-height: 1.3;
        font-family: 'GT Super Regular';
        flex-grow: 1;
        font-size: 1rem;
    }

    .card-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: auto;
    }

    .card-link {
        display: inline-flex;
        align-items: center;
        align-self: flex-end;
        margin-top: 0.25rem;
        margin-bottom: 0.75rem;
        color: var(--dark);
        text-decoration: none;
        font-family: 'GT Super Regular', serif;
        font-weight: 600;
        position: relative;
        padding-bottom: 4px;
        transition: color 0.2s ease;
        width: fit-content;
        gap: 0.25rem;
    }

    .card-link .arrow {
        display: inline-block;
        transition: transform 0.2s ease;
    }

    .card:hover .card-link .arrow {
        transform: translateX(2px);
    }

    .card-link::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 0;
        height: 2px;
        background-color: var(--dark);
        transition: width 0.2s ease;
    }

    .card:hover .card-link::after {
        width: 100%;
    }

    .tag {
        display: flex;
        height: 1.8rem;
        padding: 0rem 0.7075rem;
        justify-content: center;
        align-items: center;
        gap: 0.625rem;
        border-radius: 12.5rem;
        font-size: 0.7rem;
        font-family: 'Martian Mono';
        letter-spacing: -.05em;
        border: 1px solid #ccc;
        transition: border-color 0.2s ease, filter 0.2s ease;
    }

    .tag:hover {
        border-color: #999;
        filter: brightness(1.06);
    }
</style>

