<script lang="ts">
    import annieHeadshot from '$lib/assets/profile-photos/annie-headshot.png';
    import ericHeadshot from '$lib/assets/profile-photos/eric-headshot.png';
    import genesisHeadshot from '$lib/assets/profile-photos/genesis-headshot.png';
    import jesseHeadshot from '$lib/assets/profile-photos/jesse-headshot.png';
    import lucyHeadshot from '$lib/assets/profile-photos/lucy-headshot.png';

    interface Profile {
        name: string;
        image: string;
        role?: string;
        email?: string;
    }

    const profiles: Profile[] = [
        {
            name: 'Dr. Eric Sanderson',
            image: ericHeadshot,
            role: 'Vice President for Urban Conservation',
            email: 'ewsanderson@nybg.org'
        },
        {
            name: 'Jesse Moy',
            image: jesseHeadshot,
            role: 'Landscape Visualization Artist & Designer',
            email: 'jmoy@nybg.org'
        },
        {
            name: 'Annie Fu',
            image: annieHeadshot,
            role: 'Geospatial Developer & Systems Administrator',
            email: 'afu@nybg.org'
        },
        {
            name: 'Lucinda Royte',
            image: lucyHeadshot,
            role: 'Manager of Urban Conservation Data, Tools & Outreach',
            email: 'lroyte@nybg.org'
        },
        {
            name: 'Génesis Abreu',
            image: genesisHeadshot,
            role: 'Director of Urban Conservation Partnerships',
            email: 'gabreu@nybg.org'
        }
    ];
</script>

<div class="profile-container">

    {#each profiles as profile}
        <div class="profile">
            <img class="profile-image" src={profile.image} alt={profile.name} />
            <strong>{profile.name}</strong>
            <span>{profile.role}</span>
            <span><a href={`mailto:${profile.email}`}>{profile.email}</a></span>
        </div>
    {/each}
</div>

<style>
    .profile-image{
        width: 100%;
        margin-bottom: 8px;
    }

    .profile-container {
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 1.5rem;
        width: 90%;
        max-width: 1000px;
        margin: 4rem auto;
        flex-wrap: wrap;
    }

    .profile {
        width: 170px;
        display: flex;
        flex-direction: column;
        justify-content: left;
        text-align: left;
        font-family: 'GT Super Regular';
    }
    .profile span{
        margin: .8em 0;
        line-height: 1.1;
    }

    .profile span a{
        color: var(--sugar-pine);
        /* text-decoration: none; */
    }

    /* Tablet styles */
    @media (max-width: 1024px) {
        .profile-container {
            gap: 1.2rem;
            width: 95%;
        }
        .profile {
            width: calc(33.333% - 1rem);
            min-width: 150px;
        }
    }

    /* Mobile styles */
    @media (max-width: 768px) {
        .profile-container {
            gap: 1rem;
            width: 100%;
            padding: 0 1rem;
        }
        .profile {
            width: calc(50% - 0.5rem);
            min-width: 120px;
            max-width: 150px;
        }
    }

    /* Small mobile styles */
    @media (max-width: 480px) {
        .profile-container {
            flex-direction: column;
            align-items: center;
            gap: 2rem;
        }
        .profile {
            width: 100%;
            max-width: 180px;
        }
    }
</style>