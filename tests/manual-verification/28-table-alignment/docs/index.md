# Issue 28

[Issue 28](https://github.com/hermesbaby/hermesbaby/issues/28)

## Matter

Table alignment doesn't work.

## Test Data

### Table without directive

| left-aligned | center-aligned | right-aligned |
|:-------------|:--------------:|--------------:|
| a            |       b        |             c |
| d            |       e        |             f |

### Table with directive

```{table}
| left-aligned | center-aligned | right-aligned |
|:-------------|:--------------:|--------------:|
| a            |       b        |             c |
| d            |       e        |             f |
```

## Test steps

- Execute `hb html`
- Investigate output: Expected: The alignments are correct in both tables.

## Test outcome

PASS: The alignments are correct in both tables.
