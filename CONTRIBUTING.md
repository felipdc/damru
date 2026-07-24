# Contributing to Damru

> Part of **Damru** — the open-source, Android-native stealth browser automation framework (Redroid + Playwright + CDP) for web scraping, automation testing, and anti-bot / fingerprinting research.

*Part of the Damru open-source browser automation project.*

Thank you for considering a contribution to Damru.

## AI-Assisted Development

Damru was built with heavy AI-assisted engineering and rapid experimentation. The project has used OpenAI Codex, Kimi CLI, and other tools during research, native patching, and integration work.

AI-generated patches are welcome, but contributors are responsible for testing, reviewing, and understanding the code before submitting it.

## How to Contribute

### Reporting Bugs

If you find a bug, open an issue with:

- Target URL or benchmark name.
- OS and environment details.
- Device profile and proxy setup, with credentials removed.
- Logs with secrets, IPs, usernames, and tokens redacted.

### Suggesting Enhancements

If you know of a new fingerprinting vector or stability issue, open an issue with reproducible evidence and a minimal test case where possible.

### Code Contributions

Pull requests are welcome for noncommercial project improvement.

- Follow Damru's zero-JS philosophy. Prefer OS, binary, browser-engine, CDP, or Android-layer fixes over JavaScript monkey patches.
- Add or update tests for new spoofing behavior.
- Run the relevant pytest suite before submitting.
- Do not commit credentials, private proxies, private APK URLs, personal paths, or proof assets containing private data.
- Preserve the license, attribution, and legal notices.

## Development Setup

```bash
git clone https://github.com/akwin1234/damru.git
cd damru
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m damru install-deps -y
python -m damru check-env
```

## License

By contributing, you agree that your contribution is provided under the same license and project policy as Damru. See `LICENSE` and `LEGAL.md`.

---

## Related

- [Main README](README.md)
- [Legal Policy](LEGAL.md)
- [Security Policy](SECURITY.md)
- [Python API Reference](docs/PYTHON_API.md)
- [Test Suite](tests/README.md)

<sub>Keywords: Android browser automation · stealth automation · antidetect · web scraping · Redroid · Playwright · CDP · fingerprinting research</sub>
