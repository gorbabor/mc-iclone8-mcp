# mc-iclone8-mcp

[English](README.md)

Serveur MCP local pour piloter iClone 8 via son API Python officielle.

Le plugin iClone affiche une petite fenêtre avec les boutons de démarrage et
d’arrêt. Le point d’accès MCP est local, par défaut :
`http://127.0.0.1:8766/mcp`. Les commandes sont toujours renvoyées vers le
thread principal d’iClone avant leur exécution.

## Prérequis

- iClone 8 sous Windows.
- Un client compatible avec MCP HTTP Streamable, tel que Codex.

## Installer le plugin iClone

1. Copier le dossier de ce dépôt dans :

   ```text
   <iClone 8>\Bin64\OpenPlugin\mc-iclone8-mcp
   ```

2. Lancer iClone 8 et charger le plugin.
3. Ouvrir **Plugins → mc-iclone8-mcp → Ouvrir le serveur MCP**.
4. Cliquer sur **Démarrer**. Le statut doit indiquer
   `http://127.0.0.1:8766/mcp`.

Le serveur utilise volontairement `127.0.0.1` : il ne peut être appelé que par
des applications exécutées sur le même ordinateur qu’iClone.

## Installer comme serveur MCP dans Codex

Garder iClone ouvert et démarrer le serveur, puis exécuter :

```powershell
codex mcp add mc-iclone8-mcp --url http://127.0.0.1:8766/mcp
```

Redémarrer Codex, ou ouvrir une nouvelle tâche, puis vérifier :

```powershell
codex mcp list
```

Autre possibilité : ajouter ceci à `%USERPROFILE%\.codex\config.toml` (ou au
fichier `.codex\config.toml` du projet) :

```toml
[mcp_servers.mc-iclone8-mcp]
url = "http://127.0.0.1:8766/mcp"
startup_timeout_sec = 15
tool_timeout_sec = 60
```

Le même exemple prêt à copier se trouve dans
[`examples/codex-config.toml`](examples/codex-config.toml).

Les configurations proposées pour Claude Code, Pi coding agent, OpenClaw,
Hermes et VS Code sont regroupées dans
[`docs/agent-configs.fr.md`](docs/agent-configs.fr.md). Le skill expert
réutilisable se trouve dans [`skills/iclone8-mcp`](skills/iclone8-mcp).

## Fonctions disponibles

La version `v0.1.0` expose 60 outils MCP :

| Catégorie | Outils | Ce qu’ils permettent de faire |
| --- | --- | --- |
| Diagnostic | `ping_iclone`, `get_api_version`, `get_runtime_diagnostics` | Vérifier la connexion, la version ciblée et les capacités RLPy disponibles. |
| Scène et objets | `list_objects`, `get_selection`, `select_object`, `set_visibility`, `delete_object`, `clone_object`, `link_object`, `unlink_object`, `align_object`, `set_static` | Explorer, sélectionner, afficher/masquer, supprimer, cloner, lier, délier et aligner les objets. |
| Projet et assets | `create_primitive`, `save_project`, `get_project_info`, `import_asset`, `load_motion`, `preload_motion`, `load_substance_painter_textures`, `export_fbx` | Créer des primitives, importer des fichiers, charger des motions, appliquer des textures, sauvegarder et exporter en FBX. |
| Transformations | `get_transform`, `set_transform`, `delete_transform_key`, `move_transform_key`, `set_transform_key_transition`, `clear_transform_keys` | Lire et modifier position, rotation, échelle et clés d’animation des objets. |
| Timeline | `get_timeline`, `set_timeline`, `play_timeline`, `pause_timeline`, `stop_timeline`, `clear_scene_animations` | Contrôler la lecture, la position temporelle et la suppression des animations de la scène. |
| Caméras | `get_camera`, `get_camera_capabilities`, `set_camera`, `set_camera_transform`, `set_camera_focal_key`, `set_camera_dof`, `set_current_camera`, `set_camera_look_at` | Lire et animer les caméras, régler focale, clipping, profondeur de champ, caméra active et suivi d’un objet. |
| Matériaux | `get_materials`, `set_material_color`, `set_material_texture`, `set_material_value` | Lire les matériaux, appliquer des couleurs et textures, et animer opacité, brillance ou auto-illumination. |
| Lumières | `get_light`, `set_light` | Lire et modifier activation, couleur et intensité des lumières. |
| Avatars | `get_avatar_info`, `get_avatar_capabilities`, `get_skin_bones`, `get_animation_clips`, `set_clip_speed`, `set_clip_loop_count` | Inspecter les avatars, os, composants et clips, puis régler vitesse et boucles de lecture. |
| Morphs | `list_morphs`, `get_morph_weight`, `set_morph_weight` | Lister, lire et animer les poids de morphs sur props et avatars compatibles. |
| Rendu | `get_render_settings`, `render_video` | Lire la résolution et lancer un rendu vidéo après confirmation explicite. |
| Mocap et réseau | `get_mocap_status`, `get_network_capabilities` | Diagnostiquer le gestionnaire mocap et la disponibilité TCP/UDP native. |

