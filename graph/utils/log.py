import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# Custom theme for consistent colors
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "stage": "bold magenta",
    "progress": "bold blue",
    "debug": "dim white",
})

console = Console(theme=custom_theme)

# Configure logging with RichHandler
logging.basicConfig(
    level="INFO",  # Default level; can be set to DEBUG for verbose
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, show_time=True, show_level=True, show_path=False, markup=True)]
)

logger = logging.getLogger("estiMate")

# Helper for success/info/warning/error/stage/progress/debug with icons
def log_success(msg):
    logger.info(f":heavy_check_mark: [success]{msg}[/success]")

def log_warning(msg):
    logger.warning(f":warning: [warning]{msg}[/warning]")

def log_error(msg):
    logger.error(f":x: [error]{msg}[/error]")

def log_stage(msg):
    logger.info(f":rocket: [stage]{msg}[/stage]")

def log_progress(msg):
    logger.info(f":hourglass_flowing_sand: [progress]{msg}[/progress]")

def log_info(msg):
    logger.info(f":information_source: [info]{msg}[/info]")

def log_debug(msg):
    logger.debug(f":bug: [debug]{msg}[/debug]")

# Section header/panel

def log_panel(msg, title=None, style="stage"):
    console.print(Panel(msg, title=title, style=style))

# Table output

def log_table(headers, rows, title=None):
    table = Table(title=title)
    for h in headers:
        table.add_column(h)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)

# Markdown output

def log_markdown(md):
    console.print(Markdown(md))

# Usage: from graph.utils.log import logger, log_success, log_warning, log_error, log_stage, log_progress, log_info, log_debug, log_panel, log_table, log_markdown
