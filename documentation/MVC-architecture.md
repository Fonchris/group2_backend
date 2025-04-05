# MVC (Model-View-Controller) architecture

---

### 🧠 **Overview**
An AI-powered translation system with:
- **Frontend**: HTML, CSS, JS (View)
- **Backend**: Firebase (Authentication), API with Controller + Service Layer(Controller)
- **Infrastructure**: AWS (Api Gateway, Lambda, SageMaker, cloudwatch, IAM roles)
- **AI Model** + Language Logic (Model)

---

## 🧩 **MVC Architecture Breakdown**

### 🔹 **1. Model**
The **Model** represents the AI translation logic and any data-handling logic.

- **Responsibilities**:
  - Hold and manage the trained AI translation model.
  - Perform the actual text translation.
  - Handle language rules, preprocessing, and post-processing if necessary.

- **Components**:
  - Trained ML/NLP models for language pairs.
  - Model wrapper/adapter (e.g., Python class or service function) that takes input text and returns translated output.

---

### 🔹 **2. View**
The **View** is the frontend—the user interface that interacts with users.

- **Technologies**:
  - HTML/CSS: for structure and design.
  - JavaScript: to handle user actions and make API requests.

- **UI Features**:
  - Input textbox (for source text).
  - Dropdowns to choose input and output languages.
  - Translate button.
  - Output textbox to show translated result.

- **Responsibilities**:
  - Collect user input (text + language selection).
  - Send a request to the backend using `fetch` or `axios`.
  - Display the translated result returned from the backend.

---

### 🔹 **3. Controller**
The **Controller** acts as a bridge between the View and the Model via the Service Layer.

- **Responsibilities**:
  - Define endpoints to receive translation requests (e.g., `/translate`).
  - Accept request payload: 
  ```
    {
        "inputText": "Hello", 
        "fromLang": "en", 
        "toLang": "gho" 
    }
    ```


  - Call the Service Layer with the parsed request.
  - Return the final response to the client.

- **Example**:
  ```python
  @app.route("/translate", methods=["POST"])
  def translate():
      data = request.get_json()
      result = translation_service.translate(data["inputText"], data["fromLang"], data["toLang"])
      return jsonify({"translatedText": result})
  ```

---

### 🔹 **4. Service Layer** (Optional but good design)
This is a separation of business logic from the controller—recommended for clean architecture.

- **Responsibilities**:
  - Process input (e.g., validate text and language codes).
  - Handle business logic like selecting the right model or translation path.
  - Call the appropriate trained AI model to perform translation.
  - Handle error cases (e.g., unsupported languages).

- **Example**:
  ```python
  def translate(input_text, from_lang, to_lang):
      # Call model based on language pair
      if from_lang == "en" and to_lang == "gho":
          return model_en_gho.translate(input_text)
      elif from_lang == "gho" and to_lang == "fr":
          return model_gho_fr.translate(input_text)
      # ...
  ```

---

## 🏗️ Diagrammatic View (Simplified)

```plaintext
[User Interface - View]
   |
   | (HTTP Request - input text, langs)
   V
[Controller - API Endpoints]
   |
   | (Calls service layer)
   V
[Service Layer]
   |
   | (Calls appropriate ML model)
   V
[Model - Translation Logic]
   |
   | (Translated text)
   V
[Service Layer → Controller → View]
   |
   | (HTTP Response - translated text)
   V
[Displayed in UI textbox]
```