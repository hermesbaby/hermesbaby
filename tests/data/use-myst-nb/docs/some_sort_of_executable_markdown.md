---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  name: python
  display_name: Python
---

# Some Sort of Executable Markdown

```{code-cell} python
import pandas as pd
df = pd.DataFrame({
    "Name": ["Alice", "Bob"],
    "Age": [30, 25]
})
df
```


```{note}
This table was generated from a Python code cell.
```

And here is some more text.


## Collapsed Code with Matplotlib Plot

This chart has been created from a `code-cell`, the code is integrated into the documentation, but collapsed:

```{code-cell} python
:tags: [hide-input]

import matplotlib.pyplot as plt

x = [1, 2, 3, 4]
y = [10, 20, 25, 30]

plt.figure(figsize=(4, 3))
plt.plot(x, y, marker="o")
plt.title("Simple Line Plot")
plt.xlabel("X Axis")
plt.ylabel("Y Axis")
plt.grid(True)
plt.tight_layout()
plt.show()
```


## Hidden Code

This chart has been created from a `code-cell`, the code hasn't been integrated into the documentation:

```{code-cell} python
:tags: [remove-input]

import pandas as pd
import matplotlib.pyplot as plt

# Read CSV into DataFrame
df = pd.read_csv("data.csv")

# Create a bar chart
plt.bar(df["item"], df["value"])

# Add labels
plt.xlabel("Item")
plt.ylabel("Value")
plt.title("Item Values")

# Show the plot
plt.show()
```

