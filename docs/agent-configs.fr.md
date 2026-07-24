# Configurer les agents avec mc-iclone8-mcp

Le serveur doit être démarré dans iClone 8 avant de connecter un agent :

```text
http://127.0.0.1:8766/mcp
```

Le serveur est local et utilise le transport MCP Streamable HTTP. Il ne faut
pas utiliser `stdio`, `sse` ou une URL distante pour cette installation.

## Codex

```powershell
codex mcp add mc-iclone8-mcp --url http://127.0.0.1:8766/mcp
codex mcp list
```

Configuration équivalente dans `%USERPROFILE%\.codex\config.toml` :

```toml
[mcp_servers.mc-iclone8-mcp]
url = "http://127.0.0.1:8766/mcp"
startup_timeout_sec = 15
tool_timeout_sec = 60
```

## Claude Code

```powershell
claude mcp add --transport http mc-iclone8-mcp http://127.0.0.1:8766/mcp --scope user
claude mcp list
```

Pour un projet partagé, remplacer `--scope user` par `--scope project`. Claude
Code demandera l’approbation du serveur de projet avant sa première utilisation.

## Pi coding agent

Pi utilise un fichier MCP avec l’extension ou le package MCP installé. Dans le
fichier `mcp.json` de l’agent Pi, utiliser la forme HTTP suivante :

```json
{
  "mcpServers": {
    "mc-iclone8-mcp": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8766/mcp"
    }
  }
}
```

Le package `pi-codemcp` est nécessaire si la distribution Pi utilisée ne fournit
pas déjà le client MCP. Vérifier ensuite que le serveur apparaît dans la liste
des outils de Pi.

## OpenClaw

Les versions d’OpenClaw et leurs extensions peuvent exposer MCP différemment.
Lorsque le client MCP HTTP est disponible, utiliser cette entrée équivalente :

```json
{
  "mcpServers": {
    "mc-iclone8-mcp": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8766/mcp"
    }
  }
}
```

Vérifier la syntaxe exacte de la version installée avec `openclaw mcp --help`.
La commande `openclaw mcp serve` sert principalement à exposer OpenClaw comme
serveur/bridge MCP ; elle ne remplace pas nécessairement le client MCP requis
pour appeler iClone.

## VS Code

Créer `.vscode/mcp.json` dans le projet :

```json
{
  "servers": {
    "mc-iclone8-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8766/mcp"
    }
  }
}
```

Puis utiliser la commande **MCP: List Servers** ou **MCP: Start Server** dans
VS Code et vérifier que les outils sont visibles dans Copilot/Agent mode.

## Hermes et autres clients MCP

Si le client accepte le transport Streamable HTTP, utiliser :

```json
{
  "name": "mc-iclone8-mcp",
  "type": "streamable-http",
  "url": "http://127.0.0.1:8766/mcp"
}
```

La clé enveloppante peut être `mcpServers`, `servers` ou une interface
graphique selon l’agent. Si Hermes ne prend en charge que `stdio`, il ne peut
pas appeler directement ce serveur HTTP sans un adaptateur MCP.

## Installer le skill expert

Le dossier [`skills/iclone8-mcp`](../skills/iclone8-mcp) contient le skill
`SKILL.md`, utilisable par les agents compatibles avec le format Agent Skills.
Copier le dossier dans le répertoire de skills de l’agent :

```text
Codex       : %USERPROFILE%\.codex\skills\iclone8-mcp
Claude Code : .claude\skills\iclone8-mcp
Projet      : .agents\skills\iclone8-mcp
```

Le skill formalise l’inspection préalable, le choix des outils, les confirmations
des opérations destructives, la vérification des résultats et les prompts pour
les scènes, animations, caméras, matériaux, avatars et rendus.

## Test commun

Après avoir démarré le serveur dans iClone, demander à l’agent :

> Utilise mc-iclone8-mcp. Vérifie la connexion, liste les outils disponibles,
> puis liste les objets de la scène sans rien modifier.

L’agent doit commencer par `ping_iclone` ou `get_api_version` et ne doit pas
créer, supprimer ou animer d’objet pour ce test.
