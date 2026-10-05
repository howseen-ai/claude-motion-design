# Veille : 475 prompts Opus 5.5 "vidéos en code" → ce qui manque à notre skill motion-design

Source : collection publique MIT (`skillry.dev`), 475 fiches dans `data/videos.json` + `prompts/*.md`, champs slug/author/post_url/category/tech_tags/prompt/prompt_partial/added. Zéro métrique de viralité dans le dataset : aucune affirmation de performance ci-dessous n'est inventée, et "prompt_partial" signifie que l'auteur n'a lui-même partagé qu'une partie de son prompt (pas que notre extraction est tronquée).

## 1. Dédoublonnage (script Python, `/Users/raphaelaubry/.claude/jobs/372bf520/tmp/opus55work/dedupe.py`)

Normalisation : minuscule, espaces compactés, ponctuation retirée pour le clustering strict.

| Mesure | Valeur |
|---|---|
| Entrées totales (videos.json) | 475 |
| Prompts uniques (texte normalisé) | 415 |
| Mots, 475 prompts | 47 408 |
| Mots, 415 prompts uniques | 42 026 |

**Top 10 prompts les plus réutilisés** (texte identique après normalisation) :

| # | Reprises | Prompt (début) |
|---|---|---|
| 1 | 43 | "make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. go all out." |
| 2 | 7 | `<inputs>` UI morph "8 to 12 UI states... button, loader, player, slider, toggle, tabs, chart, command palette, toast" |
| 3 | 5 | "I want you to create a highly professional SaaS product launch video. Go and find some SaaS..." |
| 4 | 2 | "Research Distilbook. Make a dynamic 40-second motion graphics video on Distilbook..." |
| 5 | 2 | variante "resume" (sans accent) du prompt #1 |
| 6 | 2 | `<inputs>` UI morph variante (vidéos verticales réelles, 10-20 clips) |
| 7 | 2 | "create a motion design video of a poster breaking out of its own frame." |
| 8 | 2 | pixel-art wizard Canvas 2D, un seul fichier HTML |
| 9 | 2 | "Show me what goes on inside an AI data centre." |
| 10 | 2 | replay de score (reel) "who are you as Opus 5.5" |

Le prompt viral cité dans la consigne ("make a dynamic X-second motion graphics video... showreel for a résumé/resume") existe en 73 variantes textuelles uniques dès qu'on relâche la normalisation stricte (durée différente, "résumé"/"resume", ajout d'une marque, "go all out" optionnel, etc.) ; cumulées, ces variantes couvrent 117 des 475 entrées, soit un quart du dataset. C'est de loin le phénomène de reprise dominant.

## 2. Lecture intégrale

Les 415 prompts uniques ont été regroupés en 11 fichiers chunks (3 500-7 000 mots chacun, triés catégorie puis slug) et lus en entier avec l'outil Read.

- **Mots lus : 42 026 / 42 026 mots uniques (100 %)**
- Base de comparaison : 47 408 mots au total si on compte les doublons, donc ~11,3 % du volume brut est de la pure répétition textuelle du prompt viral et de ses proches variantes.

Répartition par catégorie des 415 uniques : motion (~45 %), interactive/jeux (~25 %), explainer (~20 %), 3d (~10 %). La catégorie "interactive" (jeux browser, démos 3D) apporte très peu de technique transférable à notre pipeline vidéo Howseen : elle a été lue en entier mais peu citée ci-dessous.

## 3a. Templates à ajouter au §9b (prompt library)

