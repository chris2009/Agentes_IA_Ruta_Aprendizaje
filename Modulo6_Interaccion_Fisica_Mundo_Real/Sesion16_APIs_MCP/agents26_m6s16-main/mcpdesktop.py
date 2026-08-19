# DEMO Simple integrando a Claude
# ------------------------------------
# Para agregar el MCP Server a Claude Desktop
# desde git bash o terminal ejecutamos este comando:
# uv run mcp install mcpdesktop.py y reiniciar Claude App

from fastmcp import FastMCP
import os


NOTES_FILE = os.path.join(os.path.dirname(__file__), "notasIA.txt")

def ensure_file():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("")

mcp = FastMCP("NotasIA")

# Instrucciones son mejor interpretadas en ingles especialmente para modelos de Anthropic
# Ejemplo> Haiku, Sonnet, opus
@mcp.tool()
def add_note(message : str) -> str:
    """
    Append a new note to the sticky note file.
    Args:
        message (str): the note content to be added
    Returns:
        str: Confirmation message indicating the note was saved.
    """
    ensure_file()
    with open(NOTES_FILE, "a") as f:
        f.write(message + "\n")
    return "Nota guardada!"

@mcp.tool()
def read_note() -> str:
    """
    Read and return all the notes from the sticky note file.

    Returns:
        str: all the notes as a single string separated by line breaks.
        if no notes exists, a default message is returned.
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        content = f.read().strip()
    return content if content else "No notes yet."

@mcp.resource("notes://latest")
def get_latest_note() -> str:
    """
    Read the latest note from the sticky note file.

    Returns:
        str: the latest notes as a single string.
        if no notes exists, a default message is returned.
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        lines = f.readlines
    return lines[-1].strip() if lines else "No notes yet."

@mcp.prompt()
def note_summary_prompt() -> str:
    """
    Generate a prompt asking the AI to summarize all the notes

    Returns: a Summary of all the notes in the sticky note file
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        content = f.read().strip()
    if not content:
        return "No notes yet."
    return f"Summarize current notes: "+{content}
