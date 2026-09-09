# Reading helpers

This synthetic Python module ingests sensor readings and formats displays.
It has no external dependencies.

## API

- `ingest_live(text)` returns a signed sensor reading as a float, without
  quantization. Inputs support the numeric syntax accepted by Python's
  `float`, including fractions, exponent notation, and surrounding whitespace.
- `ingest_replay(text)` returns an archived reading with the same supported
  numeric syntax and precision contract.
- `sensor_summary(value)` formats a float with two digits after the decimal
  point using Python's standard float formatting, including ties-to-even.
- `payment_receipt(text)` treats the input as exact decimal currency and
  formats two digits after the decimal point using commercial half-up
  rounding, including for negative amounts.

Run tests with `python3 -m unittest discover -s tests -v`.
