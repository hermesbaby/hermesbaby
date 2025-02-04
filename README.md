# HermesBaby

The Software and Systems Engineers' Typewriter

Meant to be the authoring environment to get our work done.

## Purpose

Do our daily written communication in

- notes,
- engineering notebooks,
- software documentations,
- technical articles,
- any other kinds of specifications or
- books.


## Installation

Two options are available: System-wide or project-wise

### System-wide

While it's possible to install it globally via `pip`, it's recommended to install it via `pipx` to keep your system clean and tidy since `hermesbaby` brings many Python packages with it.


```bash
python3 -m pip install pipx
python3 -m pipx install hermesbaby
```


### Project-wise

Let's assume your project is managed with Poetry you would add `hermesbaby` similar to

```bash
poetry add hermesbaby
```

or

```bash
poetry add hermesbaby --group dev
```


## First usage

Close the gaps by installing the missing tools. You may use the help hermesbaby gave you to do so.

Beside `hermesbaby` there is a second, shorter alias:

```bash
hb
```

Check environment for prerequisites

```bash
hb check-tools
```


Start your first new virtual piece of writing

```bash
hb new hello
cd hello
hb html-live
```

CTRL-C.


Start editing

```bash
git init .
code .
```

Statusbar / html-live

Apply changes to `docs/index.md` ..

