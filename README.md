# ⚡ CompileViz — Mini Compiler with Visual GUI Semester 5 final Project (Compiler Construction Subject)

> A full end-to-end compiler for **MiniLang** with an animated, browser-based interface showing every compilation phase in real time.

---

## 🖥️ Screenshots / Features

| Feature | Description |
|---|---|
| 🔤 **Token Stream** | Color-coded animated token chips |
| 🌳 **AST Visualizer** | Interactive SVG tree diagram |
| 📋 **Symbol Table** | Live-populated variable/function registry |
| ⚙️ **3-Address Code** | Intermediate representation |
| 🐍 **Python Output** | Runnable generated Python code |
| ⚠️ **Error Console** | Phase-tagged error & warning messages |

---

## 🚀 How to Run

### Step 1 — Install Python
Make sure Python 3.8+ is installed.
```bash
python --version
```

### Step 2 — Install Dependencies
Open a terminal in the `CompileViz` folder:
```bash
pip install flask
```

### Step 3 — Run the Server
```bash
python app.py
```

### Step 4 — Open in Browser
Open your browser and go to:
```
http://localhost:5000
```

That's it! 🎉

---

## 📁 Project Structure

```
CompileViz/
│
├── app.py                  ← Flask web server (entry point)
├── gui.html                ← Full browser GUI (dark theme IDE)
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
│
└── compiler/               ← Core compiler modules
    ├── __init__.py
    ├── lexer.py            ← Phase 1: Tokenizer
    ├── parser.py           ← Phase 2: Recursive Descent Parser
    ├── semantic.py         ← Phase 3: Semantic Analyzer
    └── codegen.py          ← Phase 4: Code Generator
```

---

## 🧠 MiniLang — Supported Language Features

### Data Types
```
int     → integers       (e.g. int x = 10;)
float   → decimals       (e.g. float pi = 3.14;)
string  → text           (e.g. string name = "Ali";)
bool    → true/false     (e.g. bool flag = true;)
```

### Control Flow
```
if (condition) { ... } else { ... }
while (condition) { ... }
for (int i = 0; i < 10; i = i + 1) { ... }
```

### Functions
```
func add(int x, int y) {
    return x + y;
}
```

### I/O
```
print(value);
```

### Operators
```
Arithmetic: + - * / %
Comparison: == != < > <= >=
Logical:    && ||
```

### Comments
```
// This is a comment
```

---

## 🔬 Compiler Phases

### Phase 1: Lexer (Tokenizer)
- Reads source code character by character
- Produces a stream of typed tokens
- Handles keywords, identifiers, literals, operators, delimiters
- Reports unknown characters as errors

### Phase 2: Parser (Syntax Analysis)
- Recursive descent parser
- Builds an Abstract Syntax Tree (AST)
- Supports full expression hierarchy (precedence, associativity)
- Error recovery: skips to next statement on error

### Phase 3: Semantic Analyzer
- Scope-aware symbol table (supports nested scopes)
- Undeclared variable detection
- Type mismatch warnings
- Function definition tracking

### Phase 4: Code Generator
- Generates Three-Address Code (TAC/IR)
- Generates equivalent Python code
- Handles labels, temporaries, jumps

---

## 💡 Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + Enter` | Compile code |
| `Tab` | Insert 4 spaces in editor |

---

## 🧪 Example Programs

### Hello World
```
string msg = "Hello, World!";
print(msg);
```

### Fibonacci
```
func fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}
int result = fibonacci(10);
print(result);
```

### Bubble Sort
```
int a = 64;
int b = 34;
int c = 25;
if (a > b) {
    int temp = a;
    a = b;
    b = temp;
}
print(a);
print(b);
```

---

## 🛠️ Built With

- **Python 3** — Core compiler implementation
- **Flask** — Lightweight web server
- **Vanilla JS** — GUI (no frameworks, pure JS)
- **SVG** — AST tree visualization
- **JetBrains Mono + Space Grotesk** — Fonts

---

## 📝 License
Built for academic demonstration — Compiler Construction Course Project.
