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

### Command line

```bash
python calculator.py "2+3*4"     # prints 14
python calculator.py             # interactive mode
```


## How it works

sidi-calc/
├── calculator.py        # safe expression engine (ast-based, no eval)
├── server.py            # stdlib HTTP server: static files + POST /api/calculate
├── static/
│   ├── index.html       # the souk
│   ├── style.css        # blue-and-white styling
│   └── app.js           # keys, keyboard, history
├── test_calculator.py
└── test_server.py



