from django.core.management.base import BaseCommand

from apps.datasets.models import ProjectPublication

SELECTED_PUBLICATIONS: list[dict] = [
    {
        "publication_year": 2014,
        "sort_order": 140,
        "citation": (
            "Atha, D., J.A. Schuler, S.L. Tobing. 2014. Corydalis incisa (Fumariaceae) in Bronx and "
            "Westchester Counties, New York. <em>Phytoneuron</em> 96: 1-6."
        ),
        "url": "https://www.nybg.org/files/forest/Athaetal2014Corydalisincisa.pdf",
    },
    {
        "publication_year": 2014,
        "sort_order": 130,
        "citation": (
            "Munshi-South, J. and C. Nagy. 2014. Urban park characteristics, genetic variation, and "
            "historical demography of white-footed mouse (<em>Peromyscus leucopus</em>) populations in New "
            "York City. <em>PeerJ</em> 2:e310; DOI 10.7717/peerj.310."
        ),
        "doi": "10.7717/peerj.310",
        "url": "https://peerj.com/articles/310/",
    },
    {
        "publication_year": 2007,
        "sort_order": 120,
        "citation": (
            "Rachlin J.W., B.E. Warkentine, A. Pappantoniou. 2007. An Evaluation of the Ichthyofauna of the "
            "Bronx River, a Resilient Urban Waterway. <em>Northeastern Naturalist</em> 14(4):531-544."
        ),
        "url": "https://www.nybg.org/files/forest/Rachlin-2007-Ichthyofauna-Bronx-River.pdf",
    },
    {
        "publication_year": 2003,
        "sort_order": 110,
        "citation": (
            "Gregg, J. W., C.G. Jones, and T.E. Dawson. 2003. Urbanization on Tree Growth in the Vicinity of "
            "New York City. <em>Nature</em> 424:183-187."
        ),
        "url": "https://www.nybg.org/files/forest/Gregg-et-al-Nature-2003.pdf",
    },
    {
        "publication_year": 1997,
        "sort_order": 100,
        "citation": (
            "McDonnell, M.J., S.T.A. Pickett, P. Groffman, P. Bohlen, R. Pouyat, W.C. Zipperer, and R.W. "
            "Parmelee. 1997. Ecosystem Processes along an urban-to-rural gradient. <em>Urban Ecosystems</em> "
            "1: 21-36."
        ),
        "url": "https://www.nybg.org/files/forest/mcdonnell-etal-ecosys-urban-rural-gradient1997.pdf",
    },
    {
        "publication_year": 1990,
        "sort_order": 90,
        "citation": (
            "McDonnell, M.J. and S.T.A. Pickett. 1990. Ecosystem Structure and Function along Urban-Rural "
            "Gradients: An Unexploited Opportunity for Ecology. <em>Ecology</em> 71(4): 1232-1237."
        ),
        "url": "https://www.nybg.org/files/forest/mcdonnell-pickett-urban-rural-gradient.pdf",
    },
    {
        "publication_year": 1989,
        "sort_order": 80,
        "citation": (
            "Rudnicky, J.L. and M. J. McDonnell. 1989. Forty-Eight Years of Canopy Change in a "
            "Hardwood-Hemlock Forest in New York City. <em>Bulletin of the Torrey Botanical Club</em> "
            "116(1): 52-64."
        ),
        "url": "https://www.nybg.org/files/forest/Rudnicky-McDonnell-1989-Torreya.pdf",
    },
    {
        "publication_year": 1988,
        "sort_order": 70,
        "citation": (
            "White, C.S. and M.J. McDonnell. 1988. Nitrogen Cycling Processes and Soil Characteristics in an "
            "Urban versus Rural Forest. <em>Biogeochemistry</em> 5(2): 243-262."
        ),
        "url": "https://www.nybg.org/files/forest/McDonnell-White-1988-Biogeochemistry.pdf",
    },
    {
        "publication_year": 1987,
        "sort_order": 60,
        "citation": (
            "Leonardi L. 1987. The Bryophytes of The New York Botanical Garden Forest. <em>Evansia</em> 4: 8-11."
        ),
        "url": "https://www.nybg.org/files/forest/Leonardi-1987-Evansia.pdf",
    },
    {
        "publication_year": 1980,
        "sort_order": 50,
        "citation": (
            "Honkala, D.A. and J.B. McAninch. 1980. The New York Botanical Garden Hemlock Forest Project Part "
            "I. NYBG Institutional Report."
        ),
        "url": "https://www.nybg.org/files/forest/HonkalaNYBGHemlockForestProject1.pdf",
    },
    {
        "publication_year": 1981,
        "sort_order": 40,
        "citation": (
            "Honkala, D.A. and J.B. McAninch. 1981. The New York Botanical Garden Hemlock Forest Project Part "
            "II. NYBG Institutional Report."
        ),
        "url": "https://www.nybg.org/files/forest/HonkalaNYBGHemlockForestProject2.pdf",
    },
    {
        "publication_year": 1924,
        "sort_order": 30,
        "citation": (
            "Moore, B., H.M. Richards, H.A. Gleason, and A.B. Stout. 1924. Hemlock and its environment. "
            "<em>Bulletin of The New York Botanical Garden</em> 12(45):325-350."
        ),
        "url": "https://www.nybg.org/files/forest/GleasonHemlockanditsEnvironment.pdf",
    },
    {
        "publication_year": 1906,
        "sort_order": 20,
        "citation": (
            "Britton, N.L. 1906. The Hemlock Grove on the banks of the Bronx River and what it signifies. "
            "<em>Contributions from The New York Botanical Garden</em> 88:5-13."
        ),
        "url": "https://www.nybg.org/files/forest/BrittonThehemlockgrove....pdf",
    },
    {
        "publication_year": 1899,
        "sort_order": 10,
        "citation": (
            "Howe, M.A. and E.G. Britton. 1899. Lists of Plants in the Grounds, 1898. "
            "<em>Bulletin of The New York Botanical Garden</em> 1(4): 195-203."
        ),
        "url": "https://www.nybg.org/files/forest/Bulletin1899-FloristicSurvey.pdf",
    },
]


class Command(BaseCommand):
    help = "Seed the Selected Publications list for /research (site-wide, not tied to a project)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update citation and metadata on existing rows matched by citation text.",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Set featured and expose_on_public_api on seeded rows.",
        )

    def handle(self, *args, **options):
        update = options["update"]
        publish = options["publish"]
        created = 0
        updated = 0

        for payload in SELECTED_PUBLICATIONS:
            citation = payload["citation"]
            defaults = {
                **payload,
                "project": None,
                "featured": publish or payload.get("featured", False),
                "expose_on_public_api": publish or payload.get("expose_on_public_api", False),
            }
            existing = ProjectPublication.objects.filter(project__isnull=True, citation=citation).first()
            if existing:
                if update or publish:
                    for field, value in defaults.items():
                        setattr(existing, field, value)
                    existing.save()
                    updated += 1
                continue

            ProjectPublication.objects.create(**defaults)
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded research publications: {created} created, {updated} updated "
                f"({'published' if publish else 'draft'})"
            )
        )
