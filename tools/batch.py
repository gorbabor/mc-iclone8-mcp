"""Run several MCP tool calls in a single main-thread dispatch.

Each normal tool call crosses the HTTP boundary and waits for its own iClone
main-thread turn. For scripted sequences (writing many keyframes, loading a
motion chain) that per-call overhead dominates. run_batch executes the whole
list inside one dispatch turn, so N operations cost one round trip and one
main-thread handoff instead of N.
"""


def register(registry):
    # Close over the shared registry dict; by call time every tool is present
    # regardless of module registration order.
    def run_batch(args):
        calls = args.get("calls")
        if not isinstance(calls, list) or not calls:
            raise ValueError("calls must be a non-empty list of {name, arguments}")
        stop_on_error = args.get("stop_on_error", True)
        results = []
        for index, call in enumerate(calls):
            name = call.get("name")
            entry = {"index": index, "name": name}
            tool = registry.get(name)
            if tool is None:
                entry["error"] = "Unknown tool: %s" % name
            else:
                try:
                    # Handlers already run on iClone's main thread here (run_batch
                    # is dispatched there), so call directly without re-dispatching.
                    entry["result"] = tool["handler"](call.get("arguments", {}))
                except Exception as error:
                    entry["error"] = str(error)
            results.append(entry)
            if "error" in entry and stop_on_error:
                break
        return {"count": len(results), "results": results, "stopped_early": len(results) < len(calls)}

    registry["run_batch"] = {
        "handler": run_batch,
        "main_thread": True,
        "description": "Exécute plusieurs appels d'outils en une seule bascule vers le thread iClone. calls = liste de {name, arguments}. Bien plus rapide pour le traitement par lot (clés d'animation, motions). stop_on_error (défaut true) interrompt à la première erreur.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "calls": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "arguments": {"type": "object"},
                        },
                        "required": ["name"],
                    },
                },
                "stop_on_error": {"type": "boolean"},
            },
            "required": ["calls"],
        },
    }
