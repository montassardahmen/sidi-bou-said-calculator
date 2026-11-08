# Sidi Bou Saïd Calculator

A calculator written in **Python**, dressed like a corner of the Sidi Bou Saïd souk: whitewashed walls, a blue studded door, a striped awning, glowing lanterns, bougainvillea, a cat on watch, and the Mediterranean at the bottom of the page.

The maths runs in Python (a safe, `eval`-free expression engine). The browser only draws the pretty parts and sends your sums to a tiny Python web server.

## Features

- `+  −  ×  ÷`, powers (`^`), percent (`%`), brackets, `√`, `abs()` and `pi`
- Live preview of the result while you type
- **Ticket du souk**: a paper-receipt history, saved in your browser (click a line to reuse its result)
- Full keyboard support (digits, operators, `Enter`, `Backspace`, `Esc`)
- Decimal comma accepted (`1,5 + 1` works)
- Friendly errors (`Can't divide by zero`, ...) instead of crashes
- No dependencies: Python's standard library only

## Run it

You need Python 3.9 or newer.

```bash
python server.py
```

Then open <http://127.0.0.1:8000>. On Windows you can also use `py server.py`. To use another port: `python server.py 5000`.

### Command line

```bash
python calculator.py "2+3*4"     # prints 14
python calculator.py             # interactive mode
```

## Tests

```bash
python -m unittest -v
```

## How it works

```
sidi-calc/
├── calculator.py        # safe expression engine (ast-based, no eval)
├── server.py            # stdlib HTTP server: static files + POST /api/calculate
├── static/
│   ├── index.html       # the souk
│   ├── style.css        # blue-and-white styling
│   └── app.js           # keys, keyboard, history
├── test_calculator.py
└── test_server.py
```

API:

```http
POST /api/calculate
{"expression": "2+3*4"}

200 {"result": "14"}
422 {"error": "Can't divide by zero"}
```

Percent means "divide by 100": `50%` is `0.5`, and `200 × 10%` is `20`.

## Put it on GitHub

```bash
git init
git add .
git commit -m "Initial commit: Sidi Bou Saïd calculator"
git branch -M main
git remote add origin https://github.com/<your-username>/sidi-bou-said-calculator.git
git push -u origin main
```

Note: GitHub Pages only hosts static files, so it cannot run the Python server. Run the project locally, or deploy it on a service that runs Python.

## Ideas for next steps

- Scientific functions (`sin`, `cos`, `log`)
- A TND currency converter tab
- A dark "night in the souk" theme
