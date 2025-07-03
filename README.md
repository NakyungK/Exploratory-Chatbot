# 🧠 Generative AI Exploratory Search Chatbot

This is a chatbot application built using **Gradio** and the **Anthropic Claude API**.  
It provides an interactive interface for users to engage in conversational exploratory search.

<a href="https://github.com/NakyungK/ai_explor_search" target="_blank">
🔗 View Source Code on GitHub</a>


### This tool was developed as part of the study _"A Study on the Impact of Generative AI Response Disclosure and Prompt Initiative in Exploratory Search Experience"_ and is publicly available for **paper review and reproducibility** purposes.

---

## 🌟 Features

- ✅ Supports four prompt modes: `OG`, `OS`, `PG`, and `PS`
- 🧠 Claude 3 Sonnet integration via `anthropic` SDK
- 💬 Gradio-based dynamic chat interface
- 📊 Logs all user activity (including prompts, responses, and elapsed time)
- ⬇️ One-click log download in Excel format (`.xlsx`)

---

## 🖼️ Demo Screenshot

> Here's an example of the chatbot interface in action:

<p align="center">
  <img src="screenshot/Example.png" alt="Gradio Chatbot Screenshot" width="700"/>
</p>


## 📁 Project Structure
```bash

Exploratory_Chatbot/
│
├── app.py # Main Gradio application (entry point)
├── my_prompt.py # Returns prompt based on conditions
├── my_sdk_caller.py # Calls Claude API with prompt and user input
│
├── requirements.txt
├── .gitignore 
├── README.md # Project documentation (you are here)
└── .env # 🔐 [NOT committed] contains API keys
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/NakyungK/ai_explor_search.git
cd ai_explor_search
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate      # On Windows
# OR
source .venv/bin/activate   # On macOS/Linux
```


### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

| Package         | Purpose                         |
| --------------- | ------------------------------- |
| `gradio`        | UI framework for web apps       |
| `openai`        | (Optional) compatibility layer  |
| `requests`      | API communication (general use) |
| `anthropic`     | Access Claude 3 API             |
| `python-dotenv` | Load environment variables      |
| `pandas`        | For logging and exporting data  |
| `openpyxl`      | Save logs to `.xlsx`            |


### 4. Configure API key
Create a .env file in the project root:

    ANTHROPIC_API_KEY=your-anthropic-api-key-here

### 5. Run the APP

```bash
python app.py
```

## 📝 License
This project is for academic or experimental use only. 

Please handle your API keys and environment files securely.

If you use or adapt this code in your own work, **please provide attribution**!
