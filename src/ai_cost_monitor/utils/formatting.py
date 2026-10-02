"""Human-friendly table and number formatting for console reports."""

from ai_cost_monitor import constants


def format_seconds(seconds: float) -> str:
    """Render seconds either in milliseconds or seconds, whichever is readable."""
    if seconds < 1.0:
        return f"{seconds * constants.MILLIS_PER_SECOND:.0f} ms"
    return f"{seconds:.2f} s"


def format_usd(amount: float | None) -> str:
    """Render a per-million-token price, tolerating unknown values."""
    if amount is None:
        return "n/a"
    return f"${amount:.4f}"


def format_percent(value: float | None) -> str:
    """Render a discount percentage, tolerating unknown values."""
    if value is None:
        return "n/a"
    return f"{value:.0f}%"


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a plain-text table with aligned columns (no third-party deps)."""
    column_widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            column_widths[index] = max(column_widths[index], len(cell))

    def _format_row(cells: list[str]) -> str:
        padded = [cell.ljust(column_widths[index]) for index, cell in enumerate(cells)]
        return " | ".join(padded)

    separator = "-+-".join("-" * width for width in column_widths)
    lines = [_format_row(headers), separator]
    lines.extend(_format_row(row) for row in rows)
    return "\n".join(lines)
