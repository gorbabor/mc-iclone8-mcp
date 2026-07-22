# mc-iclone8-mcp

Serveur MCP local pour piloter iClone 8 via son API Python officielle.

Le plugin crée une interface iClone permettant de démarrer ou d’arrêter le
serveur local, accessible par défaut à l’adresse `http://127.0.0.1:8766/mcp`.
Les commandes iClone sont exécutées dans le thread principal de l’application.

## Installation

Copier ce dossier dans :

```text
<iClone 8>\Bin64\OpenPlugin\mc-iclone8-mcp
```

Dans iClone 8, charger le plugin puis ouvrir le menu **Plugins →
mc-iclone8-mcp → Ouvrir le serveur MCP**. Utiliser les boutons **Démarrer** et
**Arrêter** pour gérer le serveur.

## Fonctions

Le serveur fournit des outils MCP pour :

- explorer, sélectionner, transformer, afficher ou supprimer les objets ;
- créer les primitives officielles d’iClone, importer des assets et sauvegarder
  les projets ;
- piloter la timeline, les caméras et les éclairages ;
- lire et modifier les matériaux et les couleurs ;
- inspecter les os de skin, les clips et les morphs ;
- charger des motions et exporter un objet en FBX.

Les fonctions sont conçues pour iClone 8 : les anciennes API iClone 7, dont les
motion bones supprimés dans iClone 8, ne sont pas utilisées.

## Développement

Exécuter les vérifications de base :

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
```

La référence principale est la [documentation Python officielle d’iClone
8](https://wiki.reallusion.com/IC8_Python_API).
