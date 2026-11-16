#!/usr/bin/env python3
# Generates _publications/*.md from the verified table below.
#
# NOTE: this rewrites the whole collection and will overwrite hand edits to
# front matter. It was used once to migrate the site to grouped publications;
# afterwards the .md files are the source of truth. Run from the repo root.
# Run from the repo root:  python make_publications.py
import json, os, re, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBDIR = os.path.join(ROOT, "_publications")

# slug, date, title, authors_short, authors_cite, journal, tail, doi, groups, permalink
P = [
    # ---------------- river birds ----------------
    ("conserving-world-specialist-riverine-birds", "2026-06-27",
     "Conserving the World's Specialist Riverine Birds",
     "Sinha, Chatterjee & Ormerod",
     "Sinha, A., Chatterjee, N., & Ormerod, S. J.",
     "WIREs Water", "13(4), e70082", "10.1002/wat2.70082",
     ["river-birds"], "/publication/2026-conserving-world-specialist-riverine-birds"),

    ("population-decline-himalayan-river-birds", "2025-02-10",
     "Population Variability and Apparent Recent Decline of River Birds in the Indian Himalaya",
     "Sinha, Chatterjee, Ormerod & Krishnamurthy",
     "Sinha, A., Chatterjee, N., Ormerod, S. J., & Krishnamurthy, R.",
     "Biotropica", "57(2), e70017", "10.1111/btp.70017",
     ["river-birds", "population"], "/publication/2025-population-decline-himalayan-river-birds"),

    ("community-assembly-himalayan-river-birds", "2022-05-18",
     "Community assembly, functional traits, and phylogeny in Himalayan river birds",
     "Sinha, Chatterjee, Krishnamurthy & Ormerod",
     "Sinha, A., Chatterjee, N., Krishnamurthy, R., & Ormerod, S. J.",
     "Ecology and Evolution", "12(6), e9012", "10.1002/ece3.9012",
     ["river-birds"], "/publication/2022-community-assembly-himalayan-river-birds"),

    ("beta-diversity-himalayan-riverine-birds", "2022-01-01",
     "Drivers of taxonomic, phylogenetic, and functional beta diversity of Himalayan riverine birds",
     "Sinha, Menzies, Chatterjee, Rao & Naniwadekar",
     "Sinha, A., Menzies, R. K., Chatterjee, N., Rao, M., & Naniwadekar, R.",
     "Frontiers in Ecology and Evolution", "10, 788184", "10.3389/fevo.2022.788184",
     ["river-birds"], "/publication/2022-beta-diversity-himalayan-riverine-birds"),

    ("river-birds-indicators-himalayan-rivers", "2019-04-02",
     "River birds as potential indicators of local- and catchment-scale influences on Himalayan river ecosystems",
     "Sinha, Chatterjee, Ormerod, Adhikari & Krishnamurthy",
     "Sinha, A., Chatterjee, N., Ormerod, S. J., Adhikari, B. S., & Krishnamurthy, R.",
     "Ecosystems and People", "15(1), 90&ndash;101", "10.1080/26395916.2019.1591508",
     ["river-birds", "population"], "/publication/2019-river-birds-indicators-himalayan-rivers"),

    # ---------------- camera traps ----------------
    ("small-cats-central-india", "2020-06-04",
     "Population density and habitat use of two sympatric small cats in a central Indian reserve",
     "Chatterjee, Nigam & Habib",
     "Chatterjee, N., Nigam, P., & Habib, B.",
     "PLOS ONE", "15(6), e0233569", "10.1371/journal.pone.0233569",
     ["camera-traps", "population"], "/publication/2020-small-cats-central-india"),

    ("honey-badger-central-india", "2020-01-01",
     "Population Estimate, Habitat-Use and Activity Patterns of the Honey Badger in a Dry-Deciduous Forest of Central India",
     "Chatterjee, Nigam & Habib",
     "Chatterjee, N., Nigam, P., & Habib, B.",
     "Frontiers in Ecology and Evolution", "8, 585256", "10.3389/fevo.2020.585256",
     ["camera-traps", "population"], "/publication/2020-honey-badger-central-india"),

    ("rarity-detectability-continuum", "2021-01-01",
     "Deciphering the rarity&ndash;detectability continuum: optimizing survey design for terrestrial mammalian community",
     "Chatterjee, Schuttler, Nigam & Habib",
     "Chatterjee, N., Schuttler, S., Nigam, P., & Habib, B.",
     "Ecosphere", "12(9), e03748", "10.1002/ecs2.3748",
     ["camera-traps", "population", "methods"], "/publication/2021-rarity-detectability-continuum"),

    ("asiatic-black-bear-camera-traps", "2022-01-01",
     "Population estimation of Asiatic black bear in the Himalayan region of India using camera traps",
     "Bhattacharya, Chatterjee, Angrish, Meena, Sinha & Habib",
     "Bhattacharya, A., Chatterjee, N., Angrish, K., Meena, D., Sinha, B. C., & Habib, B.",
     "Ursus", "2022(33e8), 1&ndash;10", "10.2192/URSUS-D-21-00002.2",
     ["camera-traps", "population"], "/publication/2022-asiatic-black-bear-camera-traps"),

    ("snapshot-usa-2019-2023", "2025-01-01",
     "SNAPSHOT USA 2019&ndash;2023: The First Five Years of Data From a Coordinated Camera Trap Survey of the United States",
     "Rooney, Kays, Cove et al.",
     "Rooney, B., Kays, R., Cove, M. V., et al.",
     "Global Ecology and Biogeography", "34(1), e13941", "10.1111/geb.13941",
     ["camera-traps"], "/publication/2025-snapshot-usa-2019-2023"),

    ("mesopredator-response-central-india", "2018-06-12",
     "Mesopredator spatial and temporal response to large predators and anthropogenic activities in a Central Indian reserve",
     "Chatterjee, Davate, Habib & Nigam",
     "Chatterjee, N., Davate, M., Habib, B., & Nigam, P.",
     "European Congress of Conservation Biology (ECCB2018)", "abstract", "10.17011/conference/eccb2018/107750",
     ["camera-traps", "population"], "/publication/2018-mesopredator-response-central-india"),

    ("himalayan-brown-bear-lippa-asrang", "2020-01-01",
     "First photographic evidence of Himalayan brown bear from Lippa-Asrang Wildlife Sanctuary, Himachal Pradesh, India",
     "Bhattacharya, Chatterjee, Angrish, Shrotriya et al.",
     "Bhattacharya, A., Chatterjee, N., Angrish, K., Shrotriya, S., et al.",
     "International Bear News", "29(1), 23&ndash;25", "",
     ["camera-traps"], "/publication/2020-himalayan-brown-bear-lippa-asrang"),

    ("snow-leopard-lippa-asrang", "2019-01-01",
     "First photographic evidence of snow leopard from Lippa Asrang Wildlife Sanctuary, India",
     "Bhattacharya, Chatterjee, Angrish, Shrotriya et al.",
     "Bhattacharya, A., Chatterjee, N., Angrish, K., Shrotriya, S., et al.",
     "Cat News", "69, 17&ndash;18", "",
     ["camera-traps"], "/publication/2019-snow-leopard-lippa-asrang"),

    ("rusty-spotted-cat-tadoba", "2015-01-01",
     "Recent records of rusty-spotted cat in dry deciduous forest of Tadoba, Maharashtra, India",
     "Davate, Chatterjee, Dashahre, Habib, Nigam et al.",
     "Davate, M., Chatterjee, N., Dashahre, A., Habib, B., Nigam, P., et al.",
     "Cat News", "62, 22&ndash;23", "",
     ["camera-traps"], "/publication/2015-rusty-spotted-cat-tadoba"),

    # ---------------- movement ----------------
    ("individual-variability-issa", "2024-06-01",
     "Modelling individual variability in habitat selection and movement using integrated step-selection analysis",
     "Chatterjee, Wolfson, Kim, Velez, Freeman et al.",
     "Chatterjee, N., Wolfson, D., Kim, D., Velez, J., Freeman, S., Bacheler, N. M., et al.",
     "Methods in Ecology and Evolution", "15(6), 1034&ndash;1047", "10.1111/2041-210X.14321",
     ["movement", "methods"], "/publication/2024-individual-variability-issa"),

    ("free-ranging-dog-movement", "2026-01-01",
     "Of shared homes and pathways: free-ranging dog movement and habitat use in a human-wildlife landscape in India",
     "Kuruppath, Chatterjee & Krishnamurthy",
     "Kuruppath, S. V., Chatterjee, N., & Krishnamurthy, R.",
     "Movement Ecology", "", "10.1186/s40462-026-00632-2",
     ["movement"], "/publication/2026-free-ranging-dog-movement"),

    ("habitat-selection-terrestrial-mammals", "2026-01-01",
     "Local and landscape-level environmental conditions drive habitat selection across terrestrial mammal species",
     "Franke, Schipper, Avgar, B&ouml;rger, Chatterjee et al.",
     "Franke, B. H., Schipper, A. M., Avgar, T., B&ouml;rger, L., Chatterjee, N., et al.",
     "Global Ecology and Biogeography", "35(3), e70212", "10.1111/geb.70212",
     ["movement"], "/publication/2026-habitat-selection-terrestrial-mammals"),

    ("roads-traversability-central-india", "2020-01-01",
     "Integrating large mammal behaviour and traffic flow to determine traversability of roads with heterogeneous traffic on a Central Indian Highway",
     "Saxena, Chatterjee, Rajvanshi & Habib",
     "Saxena, A., Chatterjee, N., Rajvanshi, A., & Habib, B.",
     "Scientific Reports", "10, 18888", "10.1038/s41598-020-75810-2",
     ["movement", "population"], "/publication/2020-roads-traversability-central-india"),

    ("blue-sheep-resource-selection", "2020-01-01",
     "Blue sheep resource selection in alpine grasslands of a western Himalayan landscape &mdash; a point process approach",
     "Bhattacharya, Chatterjee, Rawat & Habib",
     "Bhattacharya, A., Chatterjee, N., Rawat, G. S., & Habib, B.",
     "Zoological Studies", "59, e11", "10.6620/ZS.2020.59-11",
     ["movement"], "/publication/2020-blue-sheep-resource-selection"),

    ("bharal-escape-terrain", "2023-01-01",
     "Optimal distance to escape terrain of bharal in presence of livestock in Greater Himalayan alpine rangelands",
     "Bhattacharya, Chatterjee, Rawat & Habib",
     "Bhattacharya, A., Chatterjee, N., Rawat, G. S., & Habib, B.",
     "Tropical Ecology", "64(3), 571&ndash;577", "10.1007/s42965-022-00278-2",
     ["movement"], "/publication/2023-bharal-escape-terrain"),

    ("perceived-observed-biases-movement", "2025-01-01",
     "Perceived and observed biases within scientific communities: a case study in movement ecology",
     "Shaw, Fouda, Mezzini, Kim, Chatterjee et al.",
     "Shaw, A. K., Fouda, L., Mezzini, S., Kim, D., Chatterjee, N., et al.",
     "Proceedings of the Royal Society B", "292(2051), 20250679", "10.1098/rspb.2025.0679",
     ["movement", "methods"], "/publication/2025-perceived-observed-biases-movement"),

    # ---------------- population ----------------
    ("carrying-capacity-large-carnivore", "2023-01-01",
     "Predicting carrying capacity of a large carnivore from prey densities: a new approach",
     "Chatterjee, Mukhopadhyay, Nigam & Habib",
     "Chatterjee, N., Mukhopadhyay, I., Nigam, P., & Habib, B.",
     "PeerJ", "11, e15914", "10.7717/peerj.15914",
     ["population"], "/publication/2023-carrying-capacity-large-carnivore"),

    ("great-indian-bustard-surveys", "2019-01-01",
     "Testing performance of large-scale surveys in determining trends for the critically endangered Great Indian Bustard <i>Ardeotis nigriceps</i>",
     "Khan, Chatterjee & Habib",
     "Khan, S., Chatterjee, N., & Habib, B.",
     "Scientific Reports", "9, 11627", "10.1038/s41598-019-48193-2",
     ["population", "methods"], "/publication/2019-great-indian-bustard-surveys"),

    ("human-tiger-interactions", "2022-01-01",
     "Predicting negative human&ndash;tiger (<i>Panthera tigris</i>) interactions in mosaic landscapes around Dudhwa and Pilibhit Tiger Reserves in India",
     "Chatterjee, Chatterjee, Chandel, Bhattacharya & Kaul",
     "Chatterjee, M., Chatterjee, N., Chandel, P., Bhattacharya, T., & Kaul, R.",
     "Frontiers in Conservation Science", "3, 999195", "10.3389/fcosc.2022.999195",
     ["population"], "/publication/2022-human-tiger-interactions"),

    ("tatr-tiger-status-report", "2015-01-01",
     "Status of Tigers, Co-Predator and Prey in Tadoba Andhari Tiger Reserve (TATR)",
     "Habib, Nigam, Chatterjee et al.",
     "Habib, B., Nigam, P., Chatterjee, N., et al.",
     "Wildlife Institute of India, Technical Report", "", "",
     ["population"], "/publication/2015-tatr-tiger-status-report"),

    ("majgaonkar-response", "2019-01-01",
     "Casual analysis and short-sighted inferences: A response to Majgaonkar et al. 2019",
     "Shrotriya, Chatterjee & Habib",
     "Shrotriya, S., Chatterjee, N., & Habib, B.",
     "Conservation Science and Practice", "1(12), e124", "10.1111/csp2.124",
     ["population"], "/publication/2019-majgaonkar-response"),

    # ---------------- methods ----------------
    ("life-science-retractions", "2025-01-01",
     "Understanding the patterns and magnitude of life science publication retractions in the last four decades",
     "Bhattacharyya, Chatterjee & Ramanathan",
     "Bhattacharyya, S., Chatterjee, N., & Ramanathan, A.",
     "International Journal for Educational Integrity", "21(1), 17", "10.1007/s40979-025-00193-8",
     ["methods"], "/publication/2025-life-science-retractions"),

    ("bes-data-code-archiving", "2026-01-01",
     "Data- and code-archiving in the British Ecological Society journals: present status and recommendations for future improvements",
     "Cooper & the BES Data and Code Hackathon Group",
     "Cooper, N., & the BES Data and Code Hackathon Group",
     "Methods in Ecology and Evolution", "", "10.1111/2041-210X.70338",
     ["methods"], "/publication/2026-bes-data-code-archiving"),
]