| Template | Source (slug / post_url) | Pourquoi c'est mieux que notre §9b actuel |
|---|---|---|
| **Brief "produit" avec source-of-truth + règles numérotées + auto-interrogation QA** | `daniel-haida-636937` — https://x.com/daniel_haida/status/2104139720829636937 | Notre §11 couvre déjà le mode "film produit SaaS", mais ce prompt ajoute 3 pièces concrètes qu'on n'a pas : (1) chemins de repo explicites comme "source of truth" (design tokens, captures, wordmark) avec consigne "ne régresse pas la composition existante, crée-en une nouvelle nommée X" ; (2) 19 règles numérotées très concrètes dont une absente de notre skill : "les éléments ne démarrent/finissent jamais tous à la même frame" (désynchronisation volontaire) et "le premier moment produit significatif doit arriver vers 2 s, pas de générique logo de 5 s" ; (3) une liste de 10 questions d'auto-interrogation après rendu ("Est-ce que ça ressemble à un gabarit SaaS ? Est-ce que le produit reste lisible ?") et un "quality bar" formulé en négatif ("rejette ton propre résultat s'il ressemble à ceci : [liste]"). |
| **Bumper d'identité kinétique verrouillé** | `techhalla-498547` — https://x.com/techhalla/status/2103411244468498547 | Un format de 20 s qu'on n'a pas en banque : palette à 3 couleurs strictement verrouillée, système typographique à 3 polices avec tracking exact par usage (display/urban/mono), message verrouillé battu par battu ("ne pas adoucir, ne pas ajouter de slogan"), effet de "désalignement d'impression" (double calque décalé ±2-4 px, deux couleurs, 40 % opacité, uniquement sur les frames d'impact) et un micro-souffle de boucle (scale 1.000→1.012→1.000 sur le hold final). Directement réutilisable comme sting de marque Howseen avant chaque reel. |
| **Poème typographique où les mots sont l'architecture** | `gdgtify-929495` — https://x.com/Gdgtify/status/2103458245213929495 | Technique absente de notre skill : chaque mot du texte joue un rôle architectural littéral (WAIT = linteau, VOICE = support, ROOM = ouverture, FLOOR = plateforme), et la scène se construit physiquement à partir des lettres elles-mêmes, pas d'illustrations séparées. Détail technique précis et nouveau : "pour les transitions entre mots sans rapport, utiliser l'occlusion ou des bords structurels alignés ; ne jamais interpoler des points de tracé arbitraires" — règle de continuité de morph de glyphes qu'on n'a pas. |
| **Prompt gabarit à variables `{{PLACEHOLDER}}`** | `ik-builds-585923` — https://x.com/ik_builds/status/2103890476885585923 | Notre §9b donne des prompts "à adapter" en prose ; celui-ci est un vrai gabarit réutilisable avec champs ({{PRODUCT}}, {{POSITIONING_DOCS}}, {{BANNED_WORDS}}, {{COLOR_ACCENT_1}}...) et une règle absente chez nous : "jamais un logo encadré dans une boîte, toujours le vrai mark + le wordmark dans sa police". Utile pour industrialiser nos briefs clients/affiliés. |
| **Zoom infini en portails avec génération d'assets + profondeur paramétrique** | `koldo2k-778767` — https://x.com/koldo2k/status/2103129343253778767 | Donne une formule absente de notre §2 caméra : "vitesse constante perçue = durée de segment proportionnelle à log(zoom)", et une règle de continuité de coupe : "le verre/reflet de chaque portail contient déjà le monde suivant ; on coupe sans heurt quand il remplit le cadre". Notre skill a des règles de flood/camera mais pas cette mécanique de portail à profondeur paramétrique (échelle de calque = caméra^Z). |
| **Pipeline podcast : repérage à effort variable + jugement sans boucle de reprise systématique** | `stokebuilder-356793` — https://x.com/stokebuilder/status/2103896101120356793 | Affine notre §9d (B-roll sur voix off) avec un détail de workflow qu'on n'a pas formalisé : un agent à effort extra-high repère TOUS les timecodes utiles (35-50 moments), un agent à effort medium construit chaque animation, puis un agent extra-high juge une seule fois chaque clip sur 4 critères et ne renvoie en correction QUE les cas "manifestement mauvais" (pas de boucle de reprise en masse). Économise du temps/coût par rapport à notre boucle "critique jusqu'à 8+ partout". |

## 3b. Techniques, contraintes, astuces — adopt / adapt / ignore

