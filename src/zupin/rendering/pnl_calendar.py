from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class PnlDay:
    day: date
    realized_pnl: Decimal
    fees: Decimal
    gas: Decimal


def _font(size: int) -> ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def render_pnl_calendar(*, user_id: str, snapshot_id: str, month: date, days: list[PnlDay]) -> bytes:
    """Render a deterministic PNG from canonical ledger-derived rows.

    The renderer never reads live chain/provider data. Input rows and snapshot_id
    must already be produced by the accounting layer.
    """
    rows = sorted((row for row in days if row.day.year == month.year and row.day.month == month.month), key=lambda r: r.day)
    width, row_height = 900, 54
    height = 150 + max(1, len(rows)) * row_height
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = _font(24)
    body_font = _font(16)

    draw.text((30, 22), f"Zupin PnL Calendar — {month:%Y-%m}", fill="black", font=title_font)
    draw.text((30, 58), f"User: {user_id}    Snapshot: {snapshot_id}", fill="black", font=body_font)
    draw.text((30, 92), "Date", fill="black", font=body_font)
    draw.text((180, 92), "Realized PnL", fill="black", font=body_font)
    draw.text((370, 92), "Fees", fill="black", font=body_font)
    draw.text((560, 92), "Gas", fill="black", font=body_font)
    draw.text((710, 92), "Net", fill="black", font=body_font)

    y = 120
    for row in rows:
        net = row.realized_pnl + row.fees - row.gas
        draw.text((30, y), row.day.isoformat(), fill="black", font=body_font)
        draw.text((180, y), f"{row.realized_pnl}", fill="black", font=body_font)
        draw.text((370, y), f"{row.fees}", fill="black", font=body_font)
        draw.text((560, y), f"{row.gas}", fill="black", font=body_font)
        draw.text((710, y), f"{net}", fill="black", font=body_font)
        y += row_height

    draw.text((30, height - 26), "Source: canonical ledger snapshot; no live provider data used.", fill="black", font=body_font)

    output = BytesIO()
    image.save(output, format="PNG", optimize=False, compress_level=9)
    return output.getvalue()
