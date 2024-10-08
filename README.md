﻿# ChatwithPDf

## Introduction

Our project leverages cutting-edge technology to automate survey response collection from public and proprietary documents, including PDFs and web pages. By parsing complex reports related to ESG and business aspects, our system extracts relevant data based on survey questionnaires. It also automates reference and citation recording, aiming to streamline information collection for comprehensive responses across various categories. Utilizing language models like LLM and LangChain, we ensure accurate analysis and generation of responses, further enhancing the efficiency and reliability of our solution.

## Steps to Run

1. **Create a Virtual Environment**: Set up a virtual environment to isolate the project dependencies.
   ```bash
   python -m venv venv
   ```

2. **Install Required Libraries**: Install the required libraries using the provided requirements.txt file.
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**: Execute the main.py file to start the Flask API.

   ```bash
    python main.py
   ```
## File Descriptions

### `extract_questions_questionnaire.py`

- **Purpose**: This script is responsible for extracting questions from Survey-Questionnaire PDFs.
- **Description**: It parses PDF files containing survey questionnaires and extracts questions for further processing and analysis.

### `qa.py`

- **Purpose**: This module handles the question-answering functionality.
- **Description**: It utilizes ChromeDB to store vector embeddings of ESG reports. The module performs semantic search to extract relevant content for a particular question from these reports. It then employs a language model to generate the final answer along with its citation.

### `main.py`

- **Purpose**: This is the main file where the Flask API logic is implemented.
- **Description**: It contains the routes and endpoints for the Flask application. This file orchestrates the interaction between different modules, handling incoming requests, and returning appropriate responses.

## Methodology

### Embeddings Storage

![Embeddings Storage Diagram](images/embeddings.png)

### Answer Generation

![Answer Generation Diagram](images/output_generation.png)


