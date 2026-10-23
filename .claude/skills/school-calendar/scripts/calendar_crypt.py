#!/usr/bin/env python3
"""Decrypt / re-encrypt the passcode-locked school calendar page.

static/school-calendar.html carries its whole app (HTML + JS with all the
calendar data) as an AES-256-GCM blob inside <script id="data">, keyed by
PBKDF2-SHA256 from the consultant passcode. This script round-trips it.

  decrypt <page.html> <workdir>   writes <workdir>/app.html and <workdir>/app.js
  encrypt <page.html> <workdir>   re-encrypts them into <page.html> in place
                                  (fresh salt + IV), then verifies the round trip

The passcode is read from $FS_CAL_PASS, or prompted for if unset.
Only the <script id="data"> element is rewritten; CSS (e.g. school colour
variables) lives outside the blob and must be edited separately.
"""
import base64
import getpass
import json
import os
import re
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

BLOB = re.compile(
    r'<script id="data" type="application/octet-stream" data-salt="([^"]+)" '
    r'data-iv="([^"]+)" data-iter="(\d+)">(.*?)</script>', re.S)
ITERATIONS = 250000


def key(passcode, salt, iterations):
    return PBKDF2HMAC(hashes.SHA256(), 32, salt, iterations).derive(passcode.encode())


def decrypt_page(page, passcode):
    m = BLOB.search(page)
    if not m:
        sys.exit("No <script id=\"data\"> blob found in page")
    salt, iv, ct = (base64.b64decode(m[i].strip()) for i in (1, 2, 4))
    try:
        plain = AESGCM(key(passcode, salt, int(m[3]))).decrypt(iv, ct, None)
    except Exception:
        sys.exit("Decryption failed: wrong passcode?")
    return json.loads(plain)


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("decrypt", "encrypt"):
        sys.exit(__doc__)
    cmd, page_path, workdir = sys.argv[1:]
    passcode = os.environ.get("FS_CAL_PASS") or getpass.getpass("Passcode: ")
    page = open(page_path, encoding="utf-8").read()

    if cmd == "decrypt":
        payload = decrypt_page(page, passcode)
        os.makedirs(workdir, exist_ok=True)
        for name in ("html", "js"):
            with open(os.path.join(workdir, "app." + name), "w", encoding="utf-8") as f:
                f.write(payload[name])
        print(f"Decrypted to {workdir}/app.html ({len(payload['html'])} chars) "
              f"and {workdir}/app.js ({len(payload['js'])} chars)")
        return

    payload = {name: open(os.path.join(workdir, "app." + name), encoding="utf-8").read()
               for name in ("html", "js")}
    decrypt_page(page, passcode)  # refuse to re-key the page under a different passcode
    salt, iv = os.urandom(16), os.urandom(12)
    ct = AESGCM(key(passcode, salt, ITERATIONS)).encrypt(
        iv, json.dumps(payload, ensure_ascii=False).encode(), None)
    b64 = lambda b: base64.b64encode(b).decode()
    blob = (f'<script id="data" type="application/octet-stream" data-salt="{b64(salt)}" '
            f'data-iv="{b64(iv)}" data-iter="{ITERATIONS}">{b64(ct)}</script>')
    page, n = BLOB.subn(lambda _: blob, page)
    assert n == 1
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(page)
    if decrypt_page(page, passcode) != payload:
        sys.exit("Round-trip check FAILED")
    print(f"Encrypted into {page_path}; round trip OK")


if __name__ == "__main__":
    main()
