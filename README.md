# Interactive Election Education Assistant - Backend API

A modular, scalable, secure, and testable FastAPI backend designed to serve the Interactive Election Education Assistant. This system processes user queries about elections, validates input, and interfaces with a simulated LLM service to provide structured educational responses.

## 🚀 Features

- **FastAPI Framework**: High performance, easy to learn, fast to code, ready for production.
- **Input Validation**: Uses robust keyword checks and pattern matching to block irrelevant queries and basic prompt injections.
- **Structured LLM Prompts**: Forces structured, easy-to-read educational outputs.
- **Pydantic Models**: Ensures robust request parsing and validation.
- **Modular Architecture**: Clean separation of concerns (routes, services, core configuration).

## 📁 Project Structure

```text
election-assistant/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application instance
│   ├── routes.py            # API endpoints
│   ├── services/            # Business logic
│   │   ├── llm_service.py   # LLM interaction simulation
│   │   ├── validator.py     # Input validation and security
│   │
│   ├── core/
│   │   ├── config.py        # Environment settings management
│   │   ├── prompts.py       # System prompts for the LLM
│   │
│   ├── utils/               # Helper functions
│   │   ├── formatter.py
│   │   ├── helpers.py
│
├── tests/                   # Pytest test suites
│   ├── test_routes.py
│   ├── test_services.py
│
├── requirements.txt         # Project dependencies
├── .env.example             # Example environment variables
├── README.md
└── run.py                   # Application entry point
```

## 🛠️ Setup Instructions

1. **Clone the repository** (if applicable) or navigate to the project root.

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Copy `.env.example` to a new `.env` file:
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with any real API keys when you switch to a live LLM.

## 🏃‍♂️ How to Run

Run the application using the entry point script:

```bash
python run.py
```

The server will start at `http://0.0.0.0:8000`. You can access the interactive API docs at `http://0.0.0.0:8000/docs`.

## 🧪 Testing

Run the test suite using `pytest`:

```bash
pytest tests/ -v
```

## 📡 API Usage Example

**Endpoint:** `POST /api/v1/ask`

**Request Body:**
```json
{
  "query": "How do I register to vote in the USA?"
}
```

**Response:**
```json
{
  "response": "1. 📌 Overview\n   * This is a simulated response to your query about 'How do I register to vote in the USA?'. Elections are the process by which citizens choose their representatives.\n\n2. 🪜 Step-by-Step Process\n   * 1. Register to vote.\n   * 2. Research candidates and issues.\n   * 3. Go to the polling station or mail your ballot.\n   * 4. Cast your vote.\n\n3. 🗓️ Timeline\n   * Registration -> Campaigning -> Election Day -> Counting -> Results\n\n4. ⚠️ Important Notes\n   * Make sure you are registered before the deadline in your area. You must meet the age and citizenship requirements.\n\n5. 👉 Next Step / Interaction\n   * Would you like to see how voting works in a specific country?"
}
```
