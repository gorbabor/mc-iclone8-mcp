import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp_handler import MCPHandler


class TestMCPHandler(unittest.TestCase):
    def setUp(self):
        self.handler = MCPHandler({
            "hello": {
                "handler": lambda args: {"message": "hello " + args.get("name", "world")},
                "description": "Test tool",
                "inputSchema": {"type": "object", "properties": {}},
            }
        })

    def call(self, method, params=None):
        return json.loads(self.handler(json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}})))

    def test_initialize(self):
        self.assertEqual(self.call("initialize")["result"]["serverInfo"]["name"], "mc-iclone8-mcp")

    def test_list_tools(self):
        self.assertEqual(self.call("tools/list")["result"]["tools"][0]["name"], "hello")

    def test_call_tool(self):
        response = self.call("tools/call", {"name": "hello", "arguments": {"name": "iClone"}})
        content = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(content["message"], "hello iClone")

    def test_unknown_tool(self):
        self.assertIn("Unknown tool", self.call("tools/call", {"name": "missing"})["error"]["message"])


if __name__ == "__main__":
    unittest.main()