| Technique | Source | Décision | Raison en une ligne |
|---|---|---|---|
| Synthèse physique Karplus-Strong (corde pincée, guzheng) en WebAudio temps réel | `eigeorguy-813651` / `demitiyageekzen-818523` — https://x.com/eigeorguy/status/2103992442072813651 | **adopt** | Étend notre règle "son synthétisé" (§9, click/pop/thump) à un vrai modèle physique d'instrument, utile pour des stings plus riches sans fichier audio. |
| Intensité d'effet mise à l'échelle par section (intro 40 % / couplet 70 % / refrain 100 %) | `pound75423-464968` — https://x.com/pound75423/status/2103722556918464968 | **adopt** | Règle générale et simple qu'on n'a pas : moduler systématiquement la force des effets (shake, particules, flash) selon la section du film, pas seulement sur/hors du beat. |
| Désalignement d'impression (double calque coloré décalé, frames d'impact uniquement) | `techhalla-498547` | **adopt** | Signature visuelle "print" low-cost, aucune dépendance, cohérente avec notre interdiction des glows/particules. |
| Lettres mélangées puis "snap" (Fisher-Yates par glyphe, calé sur le beat) | `techhalla-498547` | **adopt** | Variante de notre "masked text rise" pour un hook plus punchy en 15-20 s. |
| Respiration de boucle (échelle 1.000→1.012→1.000 sur le hold final) | `techhalla-498547` | **adopt** | Corrige directement notre règle "jamais de frame figée" sur les plans de fin tenus. |
| Intervalle de boucle demi-ouvert `[0, durée)` sans dupliquer la frame de fin | `thegrootdev-966114` — https://x.com/TheGrootDev/status/2103516567824966114 | **adopt** | Détail technique précis d'export qui évite un micro-stutter de boucle qu'on n'avait pas explicité. |
| Sous-titres mesurés dans la vraie police et réduits pour tenir dans la zone sûre 9:16 | `l3d1c-632524` — https://x.com/l3d1c/status/2104649028193632524 | **adopt** | Concret et absent de notre §6 (formats) : éviter que les sous-titres passent sous les boutons TikTok/IG. |
| Tracé "stylo" via `stroke-dashoffset` pour notes manuscrites qui s'écrivent | `ik-builds-585923` | **adopt** | Complète nos effets de reveal masqué pour un style "marker notes" demandé dans plusieurs prompts. |
| Rôle nommé pour l'agent de critique (ex. "superviseur VFX") | `nathanwilbanks-981110` — https://x.com/NathanWilbanks_/status/2103881538592981110 | **adopt** | Coût nul, améliore la sévérité de notre boucle de critique déjà en place. |
| Triage de bugs en P0/P1/P2 + désaccords tranchés et justifiés par écrit + checkpoint de rollback avant chaque round | `voxyz-ai-345550` — https://x.com/Voxyz_ai/status/2103117246860345550 | **adopt** | Raffine notre boucle de critique multi-rounds (§8/§11) avec une priorisation et une sécurité de retour en arrière qu'on n'avait pas formalisées. |
| Vidéo générée par un modèle (Seedance 2.5) servant de référence, puis redessinée entièrement en code par-dessus (rotoscopie) | `anabology-491441` / `anjmaxx-459455` — https://x.com/anabology/status/2103534482930491441 | **adapt** | Intéressant seulement si Raphaël a des crédits Higgsfield/vidéo à dépenser sur un coup ponctuel ; contraire à notre stack "0 €, 100 % code" par défaut. |
| Pipeline 3D rigué nommé PARSE→MASS→RIG→SKIN→PACK (pièces nommées, export CAO) | `0xwast3-222104` — https://x.com/0xWast3/status/2103513328077222104 | **ignore** | Notre pipeline ne produit pas d'assets 3D riggés exportables ; hors scope vidéo. |
| Tests automatisés (unitaires/navigateur) sur un rendu 3D/jeu | `aayush4soni-644283` / `stephanferraro-224281` — https://x.com/StephanFerraro/status/2103020274107224281 | **ignore** | Pertinent pour un produit interactif persistant, pas pour un film éphémère rendu une fois. |
| Moteur physique multi-matériaux (sable/eau/feu, 100k+ particules) en un seul fichier | `cyrilxbt-149036` — https://x.com/cyrilXBT/status/2103532793406149036 | **ignore** | Faisable mais coûteux en temps/tokens pour un gain visuel marginal sur nos formats courts ; déjà couvert en substance par nos règles de particules/goo existantes. |
| Vidéo scrub liée au scroll du site (`video.currentTime` piloté par ScrollTrigger) | `iamtanzil-675031` | **ignore** | Technique de hero de site web, pas de rendu vidéo offline ; hors périmètre du skill motion-design (qui produit des fichiers vidéo, pas des pages). |
| Révélation "rayons X" au curseur via masque radial-gradient | `iamtanzil-120030` | **ignore** | Idem : interaction de site, pas une technique de film. |

## 3c. 8 à 12 prompts à adapter pour Howseen (formats launch film / LinkedIn 4:5 / X / reel IG quotidien)

Rappel du positionnement : Howseen suit les marques citées par ChatGPT/Gemini/Perplexity ; les formats utiles sont films de lancement, boucles LinkedIn 4:5, vidéos X, et le reel IG quotidien "marque aléatoire → top de ChatGPT".

