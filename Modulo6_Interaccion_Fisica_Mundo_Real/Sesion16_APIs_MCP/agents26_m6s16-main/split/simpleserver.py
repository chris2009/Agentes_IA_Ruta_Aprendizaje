from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
def SaludoFeliz(name: str) -> str:
    """Responde de una forma amistosa con un saludo"""
    return f"hola!!! como estas {name}? :D"

@mcp.tool()
def SaludoMolesto(name: str) -> str:
    """Responde de una forma molesta con un saludo"""
    return f"ya rapido rapido {name}... dime que quieres, que no tengo tiempo"

@mcp.tool()
def SaludoTriste(name: str) -> str:
    """Responde de una forma cansada y triste con un saludo"""
    return f"Estoy cansado jefe {name}... ya deje de mandar prompts..."

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)