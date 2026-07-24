# Tools & Assets (`tools/`)

> Part of **Damru** — the open-source, Android-native stealth browser automation framework (Redroid + Playwright + CDP) for web scraping, automation testing, and anti-bot / fingerprinting research.

*Development tools for Android-native browser automation research.*

This directory contains external tools, assets, and third-party binaries used for Android environment research and development.

---

## Contents

### `magisk.apk`

Provided for developers who want to manually explore the Redroid container, debug root access, or install custom Magisk modules during research phases.

> **Note:** Users do not need to provide Magisk separately for normal setup. Damru ships `magisk.apk` as a package asset, copies it into the local APK bundle when needed, and raw/unbaked Redroid uses it only as a local source for extracting standalone `resetprop`. Damru does not download Magisk from third-party APK sites at runtime.

---

Do not commit sensitive keys or large unmodified third-party binaries here unless they are required for the build or release pipeline.

---

## Related

- [Chrome APK Bundle](../chrome-apks/README.md)
- [Main README](../README.md)
- [Native Binaries](../native/README.md)
- [Damru Core Library](../damru/README.md)

<sub>Keywords: Android browser automation · stealth automation · antidetect · web scraping · Redroid · Playwright · CDP · fingerprinting research</sub>
