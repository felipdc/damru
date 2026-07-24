# Scripts

> Part of **Damru** — the open-source, Android-native stealth browser automation framework (Redroid + Playwright + CDP) for web scraping, automation testing, and anti-bot / fingerprinting research.

*Utility scripts for the Damru open-source browser automation framework.*

Standalone maintenance utilities for Damru development, proof capture, and image preparation.

## `bake_image.py`

Builds a warm `damru-redroid:latest` Docker image from the base Redroid image. It boots a temporary Redroid container, installs Chrome/TTS/native assets, prepares warm Chrome preferences, commits the result, and removes the temporary container.

Use it only inside Linux or WSL2:

```bash
python scripts/bake_image.py --image-name damru-redroid:latest
docker save damru-redroid:latest -o damru-redroid-latest.tar
sha256sum damru-redroid-latest.tar > damru-redroid-latest.tar.sha256
```

The CLI equivalent is:

```bash
python -m damru bake-image --image damru-redroid:latest
```

The exported `.tar` is intentionally ignored by Git because it is large. Keep `damru-redroid-latest.tar.sha256` with the release artifact.

## `capture_proof.py`

Captures sanitized viewport screenshots for proof targets such as Amazon, Foot Locker/DataDome, Fingerprint Pro, Sannysoft, and CreepJS.

Runtime proxy values are read from environment variables only:

```bash
DAMRU_PROXY='socks5://user:pass@host:port' \
DAMRU_HTTP_PROXY='172.17.0.1:18888' \
python scripts/capture_proof.py --device pixel_8_pro --out docs/assets/proof/sites
```

Do not hardcode proxy credentials in this repo.

## `socks_http_bridge.py`

Local HTTP CONNECT bridge for proof runs where Android needs an unauthenticated HTTP proxy but the upstream proxy is authenticated SOCKS5.

```bash
UPSTREAM_PROXY='socks5://user:pass@host:port' \
python scripts/socks_http_bridge.py --listen 0.0.0.0 --port 18888
```

This helper stores no credentials; credentials come from the runtime environment.

---

## Related

- [Browser Benchmark Report](../docs/BROWSERS_BENCHMARK_REPORT.md)
- [Verification Proof](../docs/PROOF.md)
- [Main README](../README.md)
- [Image & APK Readiness](../docs/IMAGE_AUTOPULL_FIX.md)

<sub>Keywords: Android browser automation · stealth automation · antidetect · web scraping · Redroid · Playwright · CDP · fingerprinting research</sub>
