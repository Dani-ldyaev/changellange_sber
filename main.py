from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    flash,
    url_for,
    app,
)
import json
from pathlib import Path


# from adapters.giga_chat_adapter import GigaChatAdapter

app.secret_key = "SECRET_KEY"
# app.config["sessions"]["secret_key"] = app.secret_key

# Создаем приложение Flask
app = Flask(__name__)

# Загрузка JSON-схем
with open(Path("schemas/application_schema.json"), "r", encoding="utf-8") as f:
    application_schema = json.load(f)

with open(Path("schemas/model_schema.json"), "r", encoding="utf-8") as f:
    model_schema = json.load(f)

with open(Path("schemas/credit_bureau_schema.json"), "r", encoding="utf-8") as f:
    credit_bureau_schema = json.load(f)

with open(
    Path("schemas/education_committee_resource_schema.json"), "r", encoding="utf-8"
) as f:
    education_committee_resource_schema = json.load(f)


# Главная страница
@app.route("/")
def home():
    return render_template("index.html")


# Ввод данных
@app.route("/model-selection", methods=["GET", "POST"])
def model_selection():
    if request.method == "POST":
        # Получаем данные из формы
        model_schema = request.form.get("schema")
        input_data = request.form.get("input_data")

        # Проверяем, что данные пришли корректно
        if model_schema and input_data:
            # Сохраняем данные в сессии
            session["model_schema"] = model_schema
            session["input_data"] = input_data

            flash("Данные успешно сохранены в сессии.")
            return redirect(url_for("evaluate_student"))
    else:
        flash("Не удалось сохранить данные в сессии. Попробуйте повторить операцию.")
        return redirect(url_for("model-selection"))

    return render_template("model_selection.html", model_schema=model_schema)


# Отправка данных для оценки студента
# @app.route("/evaluate-student", methods=["POST"])
# def evaluate_student():
#     # Получаем данные от клиента
#     data = request.get_json()

#     # Создаем объект адаптера
#     adapter = GigaChatAdapter(
#         data["model_name"], data["schema"], data["transformations"]
#     )

#     # Оцениваем студента
#     score = adapter.evaluate_student(data["input_data"])

#     # Возвращаем результат
#     return jsonify(score)


# Страница для ввода и отправки готовых схем
@app.route("/submit-schemas", methods=["GET", "POST"])
def submit_schemas():
    if request.method == "POST":
        # Получаем данные из форм
        application_schema = request.form.get("application_schema")
        model_schema = request.form.get("model_schema")
        credit_bureau_schema = request.form.get("credit_bureau_schema")
        education_committee_resource_schema = request.form.get(
            "education_committee_resource_schema"
        )

        # Обработка схем и передача их на GigaChat API
        cleaned_data = process_schemas(
            application_schema,
            model_schema,
            credit_bureau_schema,
            education_committee_resource_schema,
        )

        # Возвращаем результат
        return jsonify(cleaned_data)

    return render_template("submit_schemas.html")


# # Функция для обработки схем
# def process_schemas(
#     application_schema,
#     model_schema,
#     credit_bureau_schema,
#     education_committee_resource_schema,
# ):
#     # Здесь идет обработка схем и передача их на GigaChat API
#     # Возвращаем очищенные данные
#     return {"cleaned_data": "Замените это на реальный результат"}


if __name__ == "__main__":
    app.run(debug=True)
