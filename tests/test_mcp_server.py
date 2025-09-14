import importlib


def test_mcp_server_registers_sort_tool():
    """Smoke test: importing the MCP server should register a `sort` tool

    This test imports `dispatcher.mcp_server` and calls the `sort` function
    exposed on the module. The implementation delegates to
    `dispatcher.package_dispatcher.sort` which is already covered by other
    tests; here we only assert that the MCP module exposes the function and
    that it returns the expected classification for a small package.
    """

    m = importlib.import_module("dispatcher.mcp_server")

    # The module should expose an MCP tool named `sort`
    assert hasattr(m, "sort"), "mcp_server should expose a 'sort' attribute"

    # The MCP library wraps tools in a FunctionTool object which exposes a
    # `run` method to execute the underlying function. Call that.
    tool = m.sort
    assert hasattr(tool, "run"), "mcp_server.sort should expose a run() method"

    # Call the tool and ensure it returns the expected stack. fastmcp wraps
    # the original callable on `fn`; prefer calling that directly for a
    # simple smoke test. If it's missing, try calling `run` with kwargs.
    if hasattr(tool, "fn") and callable(tool.fn):
        result = tool.fn(10, 10, 10, 1)
    else:
        # `run` sometimes expects a single dict/input, try kwargs form.
        result = tool.run(width=10, height=10, length=10, mass=1)
    assert result == "STANDARD"
