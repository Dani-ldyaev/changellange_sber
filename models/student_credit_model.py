class StudentCreditModel:
     def predict(self, data):
          # Логика предсказания модели
          # Пример: просто возвращаем True, если возраст больше 18 лет
          if data["age"] >= 18:
               return True
          else:
               return False
