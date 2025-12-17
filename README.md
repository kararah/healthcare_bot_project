# 🏥 Healthcare Assistant Chatbot

A Python-based Healthcare Assistant Chatbot that provides **preliminary health guidance**
based on user-reported symptoms using a structured medical dataset.

⚠️ **Disclaimer:** This project is for **educational purposes only** and does not replace
professional medical advice.


## ❓ Problem Statement

In many cases, individuals ignore early symptoms of illnesses or lack immediate access to basic medical guidance. This can delay proper treatment and increase health risks. There is a need for an easy-to-use system that can provide initial health insights based on symptoms entered by the user.

## 🎯 Objectives:

- To develop an interactive chatbot for preliminary health assessment

- To analyze user-entered symptoms and predict possible medical conditions

- To provide precautionary advice based on predicted conditions

- To design both console-based and GUI-based user interfaces

- To build a modular and extensible system for future enhancements

## 🧠 System Architecture

The system consists of the following major components:

### User Interface
- Console-based chatbot
- GUI-based chatbot using Tkinter

### Healthcare Engine
- Symptom normalization
- Symptom-to-disease matching
- Confidence score calculation
- Severity estimation
- Precaution recommendation

### Dataset
- Symptom–disease mapping dataset (CSV)
- Symptom descriptions
- Symptom severity levels
- Precaution guidelines
- Synonym mapping (JSON)

### Output Layer
- Diagnosis result
- Confidence score
- Matched and missing symptoms
- Description and precautions

## 🛠️ Technologies Used

Programming Language: Python 3.12

Libraries & Frameworks:

pandas
tkinter
pathlib
logging
json
re (regular expressions)

Development Tools:
Visual Studio Code
Git (version control)

## 📊 Dataset Description
The system uses structured medical datasets in CSV format, where:
Each row represents a disease case

Each column (except the last) represents a symptom (binary: 0/1)

The final column represents the prognosis (disease name)

Additional datasets include:

symptom_description.csv – disease descriptions

symptom_precaution.csv – recommended precautions

symptom_severity.csv – severity levels of symptoms

synonyms.json – mapping of symptom synonyms

## ⚙️ How the System Works

The user enters symptoms (comma-separated)

Symptoms are cleaned, normalized, and mapped using synonyms

The engine compares user symptoms with stored disease profiles

A confidence score is calculated based on symptom overlap and severity

The most likely condition is identified

Description and precautions are displayed to the user

If confidence is low, the system safely reports “Unknown Condition”

## ▶️ How to Run the Project

### 1️⃣ Console Version
```bash
python source_code/main_console.py
python source_code/mvp_gui.py



Make sure the data folder exists inside source_code and contains all required CSV and JSON files.

## ⚠️ Limitations
- The system depends on predefined datasets
- It does not learn dynamically from new inputs
- Accuracy depends on the number and quality of symptoms provided
- Rare or complex conditions may not be detected

## 🚀 Future Enhancements
- Integration of machine learning models
- Natural Language Processing (NLP) for free-text symptom input
- Web-based deployment using Flask or Django
- Mobile application support
- Real-time doctor consultation integration


## 👤 Author
- **Kara Rah**  
Project – Healthcare Assistant Chatbot


## 🤝 Contributions
Contributions are welcome. If you wish to contribute, please fork the repository
and submit a pull request.
