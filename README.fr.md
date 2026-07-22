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

## Fonctions disponibles

Le serveur fournit des outils MCP pour :

- explorer, sélectionner, transformer, afficher ou supprimer les objets ;
- créer les primitives officielles d’iClone, importer des assets et sauvegarder
  les projets ;
- piloter la timeline, les caméras et les éclairages ;
- lire et modifier les matériaux et les couleurs ;
- inspecter les os de skin, les clips et les morphs ;
- charger des motions et exporter un objet en FBX.

Le plugin cible iClone 8. Il écarte volontairement les API propres à iClone 7,
dont les motion bones supprimés dans iClone 8.

## Exemples d’instructions pour un agent

Donner un objectif clair, les noms des objets et des valeurs numériques. L’agent
peut d’abord inspecter la scène, puis appeler les outils MCP adaptés.

| Catégorie | Instruction illustrative |
| --- | --- |
| Scène | « Liste les props de la scène, puis sélectionne `MCP8_Live_Test_Box`. » |
| Création | « Crée une boîte rouge nommée `Logo_Block` à X=0, Y=0, Z=20 et ajoute un sol sous elle. » |
| Transformation | « Déplace `Logo_Block` à X=200 à la frame 120 et règle son échelle à 150 %. » |
| Matériaux | « Liste les matériaux de `Logo_Block`, puis mets le matériau 0 en bleu roi et masque sa texture diffuse. » |
| Timeline | « Place la tête de lecture à la frame 0, lis les frames 0 à 300, puis arrête la lecture. » |
| Caméra | « Lis la focale de la caméra active et règle-la à 50 mm. » |
| Animation | « Anime `Orbit_Sphere` autour de `Center_Cube` avec des clés de transformation aux frames 0, 150, 300, 450 et 600. » |
| Avatar | « Liste les os de skin et les clips d’animation de l’avatar `Character1`. » |
| Morphs | « Liste les morphs de `Character1`, puis règle le morph facial indiqué au poids 0,5 à la frame courante. » |
| Import/export | « Importe ce fichier `.iProp`, sauvegarde le projet, puis exporte l’objet sélectionné en FBX. » |

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