Ces outils permettent notamment de :

- explorer, sélectionner, transformer, afficher ou supprimer les objets ;
- créer les primitives officielles d’iClone, importer des assets et sauvegarder
  les projets ;
- piloter la timeline, les caméras et les éclairages ;
- lire et modifier les matériaux, les couleurs, les textures, l’opacité, la brillance et l’auto-illumination ;
- inspecter les composants d’avatar, les os de skin, les clips, leurs boucles et les morphs ;
- charger ou précharger des motions, appliquer des dossiers de textures Substance Painter et exporter un objet en FBX ;
- lire la taille de rendu et lancer le rendu uniquement après confirmation explicite ;
- diagnostiquer l’état mocap et la disponibilité TCP/UDP native sans ouvrir de connexion externe.

Le plugin cible exclusivement iClone 8 et son API Python officielle.

## Exemples d’instructions pour un agent

Donner un objectif clair, les noms des objets et des valeurs numériques. L’agent
peut d’abord inspecter la scène, puis appeler les outils MCP adaptés.

| Catégorie | Instruction illustrative |
| --- | --- |
| Scène | « Liste les props de la scène, puis sélectionne `MCP8_Live_Test_Box`. » |
| Création | « Crée une boîte rouge nommée `Logo_Block` à X=0, Y=0, Z=20 et ajoute un sol sous elle. » |
| Transformation | « Déplace `Logo_Block` à X=200 à la frame 120 et règle son échelle à 150 %. » |
| Matériaux | « Liste les matériaux de `Logo_Block`, puis mets le matériau 0 en bleu roi et masque sa texture diffuse. » |
| Cartes de texture | « Applique `C:\\Assets\\logo_basecolor.png` comme texture diffuse du matériau 0 de `Logo_Block`. » |
| Animation matériau | « À la frame 300, règle l’opacité du matériau 0 de `Logo_Block` à 0,25 et son auto-illumination à 0,8. » |
| Timeline | « Place la tête de lecture à la frame 0, lis les frames 0 à 300, puis arrête la lecture. » |
| Caméra | « Lis la focale de la caméra active et règle-la à 50 mm. » |
| Animation | « Anime `Orbit_Sphere` autour de `Center_Cube` avec des clés de transformation aux frames 0, 150, 300, 450 et 600. » |
| Avatar | « Liste les os de skin et les clips d’animation de l’avatar `Character1`. » |
| Lecture avatar | « Inspecte les capacités de `Character1`, puis règle le clip 0 pour trois boucles à la vitesse 1,2. » |
| Morphs | « Liste les morphs de `Character1`, puis règle le morph facial indiqué au poids 0,5 à la frame courante. » |
| Import/export | « Importe ce fichier `.iProp`, sauvegarde le projet, puis exporte l’objet sélectionné en FBX. » |
| Rendu | « Lis les dimensions de rendu. Seulement après ma confirmation, rends la vidéo avec les réglages actuels du projet iClone. » |
| Mocap | « Vérifie si la mocap iClone est active ; ne modifie ni ne connecte aucun appareil. » |

Pour un plan où la caméra suit un sujet, utiliser une vraie caméra de scène —
pas la Preview Camera : « Crée ou active `Camera1`, puis pose ses clés de
transformation aux mêmes frames que le sujet, avec un décalage relatif constant. »

## Développement

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
```

La référence principale est la [documentation Python officielle d’iClone
8](https://wiki.reallusion.com/IC8_Python_API).
