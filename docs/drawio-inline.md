<!-- Draft text for the Hermesbaby documentation (hermesbaby.github.io). Not part of the docs build. -->

# Inline diagrams in Markdown

Instead of a separate `.drawio` file, you can embed a diagram as XML in a fenced block with the language `drawio`:

````markdown
```drawio locked height=300
<mxfile host="app.diagrams.net">
  <diagram id="example" name="Architecture">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Frontend" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="20" y="20" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Backend" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="220" y="20" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" edge="1" source="2" target="3" parent="1" style="endArrow=block;html=1;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```
````

No configuration is needed. Hermesbaby renders the block with the same draw.io pipeline as `{drawio-figure}`: SVG for HTML and PDF for LaTeX/PDF builds.

## Editing

In VS Code Insiders with the [Draw.io Integration](https://github.com/hediet/vscode-drawio) extension, the block opens as a graphical editor in the Markdown WYSIWYG editor. Changes are written back into the Markdown file.

## Fence attributes

- `locked`: the editor is read-only.
- `height=N`: height of the editor viewport in pixels.

Both are editor-only and do not change the published diagram size. Other attributes are an error.

## Versus `{drawio-figure}`

Inline blocks are plain images with no caption, label or numbering, and the XML lives in the Markdown file. Use `{drawio-figure}` or `{drawio-image}` with a `.drawio` file when you need captions, cross-references, or page/layer selection and export options.

## Limitations

- Only the first page of a multipage diagram is rendered.
- Malformed XML, a missing `<mxfile>` or `<diagram>`, `DOCTYPE`/`ENTITY` declarations, and content over 5 MB fail the build with the file and line.
- Builders: HTML and LaTeX/PDF (via the configured `drawio_builder_export_format`).
