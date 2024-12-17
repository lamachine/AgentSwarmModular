from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.box import ROUNDED

console = Console()

def print_assistant_response(text):
    console.print()  # Add a blank line before the assistant's response
    md = Markdown(text)
    console.print(Panel(md, border_style="green", box=ROUNDED, expand=False, title="AI Agent", title_align="left"))
    console.print()  # Add a blank line after the assistant's response

def print_system_message(text):
    console.print()  # Add a blank line before the system message
    system_text = Text(text, style="yellow")
    console.print(Panel(system_text, border_style="yellow", box=ROUNDED, expand=False, title="System", title_align="left"))
    console.print()  # Add a blank line after the system message

def print_code(code, language="python"):
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(Panel(syntax, border_style="red", box=ROUNDED, expand=False, title=f"Code ({language})", title_align="left"))

def print_tool_usage(tool_name):
    console.print(f"\n🔧 [bold blue]Tool Used:[/bold blue] {tool_name}")

def clear_screen():
    console.clear()

def print_welcome_message():
    welcome_text = Text.from_markup("""
[bold magenta]Welcome to the AI Agent Chat![/bold magenta]

[bold cyan]Available Commands:[/bold cyan]
• [yellow]reset[/yellow] - Start a new conversation
• [yellow]quit[/yellow]  - Exit the program
""")
    console.print(Panel(welcome_text, border_style="magenta", box=ROUNDED, expand=False))
    console.print()

def print_divider():
    console.print("─" * console.width, style="dim")

def get_user_input():
    user_input = console.input("\n[bold cyan]You:[/bold cyan] ")  # Add a newline before the prompt
    console.print()  # Add a blank line after the user's input
    return user_input
