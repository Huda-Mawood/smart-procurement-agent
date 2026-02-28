# 🛒 Smart Procurement Agent

> An AI-powered multi-agent system that automates product research, price comparison, and procurement reporting across Egyptian e-commerce platforms.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![CrewAI](https://img.shields.io/badge/CrewAI-0.80.0+-orange)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)


---

## 📌 Overview

**Smart Procurement Agent** is a multi-agent AI pipeline built with [CrewAI](https://crewai.com) that helps companies automate the procurement process by:

1. 🔍 **Generating smart search queries** tailored to find specific products
2. 🌐 **Searching the web** using Tavily to find product listings across e-commerce stores
3. 🕷️ **Scraping product pages** to extract prices, specs, and discounts
4. 📊 **Generating a professional HTML procurement report** with recommendations

Built for **Rankyx** — an AI solutions company focused on improving search and recommendation systems.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CrewAI Pipeline                   │
│                                                     │
│  Agent A          Agent B         Agent C           │
│  ─────────        ────────        ────────          │
│  Search Query  →  Web Search  →  Web Scraping  →   │
│  Generator        (Tavily)       (ScrapeGraph)      │
│                                                     │
│                                    ↓                │
│                                Agent D              │
│                                ────────             │
│                             Procurement             │
│                             Report (HTML)           │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-procurement-agent.git
cd smart-procurement-agent
```

### 2. Set Up Environment

```bash
conda create -n smart-procurement-agent python=3.11
conda activate smart-procurement-agent
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 4. Run the Agent

```bash
python main.py
```

---

## 🐳 Run with Docker

The easiest way to run the project without any local setup:

```bash
# Pull and run directly
docker pull YOUR_DOCKERHUB_USERNAME/smart-procurement-agent:latest
docker run --env-file .env smart-procurement-agent
```

Or build locally:

```bash
docker build -t smart-procurement-agent .
docker run --env-file .env smart-procurement-agent
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
AGENTOPS_API_KEY=your_agentops_api_key
TAVILY_API_KEY=your_tavily_api_key
SCRAPE_API_KEY=your_scrapegraph_api_key
```

### Input Parameters (inside `main.py`)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `product_name` | Product to search for | `"coffee machine for the office"` |
| `websites_list` | Target e-commerce sites | `["amazon.eg", "jumia.com.eg"]` |
| `country_name` | Country to search in | `"Egypt"` |
| `no_keywords` | Max search queries to generate | `10` |
| `language` | Search language | `"English"` |
| `score_th` | Minimum search result confidence | `0.10` |
| `top_recommendations_no` | Top products to scrape | `10` |

---

## 📂 Project Structure

```
smart-procurement-agent/
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image definition
├── .env.example             # Environment variables template
├── .github/
│   └── workflows/
│       ├── ci.yml           # CI pipeline
│       └── docker.yml       # Docker build & push pipeline
├── ai-agent-output/         # Generated outputs (git-ignored)
│   ├── step_1_suggested_search_queries.json
│   ├── step_2_search_result_engin.json
│   ├── step_3_search_results.json
│   └── step_4_procurement_report.html
└── README.md
```

---

## 📤 Output

After running, the agent generates 4 files inside `ai-agent-output/`:

| File | Description |
|------|-------------|
| `step_1_suggested_search_queries.json` | AI-generated search queries |
| `step_2_search_result_engin.json` | Raw search results from Tavily |
| `step_3_search_results.json` | Scraped product details |
| `step_4_procurement_report.html` | Final HTML procurement report |

---

## 🔧 Tech Stack

| Tool | Purpose |
|------|---------|
| [CrewAI](https://crewai.com) | Multi-agent orchestration framework |
| [Groq + LLaMA 3.3 70B](https://groq.com) | LLM backbone (fast inference) |
| [Tavily](https://tavily.com) | AI-powered web search |
| [ScrapeGraph AI](https://scrapegraph.ai) | Intelligent web scraping |
| [AgentOps](https://agentops.ai) | Agent monitoring & observability |
| [Pydantic](https://docs.pydantic.dev) | Data validation & structured outputs |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

[MIT](LICENSE)