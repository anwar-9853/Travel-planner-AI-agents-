```markdown
# ✈️ TripMate AI — Multi-Agent Travel Planner

An open-source AI travel planner that transforms natural-language travel requests into practical travel plans with flight suggestions, hotel recommendations, and day-by-day itineraries. Built with **LangGraph, LangChain, FastAPI, PostgreSQL, Groq, Tavily, and AviationStack**.

## 🚀 Features

- ✈️ Flight research using AviationStack and Tavily
- 🏨 Hotel research using Tavily
- 🗺️ AI-generated day-by-day itineraries
- 🧠 Multi-agent orchestration with LangGraph
- 🔄 Shared `TravelState` between agents
- 💾 Persistent conversation and workflow state with PostgreSQL
- ⚡ LLM-powered responses with Groq
- 🌐 FastAPI backend with web interface
- 🐳 Docker-ready deployment

## 🏗️ Architecture

```text
                         User Query
                             │
                             ▼
                         FastAPI
                             │
                             ▼
                    LangGraph Workflow
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ✈️ Flight Agent     🏨 Hotel Agent     🗺️ Itinerary Agent
   AviationStack       Tavily             Tavily
   Tavily              Google Places*     Google Maps*
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                    Shared TravelState
                             │
                             ▼
                  🤖 Final Response Agent
                      openrouter
                             │
                             ▼
                     Final Travel Plan
                             │
                             ▼
                        PostgreSQL
                  Conversation + State
```

> `*` Optional integrations.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core application |
| FastAPI | Backend API |
| Jinja2 | HTML templating |
| HTML/CSS/JavaScript | Web interface |
| LangGraph | Multi-agent orchestration |
| LangChain | LLM and agent tooling |
| Groq | LLM inference |
| PostgreSQL | Persistent state |
| Tavily | Web research |
| AviationStack | Flight information |
| Docker | Containerization |

## 📁 Project Structure

```text
.
├── app.py                # FastAPI application entry point
├── backend.py            # LangGraph travel workflow
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── .gitignore
├── static/               # Frontend assets
├── templates/            # Jinja2 HTML templates
└── tools/                # Flight and web search integrations
```

## 🔑 Prerequisites

- Python 3.10+
- PostgreSQL
- Git
- Groq API key
- Tavily API key
- AviationStack API key

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
openrouter_API_KEY=your_openrouter_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
DEFAULT_ORIGIN_IATA=DAC
```

> Never commit `.env` or API keys to GitHub.

## 📦 Installation

```bash
git clone https://github.com/your-username/tripmate-ai.git
cd tripmate-ai
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure PostgreSQL is running and the database specified in `DATABASE_URL` exists.

## ▶️ Running the Application

```bash
python app.py
```

Or:

```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

Open the application:

```text
http://127.0.0.1:8080/
```

API documentation:

```text
http://127.0.0.1:8080/docs
```

## 🐳 Docker

Build the image:

```bash
docker build -t tripmate-ai .
```

Run the container:

```bash
docker run -p 8080:8080 --env-file .env tripmate-ai
```

The application will be available at:

```text
http://localhost:8080
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/travel` | Submit a travel request |

### Example Request

```bash
curl -X POST http://127.0.0.1:8080/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with a budget of $1200"}'
```

## 🧠 How the Workflow Works

1. The user submits a natural-language travel request.
2. FastAPI receives the request through `/api/travel`.
3. LangGraph initializes the shared `TravelState`.
4. The Flight Agent researches flight information.
5. The Hotel Agent researches accommodation options.
6. The Itinerary Agent creates a practical day-by-day travel plan.
7. The Final Response Agent combines the collected information.
8. PostgreSQL persists conversation and workflow state.
9. The final travel plan is returned to the user.

## 💡 Example

```text
Plan a 5-day trip from Addis Ababa to India.

Budget: $2,000

Include:
- Flights
- Hotels
- Daily activities
- Estimated costs
```

## 🔮 Future Improvements

- 💰 Real-time price comparison
- ✈️ Additional flight providers
- 🏨 Dedicated hotel APIs
- 🗺️ Interactive maps
- 🌦️ Weather-aware itinerary planning
- 💱 Real-time currency conversion
- 🧳 Personalized travel preferences
- 🔐 User accounts and saved trips
- 📱 Mobile application
- 🤖 Additional specialized agents

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Commit and push your changes.
5. Open a pull request.

## 📄 License

This project is open source. See the repository for license information.

## 🙏 Acknowledgments

TripMate AI demonstrates how **LangGraph, LangChain, LLMs, external APIs, web search, PostgreSQL, and FastAPI** can be combined to build a practical stateful multi-agent AI application.
```
