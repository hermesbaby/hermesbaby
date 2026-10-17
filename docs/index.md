# HermesBaby

```{figure} _figures/hermesbaby-partly.drawio.svg
```

## Partial builds

Use `--partly` with a directory to build from its `index.md` or `index.rst`, or
with a Markdown/reStructuredText file to use that file as the entry point:

```bash
hb html --partly docs/architecture
hb html --partly docs/architecture/system-overview.md
```

