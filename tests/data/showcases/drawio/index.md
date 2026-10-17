# draw.io

```{drawio-figure} _figures/1.drawio
1.drawio
```

```{figure} _figures/2.drawio.svg
2.drawio.svg
```

```{figure} _figures/3.drawio.png
3.drawio.png
```

```{drawio-figure} _figures/4.drawio

4.draw no page selected
```

```{drawio-figure} _figures/4.drawio
:page-name: a

4.drawio page a
```

```{drawio-figure} _figures/4.drawio
:page-name: b

4.drawio page b
```

```{drawio-figure} _figures/4.drawio
:page-name: c

4.drawio page c
```

```{drawio-figure} _figures/5.drawio

5.drawio No layers selected
```

```{drawio-figure} _figures/5.drawio
:layer-selection: 0

5.drawio layers: indexes 0
```

```{drawio-figure} _figures/5.drawio
:layer-selection: 1

5.drawio layers: indexes 1
```

```{drawio-figure} _figures/5.drawio
:layer-selection: 2

5.drawio layers: indexes 2
```

```{drawio-figure} _figures/5.drawio
:layer-selection: 0,1

5.drawio layers: indexes 0,1
```

```{drawio-figure} _figures/5.drawio
:layer-selection: 0,2

5.drawio layers: indexes 0,2
```

```{drawio-figure} _figures/5.drawio
:layer-selection: 1,2

5.drawio layers: indexes 1,2
```

```{drawio-figure} _figures/5.drawio
:layer-selection: 0,1,2

5.drawio layers: indexes 0,1,2
```


## Inline diagrams

Diagrams embedded directly in Markdown as fenced `drawio` blocks.

```drawio
<mxfile host="app.diagrams.net">
  <diagram id="d" name="Page-1">
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

Locked:

```drawio locked
<mxfile host="app.diagrams.net">
  <diagram id="d" name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Locked" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
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

Height:

```drawio height=300
<mxfile host="app.diagrams.net">
  <diagram id="d" name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Height" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
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

Locked and height:

```drawio locked height=300
<mxfile host="app.diagrams.net">
  <diagram id="d" name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="LockedHeight" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
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

Same content again:

```drawio
<mxfile host="app.diagrams.net">
  <diagram id="d" name="Page-1">
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

Compressed:

```drawio
<mxfile><diagram id="c" name="Page-1">jZFBDoMgEEVPwx4h6QFKW1dd9QSkTIQEhABWvX1RxhoXJl2QzPzH/xkGwoWb2iiDfnoFlvA74SJ6n2vlJgHWEkaNIvxGGKPlEPY4oc1KaZAR+vyPgVXDR9oBqiK8CxFSAlVRyrNFFP3QK1icDeHXUZsMryDfCx3LC4qms7OIMRhihul0uFXCyVrwDnKcyxU04Ox0PrajUVmjf9M0mE5j6AU1mWrf/YL3RZQCd7G1+85XdviSLw==</diagram></mxfile>
```

Multipage (first page is rendered):

```drawio
<mxfile>
  <diagram id="d" name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="P1" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
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

  <diagram id="d" name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="P2" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
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

An ordinary code fence stays a code block:

```xml
<note>plain XML</note>
```
