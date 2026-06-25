# Harden WebView runtime and baked Redroid image for Android PDP loads

Source branch: `felipdc/damru:v1.2`  
Target branch: `akwin1234/damru:v1.2`  
Compare URL: https://github.com/akwin1234/damru/compare/v1.2...felipdc:damru:v1.2

## Description

This PR hardens Damru's WebView/Redroid path so warmed Android slots present a more coherent real-device surface while preserving the project's zero-JS philosophy.

The main changes are:

- Add native WebView library patch helpers for `X-Requested-With` append paths and the Android `navigator.platform` string, with guarded/idempotent byte matching.
- Move deeper runtime identity cleanup into Android/native layers: debug props, runtime ABI/hardware props, Android ID/boot ID/proc version spoofing, proc status/maps/mountinfo filtering, native preload asset installation, and app data directory repair.
- Improve baked image support so native assets and input/sensor fixes are installed during image build instead of relying only on runtime mutations.
- Make Chrome/WebView command-line handling safer by quoting argv tokens, using the installed Chrome/WebView version in the native user agent, and allowing no-CDP WebView modes to avoid remote debugging flags.
- Relax APK bundle validation and WebView selection so missing optional assets warn instead of blocking, while system WebView fallback remains available.
- Improve operational stability around ADB subprocess cleanup, Redroid worker preservation, WSL serial handling, baked ADB bootstrap connectivity, and worker pool caps.
- Extend regression coverage for native WebView patches, image build behavior, profile application, root/app data repair, runtime prop spoofing, ADB timeout cleanup, and locale batching.

Fixes # N/A

## Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Stealth Philosophy Check

- [x] My change relies on native OS, binary, browser-engine, CDP, or Android-layer spoofing.
- [x] I have **NOT** injected JavaScript (`Object.defineProperty`, etc.) to achieve this bypass.

## Checklist

- [x] I have performed a self-review of my own code.
- [x] I have commented my code, particularly in hard-to-understand areas (C++ hooks, ADB shell commands).
- [ ] I have made corresponding changes to the documentation.
  - Not applicable for this PR; behavior is covered by focused tests and inline comments.
- [ ] I have run the benchmark suite (`python -m damru.benchmark`) and verified no regressions occurred.
  - Not run locally because it requires live Android/Redroid/browser infrastructure.

## Testing

- [x] `git diff --check origin/v1.2..HEAD`
- [x] `.venv/bin/python -m pytest -m unit`
  - Result: `120 passed, 11 deselected, 1 warning`
  - Warning was from an APK fixture intentionally missing a matching WebView asset.

## Notes for review

- The WebView native mutation paths are guarded and idempotent. Ambiguous binary signatures raise instead of patching unsafe offsets.
- Installed WebView native mutation is opt-in behind environment gates, while bake-time/native asset installation is covered separately.
- No credentials, private proxy values, private APK URLs, or live proof artifacts are included.
