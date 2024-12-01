from flask import Flask, render_template, request, jsonify
import json
import jsonschema
from datetime import date

app = Flask(__name__)

# Модель JSON схемы
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "studentData": {
            "type": "object",
            "properties": {
                "age": {"type": "number"},
                "residenceRegion": {"type": "string"},
                "averageScore": {"type": "number"},
                "profession": {"type": "string"},
                "administrativeOffense": {"type": "number"},
                "overdueLoanStudent": {"type": "number"},
            },
            "required": [
                "age",
                "residenceRegion",
                "averageScore",
                "profession",
                "administrativeOffense",
                "overdueLoanStudent",
            ],
            "additionalProperties": False,
        },
        "parentsData": {
            "type": "object",
            "properties": {
                "overdueLoanParents": {"type": "number"},
                "parentsBankruptcy": {"type": "boolean"},
            },
            "required": ["overdueLoanParents", "parentsBankruptcy"],
            "additionalProperties": False,
        },
    },
    "required": ["studentData", "parentsData"],
    "additionalProperties": False,
}


# Словарь для оценки региона
REGION_SCORES = {
    "Москва": 12.5,
    "Санкт-Петербург": 12.5,
    "Новосибирск": 12,
    "Екатеринбург": 11.5,
    "Казань": 11,
    "Нижний Новгород": 10.5,
    "Челябинск": 10,
    "Омск": 9.5,
    "Самара": 9,
    "Ростов-на-Дону": 8.5,
    "Уфа": 8,
    "Красноярск": 7.5,
    "Пермь": 7,
    "Воронеж": 6.5,
    "Волгоград": 6,
}


def calculate_age(birth_date):
    today = date.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def validate_json(data):
    print(type(data))
    try:
        jsonschema.validate(instance=data, schema=JSON_SCHEMA)
        return True
    except jsonschema.exceptions.ValidationError as err:
        print(f"Валидатор обнаружил ошибку: {err.message}")
        return False


def calculate_credit_score(data):
    score = 0

    # Возраст
    if data["studentData"]["age"] < 18:
        age_score = 0
    else:
        age_score = min((data["studentData"]["age"] - 18) * 3 + 4, 12.5)

    # Регион
    region_score = REGION_SCORES.get(data["studentData"]["residenceRegion"], 0)

    # Средний балл
    average_score = data["studentData"]["averageScore"]
    if average_score >= 5:
        avg_score = 12.5
    elif average_score >= 4:
        avg_score = 10
    elif average_score >= 3:
        avg_score = 7
    else:
        avg_score = 0

    # Специальность
    profession_score = 12.5

    # Административные нарушения
    admin_offenses = data["studentData"]["administrativeOffense"]
    admin_offense_score = max(-admin_offenses * 6.25, 0)

    # Просроченные кредиты студента
    student_loan_overdue = data["studentData"]["overdueLoanStudent"]
    student_loan_score = max(12.5 - student_loan_overdue // 10 * 5, 0)

    # Просроченные кредиты родителей
    parent_loan_overdue = data["parentsData"]["overdueLoanParents"]
    parent_loan_score = max(12.5 - parent_loan_overdue // 10 * 6, 0)

    # Банкротство родителей
    parent_bankruptcy = data["parentsData"]["parentsBankruptcy"]
    bankruptcy_score = 12.5 if not parent_bankruptcy else 0

    total_score = sum(
        [
            age_score,
            region_score,
            avg_score,
            profession_score,
            admin_offense_score,
            student_loan_score,
            parent_loan_score,
            bankruptcy_score,
        ]
    )

    return round(total_score, 2)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/data_source", methods=["GET"])
def data_source():
    return render_template("data_source.html")


@app.route("/credit_calculation", methods=["POST", "GET"])
def credit_calculation():
    if request.method == "POST":
        try:
            raw_data = request.data.decode("utf-8").strip()
            print(raw_data)
            data = json.loads(raw_data)
            print(f"Принятые данные: {data}")
            is_valid = validate_json(data)
            if is_valid:
                score = calculate_credit_score(data)
                color = "green" if score > 80 else "yellow" if score <= 80 else "red"
                result = {"score": score, "color": color}
                print(f"Результат расчета: {result}")
                return jsonify(result)
            else:
                return jsonify({"error": "Invalid JSON format"})
        except Exception as e:
            print(f"Ошибка обработки данных: {e}")
            return jsonify({"error": str(e)})
    elif request.method == "GET":
        # Отображение формы для ввода данных
        return render_template("credit_calculation.html")


if __name__ == "__main__":
    app.run(debug=True)
