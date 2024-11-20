from flask import Flask, render_template, request, jsonify
import locale
import re
import math

app = Flask(__name__)
locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')

MIN_VALUE = -1000000000000.0000000000
MAX_VALUE = 1000000000000.0000000000

current_result = 0


def check_overflow(number):
    return number < MIN_VALUE or number > MAX_VALUE


def parse_number(number_str):
    if not number_str:
        return 0.0
    number_str = number_str.replace(',', '.')
    number_str = number_str.strip()
    try:
        return float(number_str)
    except ValueError:
        return None


def arithmetic_round(number, decimals=10):
    factor = 10 ** decimals
    return math.copysign(int(abs(number) * factor + 0.5) / factor, number)


def format_result(number):
    formatted_number = arithmetic_round(number, 10)
    formatted_number = str(formatted_number)
    formatted_number = formatted_number.rstrip('0').rstrip('.') if '.' in formatted_number else formatted_number
    return formatted_number.replace(",", " ")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    global current_result

    number1 = parse_number(request.form.get('number1'))
    operation1 = request.form.get('operation1')
    number2 = parse_number(request.form.get('number2'))
    operation2 = request.form.get('operation2')
    number3 = parse_number(request.form.get('number3'))
    operation3 = request.form.get('operation3')
    number4 = parse_number(request.form.get('number4'))

    if None in [number1, number2, number3, number4]:
        return jsonify({'error': 'Invalid input'})

    if check_overflow(number1) or check_overflow(number2) or check_overflow(number3) or check_overflow(number4):
        return jsonify({'error': 'Overflow'})

    try:
        intermediate_result = eval(f"{number2} {operation2} {number3}")
        if check_overflow(intermediate_result):
            return jsonify({'error': 'Overflow'})
        intermediate_result = arithmetic_round(intermediate_result)
        result = eval(f"{number1} {operation1} {intermediate_result} {operation3} {number4}")
        if check_overflow(result):
            return jsonify({'error': 'Overflow'})
    except ZeroDivisionError:
        return jsonify({'error': 'Division by zero'})
    except Exception as e:
        return jsonify({'error': f'Calculation error: {e}'})

    if check_overflow(result):
        current_result = 0
        return jsonify({'error': 'Overflow'})
    else:
        current_result = arithmetic_round(result, 10)
        return jsonify({'result': format_result(current_result)})


@app.route('/round', methods=['POST'])
def round_result():
    global current_result

    data = request.get_json()
    rounding_method = data.get('method')

    if rounding_method == 'math':
        rounded = arithmetic_round(current_result, 0)
    elif rounding_method == 'banking':
        rounded = round(current_result)
    elif rounding_method == 'truncate':
        rounded = math.trunc(current_result)
    else:
        return jsonify({'error': 'Invalid rounding method'})

    return jsonify({'rounded': rounded})


if __name__ == '__main__':
    app.run(debug=True)
