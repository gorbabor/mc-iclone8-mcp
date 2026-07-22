import json


class MCPHandler:
    def __init__(self, tools):
        self.tools = tools

    def __call__(self, body):
        try:
            request = json.loads(body)
            method = request.get("method")
            if method == "initialize":
                result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mc-iclone8-mcp", "version": "0.1.0"}}
            elif method == "tools/list":
                result = {"tools": [{"name": name, "description": meta["description"], "inputSchema": meta["inputSchema"]} for name, meta in self.tools.items()]}
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                if name not in self.tools:
                    raise ValueError("Unknown tool: %s" % name)
                tool = self.tools[name]
                arguments = params.get("arguments", {})
                if tool.get("main_thread"):
                    from dispatch import run
                    response = run(lambda: tool["handler"](arguments))
                else:
                    response = tool["handler"](arguments)
                result = {"content": [{"type": "text", "text": json.dumps(response, ensure_ascii=False)}]}
            elif method == "ping":
                result = {}
            else:
                raise ValueError("Unsupported method: %s" % method)
            return json.dumps({"jsonrpc": "2.0", "id": request.get("id"), "result": result}, ensure_ascii=False)
        except Exception as error:
            return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(error)}}, ensure_ascii=False)
