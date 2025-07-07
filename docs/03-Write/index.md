(sec_write)=
# Write

## Getting Started

## Become Advanced

(sec_write_diagrams_drawio)=
### Diagrams with draw.io

(a) Simple:

````markdown
```{drawio-figure} _figures/some_diagram.drawio
```
````

(b) With some caption:

````markdown
```{drawio-figure} _figures/some_diagram.drawio
Some Caption
```
````

(c) With a label for cross-referencing:

````markdown
(fig_some_diagram)=
```{drawio-figure} _figures/some_diagram.drawio
Some Caption
```

The diagram {ref}`fig_some_diagram` illustrates ...

As we can see in {numref}`fig_some_diagram`, ...
````

(d) Overriding format:

````markdown
```{drawio-figure} _figures/some_diagram.drawio
:format: svg
```
````

Possible values: `svg`, `png`

The document's default figure image format can be set in the configuration, see {ref}`sec_configure`.
