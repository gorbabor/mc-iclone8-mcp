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

## Développement

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
```

La référence principale est la [documentation Python officielle d’iClone
8](https://wiki.reallusion.com/IC8_Python_API).
