from datetime import date
from decimal import Decimal
from hashlib import sha256

from PIL import Image
from io import BytesIO

from zupin.rendering import PnlDay, render_pnl_calendar


def _fixture() -> list[PnlDay]:
    return [
        PnlDay(date(2026, 9, 1), Decimal("1.25"), Decimal("0.40"), Decimal("0.05")),
        PnlDay(date(2026, 9, 2), Decimal("-0.50"), Decimal("0.20"), Decimal("0.03")),
    ]


def test_pnl_renderer_is_deterministic() -> None:
    kwargs = {"user_id": "fixture-user", "snapshot_id": "snapshot-001", "month": date(2026, 9, 1), "days": _fixture()}
    first = render_pnl_calendar(**kwargs)
    second = render_pnl_calendar(**kwargs)
    assert first == second
    assert sha256(first).hexdigest() == sha256(second).hexdigest()


def test_pnl_renderer_produces_png_with_snapshot_trace() -> None:
    data = render_pnl_calendar(
        user_id="fixture-user",
        snapshot_id="snapshot-001",
        month=date(2026, 9, 1),
        days=_fixture(),
    )
    image = Image.open(BytesIO(data))
    assert image.format == "PNG"
    assert image.width == 900
    assert image.height > 150
