# Roadmap

## Why keep going

This is the decoder-ring underneath a much bigger question: why GPS is good or bad on the routes you actually run. `[private]`'s entire accuracy model depends on this Svid → NORAD mapping being trustworthy — right now it isn't yet (hardcoded observer position, unverified matches reaching the published dataset). Fixing this repo is the highest-leverage unlock for the sibling project, not a side quest.

## What it opens up

Once verified, this becomes a durable, versioned reference dataset — not just for this repo, but for any [private] work downstream. The interesting question stops being "what satellite is Svid 7" and becomes "given this mapping is solid, what else can be derived from raw phone GNSS logs without needing new hardware" (multipath heuristics, constellation diversity scoring, per-location visibility forecasts).

## Capability this builds

Building a shared, versioned lookup table once instead of re-deriving satellite-identity logic in every downstream analysis — the data-engineering discipline of treating reference data as a product, not a one-off script output.

## Connects to

- **[private]** — direct, explicit consumer: its own roadmap names this repo's known matching bugs (azimuth wrap-around, unverified uploads, hardcoded lat/lon) as its Phase 0 blocking work.
- **[private]** — same underlying satellite-identity question, approached from the device-comparison angle.
