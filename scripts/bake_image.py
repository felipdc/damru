"""Bake a pre-configured damru-redroid Docker image.

Run once to create a custom image with Chrome, eSpeak, fonts, resetprop
pre-installed. Then set REDROID_IMAGE in config.py to use it.

Usage:
    python bake_image.py [--image-name damru-redroid:latest] [--chrome-apk path] [--extra-system-ca ca.pem]

This saves ~20-30s on every cold start.
"""
import argparse
import asyncio
import sys

sys.path.insert(0, ".")
from damru.docker import RedroidManager


async def main():
    parser = argparse.ArgumentParser(description="Bake damru-redroid Docker image")
    parser.add_argument(
        "--image-name", default="damru-redroid:latest",
        help="Name for the baked image (default: damru-redroid:latest)",
    )
    parser.add_argument(
        "--chrome-apk", default=None,
        help="Path to Chrome APK or split-APK directory",
    )
    parser.add_argument(
        "--extra-system-ca",
        "--mitm-ca-cert",
        dest="extra_system_ca",
        action="append",
        default=None,
        help="PEM CA certificate to bake into Android system CA stores; repeatable",
    )
    args = parser.parse_args()

    mgr = RedroidManager()
    image = await mgr.bake_image(
        chrome_apk=args.chrome_apk,
        image_name=args.image_name,
        extra_system_ca_certs=args.extra_system_ca,
    )
    print(f"\nDone! Set this in damru/config.py:")
    print(f'  REDROID_IMAGE = "{image}"')


if __name__ == "__main__":
    asyncio.run(main())
