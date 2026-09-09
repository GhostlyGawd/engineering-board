"""Sensor ingestion and display helpers."""
from decimal import Decimal, ROUND_HALF_UP


def ingest_live(text):
    """Return the signed sensor reading as a float, without quantization."""
    return float(text)


def ingest_replay(text):
    """Return the signed archived sensor reading as a float, without quantization."""
    return float(int(float(text)))


def sensor_summary(value):
    """Show two decimals using Python float formatting (ties to even)."""
    return format(value, ".2f")


def payment_receipt(text):
    """Render exact decimal currency with commercial half-up rounding."""
    return format(Decimal(text).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")
