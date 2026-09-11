---
status: open
owner: Chiquetin
updated: 2026-09-02
source: OSV API (https://api.osv.dev), scanned against poetry.lock
---

# Dependency Vulnerability Report — 2026-09-02

Scanned 199 packages from `poetry.lock` against the OSV database.  
**18 packages affected** (9 %); 0 API errors.

---

## Summary by priority

| Priority | Packages |
|---|---|
| HIGH (upgrade now) | gitpython, pillow, mistune, tornado, urllib3, starlette, lxml, msgpack, soupsieve, nbconvert |
| MODERATE | bleach, filelock, idna, requests, setuptools, pytest |
| LOW / unknown | pygments, click |

---

## HIGH — immediate action required

### gitpython 3.1.45 — 22 advisories

Fix: upgrade to **≥ 3.1.51**

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-rpm5-65cw-6hj4 | CVE-2026-42215 | Command injection via Git options bypass |
| GHSA-2f96-g7mh-g2hx | CVE-2026-67325 | Bypass of CVE-2026-42215 fix via long-option prefix abbreviation |
| GHSA-mv93-w799-cj2w | CVE-2026-67326 | Newline injection in `config_writer()` enabling RCE via `core.hooksPath` |
| GHSA-v87r-6q3f-2j67 | CVE-2026-44244 | Newline injection in `config_writer().set_value()` enabling RCE |
| GHSA-7545-fcxq-7j24 | CVE-2026-44243 | Path traversal via reference APIs allowing arbitrary file write/delete |
| GHSA-4gmw-gg2m-w46p | CVE-2026-76219 | Unguarded `git read-tree` option forwarding (arbitrary file overwrite) |
| GHSA-9rj7-rf2p-w77r | CVE-2026-76218 | Unguarded `Repo.init` forwarding enabling RCE via `--template` clone hooks |
| GHSA-hmq2-w58f-27jc | CVE-2026-76222 | Arbitrary Git repository creation via unvalidated `.gitmodules` submodule name |
| *(14 further advisories at HIGH/MODERATE)* | | |

---

### pillow 10.4.0 — 17 advisories

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-6r8x-57c9-28j4 | CVE-2026-59199 | Heap OOB write via signed coordinate overflow in `paste()`/`crop()` |
| GHSA-xj96-63gp-2gmr | CVE-2026-59197 | Heap OOB write in `ImageFilter.RankFilter` via integer overflow |
| GHSA-pwv6-vv43-88gr | CVE-2026-42311 | OOB write with invalid PSD tile extents (integer overflow) |
| GHSA-cfh3-3jmp-rvhc | CVE-2026-25990 | OOB write when loading PSD images |
| GHSA-whj4-6x5x-4v2j | CVE-2026-40192 | FITS GZIP decompression bomb |
| GHSA-4x4j-2g7c-83w6 | CVE-2026-55798 | `WindowsViewer.get_command()` OS command injection via unescaped shell path |
| *(11 further advisories)* | | |

---

### mistune 3.1.4 — 14 advisories

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-4j32-57v6-6g45 | CVE-2026-59925 | HIGH: Quadratic-time parsing on long `**x**` emphasis runs |
| GHSA-c8j7-8cv4-2xmq | CVE-2026-59922 | HIGH: Quadratic-time parsing on `~~x~~`, `==x==`, `^^x^^` |
| GHSA-ffq3-xpv3-j92q | CVE-2026-59928 | HIGH: Quadratic parsing on repeated reference-link definitions |
| GHSA-qcq2-496w-v96p | CVE-2026-49851 | HIGH: DoS via quadratic-time parsing in `parse_link_text` |
| GHSA-8mp2-v27r-99xp | CVE-2026-33079 | HIGH: ReDoS in `LINK_TITLE_RE` |
| GHSA-r4rv-85jg-w4mf | CVE-2026-59924 | MODERATE: Arbitrary file read via Include directive path traversal |
| *(8 further MODERATE: XSS in math plugin, directives, heading IDs)* | | |

---

### tornado 6.5.2 — 11 advisories

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-3x9g-8vmp-wqvf | CVE-2026-49853 | Authorization header forwarded across cross-origin redirects |
| GHSA-c98p-7wgm-6p64 | CVE-2025-67725 | Quadratic DoS via repeated header coalescing |
| GHSA-jhmp-mqwm-3gq8 | CVE-2025-67726 | Quadratic DoS via crafted multipart parameters |
| GHSA-mgf9-4vpg-hj56 | CVE-2026-49855 | AsyncHTTPClient accumulates decompressed chunks without size limit (gzip bomb) |
| GHSA-fqwm-6jpj-5wxc | CVE-2026-35536 | Cookie attribute injection via `RequestHandler.set_cookie` |
| GHSA-qjxf-f2mg-c6mc | CVE-2026-31958 | DoS via too many multipart parts |
| GHSA-8423-8fgw-73vq | — | Multipart `split()` memory amplification before `max_parts` check |
| GHSA-pr2v-jx2c-wg9f | CVE-2025-67724 | Header injection and XSS via `reason` argument |
| GHSA-pw6j-qg29-8w7f | — | CurlAsyncHTTPClient leaks per-request credentials on handle reuse |
| GHSA-78cv-mqj4-43f7 | CVE-2026-35536 | Incomplete cookie attribute validation |
| GHSA-cx3h-4qpv-8hc9 | CVE-2026-49854 | LOW: Out-of-bounds memory access via C extension |

---

### urllib3 2.6.0 — 3 advisories (all HIGH)

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-38jv-5279-wg99 | CVE-2026-21441 | Decompression-bomb safeguards bypassed when following HTTP redirects |
| GHSA-mf9v-mfxr-j63j | CVE-2026-44432 | Decompression-bomb safeguards bypassed in parts of the streaming API |
| GHSA-qccp-gfcp-xxvc | CVE-2026-44431 | Sensitive headers forwarded across origins in proxied low-level redirects |

---

### starlette 0.49.1 — 5 advisories

| Advisory | CVE | Severity | Summary |
|---|---|---|---|
| GHSA-82w8-qh3p-5jfq | CVE-2026-54283 | HIGH | `request.form()` limits silently ignored for `application/x-www-form-urlencoded`, enabling DoS |
| GHSA-wqp7-x3pw-xc5r | CVE-2026-48818 | HIGH | SSRF and NTLM credential theft via UNC paths in `StaticFiles` on Windows |
| GHSA-86qp-5c8j-p5mr | CVE-2026-48710 | MODERATE | Missing Host header validation poisons `request.url.path`, bypassing path-based security checks |
| GHSA-x746-7m8f-x49c | CVE-2026-48817 | MODERATE | Arbitrary HTTP method dispatched to `HTTPEndpoint` via `getattr` |
| GHSA-jp82-jpqv-5vv3 | CVE-2026-54282 | LOW | Unvalidated request path concatenated into authority poisons `request.url.hostname` |

---

### lxml 6.0.1 — 1 advisory

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-vfmq-68hx-4jfw | CVE-2026-41066 | HIGH: Default config of `iterparse()` and `ETCompatXMLParser()` allows XXE to local files |

---

### msgpack 1.1.1 — 1 advisory

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-6v7p-g79w-8964 | CVE-2026-57585 | HIGH: OOB read / crash on `Unpacker` reuse after a caught error |

---

### soupsieve 2.8 — 2 advisories (both HIGH)

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-2wc2-fm75-p42x | CVE-2026-49476 | Memory exhaustion via large comma-separated selector lists |
| GHSA-836r-79rf-4m37 | CVE-2026-49477 | ReDoS via selector parser |

---

### nbconvert 7.16.6 — 3 advisories

| Advisory | CVE | Severity | Summary |
|---|---|---|---|
| GHSA-xm59-rqc7-hhvf | CVE-2025-53000 | HIGH | Uncontrolled search path → unauthorized code execution on Windows |
| GHSA-4c99-qj7h-p3vg | CVE-2026-39377 | MODERATE | Arbitrary file write via path traversal in cell attachment filenames |
| GHSA-7jqv-fw35-gmx9 | CVE-2026-39378 | MODERATE | Arbitrary file read via path traversal in HTMLExporter image embedding |

---

## MODERATE

### bleach 6.2.0 — 2 advisories

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-8rfp-98v4-mmr6 | — | URI sanitization allows disallowed URI schemes with Unicode > U+00A0 |
| GHSA-gj48-438w-jh9v | — | `clean()`/`Cleaner()` fails to sanitize dangerous URI schemes in `formaction` attributes |

### filelock 3.19.1 — 2 advisories

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-w853-jp5j-5j7f | CVE-2025-68146 | TOCTOU race allows symlink attacks during lock file creation |
| GHSA-qmgc-5h2g-mvrw | CVE-2026-22701 | TOCTOU symlink vulnerability in `SoftFileLock` |

### idna 3.10 — 1 advisory

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-65pc-fj4g-8rjx | CVE-2026-45409 | Crafted inputs to `idna.encode()` bypass CVE-2024-3651 fix |

### requests 2.32.5 — 1 advisory

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-gc5v-m9x4-r6x2 | CVE-2026-25645 | Insecure temp file reuse in `extract_zipped_paths()` |

### setuptools 80.9.0 — 1 advisory

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-h35f-9h28-mq5c | CVE-2026-59890 | `MANIFEST.in` exclusion bypass via Unicode normalization (NFC/NFD) on macOS APFS/HFS+ |

### pytest 8.4.2 — 1 advisory

| Advisory | CVE | Summary |
|---|---|---|
| GHSA-6w46-j5rx-g56g | CVE-2025-71176 | Vulnerable `tmpdir` handling |

---

## LOW / unknown

| Package | Advisory | CVE | Summary |
|---|---|---|---|
| pygments 2.19.2 | GHSA-5239-wwwm-4pmq | CVE-2026-4539 | ReDoS via inefficient regex for GUID matching |
| click 8.1.8 | PYSEC-2026-2132 | CVE-2026-7246 | No public summary yet |

---

## Recommended action

```
poetry update gitpython pillow mistune tornado urllib3 starlette lxml msgpack soupsieve nbconvert
```

Run `pip-audit` (or re-query OSV) after upgrading to confirm all advisories are resolved before closing this report. Update `status` to `resolved` and record the resolving commit.