| Slug | post_url | Catégorie | Adaptation Howseen |
|---|---|---|---|
| `ajith-io-890146` | https://x.com/ajith_io/status/2103449416325890146 | motion | Le prompt viral "showreel" appliqué à Howseen même : un film de 15 s où le dashboard réel (scan → citations → écarts concurrents) devient la preuve de compétence, posté comme asset de crédibilité/recrutement. |
| `twoclipping-402193` | https://x.com/twoclipping/status/2103273003555402193 | motion | Template UI morph (bouton → loader → ... → toast, repris 7 fois) adapté à notre propre produit : scan → loader → graphique de citations → écart concurrent → CTA "get-cited", en boucle LinkedIn 4:5. |
| `daniel-haida-636937` | https://x.com/daniel_haida/status/2104139720829636937 | motion | Devient le brief-maître pour chaque film de lancement de feature Howseen : pointer vers les vrais tokens de design/app/PostHog, lister les règles anti-template, et finir par la checklist d'auto-interrogation avant de livrer. |
| `techhalla-498547` | https://x.com/techhalla/status/2103411244468498547 | motion | Sting de marque Howseen de 15-20 s (palette/message verrouillés) à ouvrir chaque jour avant le reel IG "marque aléatoire → top de ChatGPT". |
| `stokebuilder-356793` | https://x.com/stokebuilder/status/2103896101120356793 | explainer | Pipeline pour habiller automatiquement les apparitions filmées de Raphaël (calls, podcasts) avec des incrustations plein écran du dashboard Howseen, PiP bas-droite, sans tout refaire manuellement. |
| `gdgtify-929495` | https://x.com/Gdgtify/status/2103458245213929495 | motion | Vidéo X de positionnement façon manifeste : les mots clés ("cité", "classé", "visible") deviennent littéralement l'architecture de l'argument "être cité par l'IA, pas juste bien classé sur Google". |
| `koldo2k-778767` | https://x.com/koldo2k/status/2103129343253778767 | explainer | Version simplifiée 100 % code (sans les générateurs d'images payants du prompt original) : zoom infini en boucle à travers "une réponse ChatGPT" → "la citation" → "le dashboard" → "le logo de la marque", pour IG. |
| `ishaaqahamed-107563` | https://x.com/Ishaaqahamed/status/2103837917538107563 | motion | Devient le squelette standard du reel quotidien : 1080×1080, hook en 1 s, boucle parfaite — à verrouiller comme template reel-factory. |
| `thegrootdev-966114` | https://x.com/TheGrootDev/status/2103516567824966114 | motion | Structure "silhouette persistante" (ici un Poké Ball) réappliquée : le mark Howseen reste visible et reconnaissable à travers tous les états (scan → marques suivies → alerte), boucle LinkedIn. |
| `ik-builds-585863` *(ik-builds-585923)* | https://x.com/ik_builds/status/2103890476885585923 | motion | Transformé en gabarit interne à variables pour les demandes client/affiliées récurrentes de film explicatif 15 s, avec la règle logo réel + wordmark imposée. |

## 3d. Avertissements d'échec récurrents mentionnés par les créateurs

- **Rythme trop rapide/saccadé et musique générique perçus comme non professionnels** : retour explicite d'un créateur sur sa propre vidéo — "I would not hire you... This is not a professional-looking video. Also, it is a bit too fast and bumpy" (`sachaarbonel-673648` — https://x.com/sachaarbonel/status/2103614797501673648).
- **Artefacts de lip-sync/membres mal posés sur un personnage qui ne chante pas vraiment** : bouche qui "jiggle" sans réellement synchroniser, bras figé en position qui "a l'air d'une erreur" (`doubleunplussed-181894` — https://x.com/doubleunplussed/status/2103697580421181894).
- **Typographie faible sans direction artistique fournie** : "very blah text design, I need a fal design skill/guideline ideally" (`mattworkman-309357` — https://x.com/mattworkman/status/2104662818742309357) — confirme notre règle "sans charte/facts.md, pas de film correct".
- **Résultat générique tant que le prompt viral brut n'est pas enrichi d'une direction de marque** : un créateur rapporte un résultat "far better" uniquement après avoir réinjecté le prompt showreel sur un brief déjà construit avec références et storyboard (`elliot-garreffa-446825` — https://x.com/elliot_garreffa/status/2104213514944446825) — confirme notre diagnostic existant "même prompt collé sans charte = même film que tout X".
- **Dérive de coût/temps sur les pièces 3D/simulation ambitieuses** : 3h et environ 54,52 $ pour un seul zoom caméra Three.js (`kgonia7-746268` — https://x.com/kgonia7/status/2103835848575746268), 5h28 et environ 90 $ pour un laboratoire de trou noir interactif (`Voxyz_ai`, même post que ci-dessus) — rappelle notre règle "effort max seulement si les 3 premières secondes portent un lancement, medium pour les retouches".
- **Liste "anti-slop IA" reconnue par plusieurs créateurs eux-mêmes** (bannis dans leurs propres prompts) : cerveaux/robots/réseaux de neurones génériques, gradients doux, particules en explosion, "HUD futuriste" en stock, glassmorphisme partout, néon violet/bleu générique, énergie "slide Canva" — confirme et détaille notre règle anti-"AI motion" existante (§9b), avec des exemples concrets supplémentaires à citer si on veut enrichir la liste de bannis.

## Sources

Toutes les citations ci-dessus proviennent de `data/videos.json` et des fichiers `prompts/*.md` de la collection (licence MIT, cloné localement). Aucun chiffre de viralité, de vues ou d'engagement n'a été inventé : le dataset n'en contient pas, et seuls les chiffres de temps/coût explicitement donnés par les auteurs eux-mêmes (ex. "$54.52", "5h 28m") ont été repris, avec leur source.