GROUP_LABEL = {}  # filled from data file at build time (not needed here)

def yq(s):
    """Quote a string as a YAML double-quoted scalar."""
    return json.dumps(s, ensure_ascii=False)

def existing_body(permalink):
    """Reuse the prose already written for a paper, matched on its permalink."""
    for fn in os.listdir(PUBDIR):
        if not fn.endswith(".md"):
            continue
        raw = io.open(os.path.join(PUBDIR, fn), encoding="utf-8").read()
        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", raw, re.S)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)
        if re.search(r"^permalink:\s*" + re.escape(permalink) + r"\s*$", fm, re.M):
            return body.strip("\n")
    return ""

written = []
for (slug, date, title, short, cite, journal, tail, doi, groups, link) in P:
    year = date[:4]
    venue = (journal + (" " + tail if tail else "")).strip()
    citation = '%s (%s). &quot;%s&quot; <i>%s</i>%s.' % (
        cite, year, title, journal, (", " + tail) if tail else "")
    body = existing_body(link)
    head = [
        "---",
        "title: " + yq(title),
        "collection: publications",
        "category: manuscripts",
        "permalink: " + link,
        "date: " + date,
        "venue: " + yq(venue),
        "authors: " + yq(short),
        "journal: " + yq(journal),
        "groups: [" + ", ".join(yq(g) for g in groups) + "]",
    ]
    if doi:
        head.append("paperurl: " + yq("https://doi.org/" + doi))
        head.append("doi: " + yq(doi))
    head.append("citation: " + yq(citation))
    head.append("---")
    out = "\n".join(head) + "\n"
    if body:
        out += "\n" + body + "\n"
    fn = "%s-%s.md" % (date, slug)
    io.open(os.path.join(PUBDIR, fn), "w", encoding="utf-8", newline="\n").write(out)
    written.append(fn)

print("wrote", len(written), "files")
for w in written:
    print("  ", w)
