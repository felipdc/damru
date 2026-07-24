# Test Suite

> Part of **Damru** — the open-source, Android-native stealth browser automation framework (Redroid + Playwright + CDP) for web scraping, automation testing, and anti-bot / fingerprinting research.

*Test suite for the Damru open-source browser automation framework.*

Damru has two kinds of tests:

- Fast unit tests that do not need Android, Docker, Redroid, ADB, GPU access, or live websites.
- Environment probes that exercise real WSL/Linux Docker, Redroid, ADB, Chrome, GPU spoofing, fingerprinting sites, and network behavior.

Default pytest runs only the fast unit tests and skips environment-heavy probes:

```bash
python -m pytest -q
```

Run the live probes only when the machine has the required Linux/WSL Redroid environment ready:

```bash
python -m pytest --run-damru-probes -q
```

Useful focused checks:

```bash
python -m pytest tests/test_preflight_cli.py -q
python -m pytest tests/test_images_unit.py tests/test_root_webrtc.py -q
python -m damru check preflight --json --no-adb
python -m damru check-env --viewer
python -m damru fix-wsl
```

Manual probe scripts can still be run directly with `python tests/<script>.py` when you intentionally want a live browser/device check.

---

## Related

- [Main README](../README.md)
- [Verification Proof](../docs/PROOF.md)
- [Browser Benchmark Report](../docs/BROWSERS_BENCHMARK_REPORT.md)
- [Contributing Guide](../CONTRIBUTING.md)

<sub>Keywords: Android browser automation · stealth automation · antidetect · web scraping · Redroid · Playwright · CDP · fingerprinting research</sub>
