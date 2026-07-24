# Image and APK Readiness

> Part of **Damru** — the open-source, Android-native stealth browser automation framework (Redroid + Playwright + CDP) for web scraping, automation testing, and anti-bot / fingerprinting research.

*Setup for Android-native browser automation on WSL2.*

Status: implemented. Current users should prefer the documented CLI flow instead of manually pulling Redroid images.

## Recommended Flow

```bash
python -m damru install-deps -y
python -m damru install-image
python -m damru check preflight
python -m damru check-env
```

`install-image` loads or downloads the baked `damru-redroid:latest` image. The baked image is the recommended path because Chrome, WebView/TTS assets, fonts, warm preferences, and native assets are already inside the container image.

The published tarball is exported from a clean Redroid base with Damru assets applied once. If you rebake, make sure `bake-image --image damru-redroid:latest` starts from the configured Redroid base image, not an older `damru-redroid:latest`, or the tarball will grow from stale stacked layers.

## Raw/Unbaked Flow

Use this only for baking, debugging, or APK recovery:

```bash
python -m damru install-apks --download
python -m damru bake-image --image damru-redroid:latest
docker save damru-redroid:latest -o damru-redroid-latest.tar
sha256sum damru-redroid-latest.tar > damru-redroid-latest.tar.sha256
python -m damru install-image --tar damru-redroid-latest.tar
python -m damru quick-check --serial 127.0.0.1:5600
```

The APK installer extracts to `/home/damru/chrome-apks` by default and validates:

- Chrome split-APK version folders
- Matching per-version `webview.apk` or `TrichromeWebView.apk` for folders used by Chrome rotation
- `google_tts.apk`
- `espeak.apk`
- `rhvoice.apk`
- Damru's packaged `magisk.apk` when raw Redroid needs a local `resetprop` source

Random profile actions rotate only through Chrome version folders with a matching WebView APK. Folders without a matching WebView asset are skipped so Chrome and Android WebView do not drift apart.

During install or bake, Damru replaces the Redroid system WebView APK with the matching bundle WebView, fixes ownership/permissions to `root:root 0644`, and clears stale WebView oat/dalvik-cache files. This avoids Android rejecting the provider as a writable dex file and keeps WebView Shell/custom WebView harnesses on the same Chromium engine as Chrome.

Explicit Chrome pinning is strict:

```bash
python -m damru force-profile --serial 127.0.0.1:5600 --device pixel_8_pro --rotate-chrome --chrome-version 148.0.7778.217
```

The command only succeeds when that version folder has a matching `webview.apk` or `TrichromeWebView.apk`.

## Readiness Checks

`python -m damru check preflight` is fast and read-only. It does not install packages, pull/load images, mount binderfs, start containers, edit iptables, or change `.wslconfig`. Use `--json` for automation:

```bash
python -m damru check preflight --json --timeout 3
```

`python -m damru check-env` is slower and deeper. It verifies setup details such as Docker, binderfs, image/APK discovery, ADB, Playwright patching, and optional viewer tooling.

## Failure Handling

- Missing baked image: run `python -m damru install-image`.
- Missing raw APKs: run `python -m damru install-apks --download`.
- WSL Docker/binderfs/network issue: run `python -m damru fix-wsl`.
- Worker DNS/internet issue: run `python -m damru fix-internet --all`.
- Unsupported Debian/custom kernel: use Ubuntu 24.04 or a binderfs-enabled kernel.

---

## Related

- [Chrome APK Bundle](../chrome-apks/README.md)
- [Main README](../README.md)
- [Automation Status & Roadmap](AUTOMATION_GAPS_PLAN.md)
- [WSL2 Kernel Notes](WSL_KERNEL.md)

<sub>Keywords: Android browser automation · stealth automation · antidetect · web scraping · Redroid · Playwright · CDP · fingerprinting research</sub>
