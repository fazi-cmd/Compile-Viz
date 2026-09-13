"""
CompileViz Web Server
Flask backend serving the GUI and compilation API.
"""

from flask import Flask, request, jsonify, render_template_string
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.semantic import analyze
from compiler.codegen import generate

app = Flask(__name__)

# ─── HTML Template ────────────────────────────────────────────────────────────

HTML = open(os.path.join(os.path.dirname(__file__), 'gui.html')).read()


@app.route('/')
def index():
    return HTML


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route('/api/compile', methods=['POST'])
def compile_code():
    data = request.json
    source = data.get('source', '')

    result = {
        'tokens': [],
        'ast': None,
        'symbols': [],
        'tac': [],
        'python': [],
        'errors': [],
        'warnings': [],
        'success': False
    }

    try:
        # Phase 1: Lexing
        tokens, lex_errors = tokenize(source)
        result['tokens'] = [t.to_dict() for t in tokens]
        result['errors'].extend([{**e, 'phase': 'Lexer'} for e in lex_errors])

        if tokens:
            # Phase 2: Parsing
            try:
                ast, parse_errors = parse(tokens)
                result['ast'] = ast.to_dict()
                result['errors'].extend([{**e, 'phase': 'Parser'} for e in parse_errors])

                # Phase 3: Semantic Analysis
                try:
                    symbols, sem_errors, warnings = analyze(ast)
                    result['symbols'] = symbols
                    result['errors'].extend([{**e, 'phase': 'Semantic'} for e in sem_errors])
                    result['warnings'] = warnings

                    # Phase 4: Code Generation
                    try:
                        tac, python_code = generate(ast)
                        result['tac'] = tac
                        result['python'] = python_code
                        result['success'] = len(result['errors']) == 0
                    except Exception as e:
                        result['errors'].append({'message': f'Code gen error: {str(e)}', 'phase': 'CodeGen'})
                except Exception as e:
                    result['errors'].append({'message': f'Semantic error: {str(e)}', 'phase': 'Semantic'})
            except Exception as e:
                result['errors'].append({'message': f'Parse error: {str(e)}', 'phase': 'Parser'})

    except Exception as e:
        result['errors'].append({'message': f'Fatal error: {str(e)}', 'phase': 'Lexer'})

    return jsonify(result)


@app.route('/api/examples', methods=['GET'])
def get_examples():
    examples = {
        'fibonacci': '''// Fibonacci sequence
func fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int result = fibonacci(10);
print(result);''',

        'bubble_sort': '''// Bubble sort demo
int a = 64;
int b = 34;
int c = 25;

if (a > b) {
    int temp = a;
    a = b;
    b = temp;
}

if (b > c) {
    int temp2 = b;
    b = c;
    c = temp2;
}

print(a);
print(b);
print(c);''',

        'factorial': '''// Factorial with while loop
int n = 5;
int result = 1;
int i = 1;

while (i <= n) {
    result = result * i;
    i = i + 1;
}

print(result);''',

        'calculator': '''// Simple calculator
func add(int x, int y) {
    return x + y;
}

func multiply(int x, int y) {
    return x * y;
}

int a = 10;
int b = 5;
int sum = add(a, b);
int product = multiply(a, b);

print(sum);
print(product);''',

        'grade': '''// Grade checker
int score = 85;
string grade = "F";

if (score >= 90) {
    grade = "A";
} else {
    if (score >= 80) {
        grade = "B";
    } else {
        if (score >= 70) {
            grade = "C";
        } else {
            grade = "F";
        }
    }
}

print(grade);'''
    }
    return jsonify(examples)


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  CompileViz - Mini Compiler with Visual GUI")
    print("="*50)
    print("  Open your browser at: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=False, port=5000)
