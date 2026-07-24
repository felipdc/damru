# Changelog

All notable changes to the **Damru** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Part of **Damru** ? the open-source, Android-native stealth browser automation framework (Redroid + Playwright + CDP) for web scraping, automation testing, and anti-bot / fingerprinting research.

## [0.1.0] - 2026-06-20

### Added
- **SEO/AEO Optimizations**: Updated README and documentation files with entity context lines, internal "Related" cross-links, and keyword footers.
- **Repository Metadata**: Added CITATION.cff, .github/FUNDING.yml, and .github/workflows/unit-tests.yml (CI).
- **Packaging Upgrades**: Added project URLs, keywords, classifiers, license, and richer description to `pyproject.toml` (version unchanged).

### Changed
- Re-formatted top sections of the README to improve alignment and layout of badges and introductory definitions.

---

## [0.0.9] - 2026-06-17

### Fixed
- **WebRTC Spoof Leak**: Fixed WebRTC leak protection by replacing kernel UDP blocking with `remove_webrtc_block()`. iptables DROP rules are removed and Chrome flag changed from `default_public_interface_only` to `default_public_and_private_interfaces` so WebRTC discovers the real proxy exit IP instead of appearing disabled.
- **Timezone Resolver**: Fixed timezone resolution bugs under proxies.
- **WebGL Model Spoofing**: Corrected WebGL model strings emulation.
- **Hardware Profile Hardening**: Patched Tensor-G3 cores emulation signatures.
- **OS Images**: Updated pre-baked `damru-redroid-latest` OS image checksums.

---

## [0.0.8] - 2026-06-16

### Fixed
- **Asset Search**: Resolved local `chrome-apks.zip` path prioritization.
- **Boot warnings**: Made missing touchscreen warnings non-fatal during headless device boots.

---

## [0.0.7] - 2026-06-15

### Added
- **Global Bundle Auto-detection**: Automatically detect local `chrome-apks` bundle or ZIP inside the `Downloads/damru` folder when running globally to prevent unnecessary downloads.
- **UI Server Public Exposure**: Added a `--host` parameter to the UI server to support public host exposure.
- **UI Unit Tests**: Added comprehensive unit tests for UI server backend helper functions.
- **GPU Control**: Added support for dynamic GPU profile switching.

### Changed
- **Hatchling Migration**: Migrated Python build-system backend to Hatchling from setup.py and untracked `damru.egg-info`.
- **Base OS Image**: Changed default download URL for Redroid image to `https://dl.damru.dev/assets/damru-baked.tar.gz`.

### Fixed
- Cache issues with reloading configuration in UI, listing native devices in non-auto modes, and checking `com.android.chromium` package readiness.
- Resolved pip install packaging conflicts.

---

## [0.0.6] - 2026-06-14

### Added
- **WebRTC Protection**: Added optional WebRTC leak protection (default proxy IP spoofing, opt-in kernel block) and a new `--webrtc-spoof` option.
- **Stealth Open URL Defaults**: Made `stealth-open-url` default to `--mode reattach` (apply full Damru stealth, detach CDP for native Chrome navigation, then reconnect). `--mode cdp`, `--mode native`, and `--mode playwright` remain available.

### Fixed
- Version matching for Chrome flags with the installed Chrome executable in `random-profile` CLI.
- Stop container before committing during image baking to avoid OverlayFS commit race.
- Fixed Crashpad crash issues, persistent ADB keys, and WSL path translation for assets.
- Fixed `disable-breakpad` flag and `su_root` adb execution method.

---

## [0.0.5] - 2026-06-13

### Added
- **WebView Shell Hardening**: Added `force-profile --browser-package org.chromium.webview_shell` to write WebView command-line/preferences, apply native memory preloads, and align props/timezone/locale.
- **Profile Database Expansion**: Expanded built-in profiles database from 51 to 155 devices by importing 104 additional validated profiles.
- **Premium Profile Pool**: Added a 100-profile premium tier selection pool for default random profiles.

### Changed
- Changed default stealth opener to `--mode reattach` (detach CDP for native Chrome navigation, then reconnect).
- Relocated default download URLs to `damru.dev` and refactored `install-image` command.

### Fixed
- WebView version match relaxation, wsl serial compatibility, and sensor HAL grace period.
- Fixed locale assertions with batched props in test suites.

---

## [0.0.4] - 2026-06-12

### Added
- **Default Experimental Features**: Enabled experimental features by default (`DAMRU_EXPERIMENTAL_CDP_SENSORS`, `DAMRU_EXPERIMENTAL_BATTERY_DUMPSYS`, `DAMRU_EXPERIMENTAL_SENSOR_HAL`, `DAMRU_ENABLE_NATIVE_SENSOR_HAL`, `DAMRU_EXPERIMENTAL_HIDL_SENSOR_HAL`).
- **Persistent Workers**: Preserved Redroid docker containers across workspace restarts.
- **Subprocess reaping**: Cleaned up timed-out subprocesses in ADB and Docker operations.
- **Stealth APIs**: Navigator properties (`navigator.credentials`, `navigator.serviceWorker`, `navigator.mediaDevices`, `navigator.bluetooth`, `navigator.usb`, `navigator.storage`, `navigator.keyboard`) verified working on HTTPS pages.

### Changed
- Playwright `crPage.js` patcher now modifies Playwright in-place.
- Precomputed mobile User-Agent during `_chrome_prep()`: UA + Client Hints metadata are written to Chrome's native command line via `--user-agent=` flag.

### Fixed
- Removed WebView hard requirement from `find_chrome_apk` (fall back to system WebView).
- Relaxed APK bundle validation (warn instead of fail for missing WebView/TTS assets).

---

## [0.0.3-beta] - 2026-06-09

### Added
- WebView Shell DevTools socket support.
- APK Matrix validation across multiple Chrome and WebView versions.

### Fixed
- Authenticated proxy routing and local proxy bridge.

---

## [0.0.2-beta] - 2026-06-05

### Added
- Initial Damru local UI control panel dashboard, setup guides, and log pages.
- Native memory spoofing via per-Chrome wrap property and `libfakemem`.

---

## [0.0.1-beta] - 2026-06-02

### Added
- Initial beta automation stack including WSL kernel natfix, check-env, and setup routines.

---

## Related

- [Main README](README.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Automation Status & Roadmap](docs/AUTOMATION_GAPS_PLAN.md)
- [Verification Proof](docs/PROOF.md)

<sub>Keywords: Android browser automation ? stealth automation ? antidetect ? web scraping ? Redroid ? Playwright ? CDP ? fingerprinting research</sub>
