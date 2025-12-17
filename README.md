🏥 Healthcare Assistant Chatbot
📌 Overview

The Healthcare Assistant Chatbot is a Python-based application designed to provide preliminary health guidance based on user-reported symptoms. The system interacts with users through both a console interface and a graphical user interface (GUI), analyzes symptoms using a structured medical dataset, and suggests possible health conditions along with basic precautions.

⚠️ Disclaimer: This system is not a medical diagnosis tool. It is intended for educational purposes only and should not replace professional medical consultation.

 Problem Statement:

In many cases, individuals ignore early symptoms of illnesses or lack immediate access to basic medical guidance. This can delay proper treatment and increase health risks. There is a need for an easy-to-use system that can provide initial health insights based on symptoms entered by the user.

🎯 Objectives:

To develop an interactive chatbot for preliminary health assessment

To analyze user-entered symptoms and predict possible medical conditions

To provide precautionary advice based on predicted conditions

To design both console-based and GUI-based user interfaces

To build a modular and extensible system for future enhancements

🧠 System Architecture

The system consists of the following major components:

User Interface

Console-based chatbot

GUI-based chatbot using Tkinter

Healthcare Engine

Symptom normalization

Symptom-to-disease matching

Confidence score calculation

Severity estimation

Precaution recommendation

Dataset

Symptom–disease mapping dataset (CSV)

Symptom descriptions

Symptom severity levels

Precaution guidelines

Synonym mapping (JSON)

Output Layer

Diagnosis result

Confidence score

Matched and missing symptoms

Description and precautions

🛠️ Technologies Used

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

📊 Dataset Description
The system uses structured medical datasets in CSV format, where:
Each row represents a disease case

Each column (except the last) represents a symptom (binary: 0/1)

The final column represents the prognosis (disease name)

Additional datasets include:

symptom_description.csv – disease descriptions

symptom_precaution.csv – recommended precautions

symptom_severity.csv – severity levels of symptoms

synonyms.json – mapping of symptom synonyms

⚙️ How the System Works

The user enters symptoms (comma-separated)

Symptoms are cleaned, normalized, and mapped using synonyms

The engine compares user symptoms with stored disease profiles

A confidence score is calculated based on symptom overlap and severity

The most likely condition is identified

Description and precautions are displayed to the user

If confidence is low, the system safely reports “Unknown Condition”

▶️ How to Run the Project
🔹 Console Version
python source_code/main_console.py

🔹 GUI Version
python source_code/mvp_gui.py


Make sure the data folder exists inside source_code and contains all required CSV and JSON files.

⚠️ Limitations

The system relies on predefined datasets and does not learn dynamically

Accuracy depends on the completeness of symptoms entered by the user

The chatbot does not replace professional medical diagnosis

Rare diseases may not be accurately predicted
