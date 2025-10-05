# 🔍 Cardano Lead Generator Agent

> AI-powered agent that finds and analyzes Cardano ecosystem participants on X.com (Twitter) with automated blockchain payments via Masumi Network.

[![Built with Masumi](https://img.shields.io/badge/Built%20with-Masumi-blue)](https://masumi.network)
[![Cardano](https://img.shields.io/badge/Blockchain-Cardano-0033AD)](https://cardano.org)
[![MIP-003 Compliant](https://img.shields.io/badge/MIP--003-Compliant-green)](https://github.com/masumi-network/masumi-improvement-proposals/blob/main/MIPs/MIP-003/MIP-003)

## 🎥 Demo Video

[![Watch Demo](https://img.youtube.com/vi/kbF5d00DKHQ/maxresdefault.jpg)](https://youtu.be/kbF5d00DKHQ)

**[► Watch the full demo on YouTube](https://youtu.be/kbF5d00DKHQ)**

## 🎯 What It Does

This agent automates the discovery of Cardano community members on X.com. Simply specify what you're looking for (developers, NFT artists, DeFi projects, etc.) and receive structured JSON data with:

- **Name**: Account/project name
- **Username**: X.com handle
- **Profile URL**: Direct link to their X.com profile
- **Description**: Bio/description
- **Follower Count**: Audience size

Perfect for marketing teams, community managers, researchers, and developers building Cardano ecosystem tools.

## 💰 Pricing

**5 ADA per search** on Cardano Preprod testnet (configurable in `.env`)

## ✨ Features

- ✅ **Real-time web scraping** via Apify Google Search API
- ✅ **MIP-003 compliant** API following Masumi standards
- ✅ **Automated blockchain payments** on Cardano
- ✅ **Structured JSON output** with pydantic validation
- ✅ **Production-ready** FastAPI application
- ✅ **Railway deployable** with one click

## 🚀 Quick Start

### Prerequisites

- Python 3.10-3.13
- [uv](https://github.com/astral-sh/uv) package manager
- Apify API token ([get one here](https://apify.com))
- Railway account (for deployment)
- Cardano wallet with test ADA

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd crewai-masumi-quickstart-template

# Create virtual environment
uv venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required environment variables:**

```ini
# Masumi Payment Service (Railway deployment)
PAYMENT_SERVICE_URL=https://your-payment-service.up.railway.app/api/v1
PAYMENT_API_KEY=your_admin_key

# Agent Configuration
AGENT_IDENTIFIER=your_agent_identifier_from_masumi_registry
PAYMENT_AMOUNT=5000000  # 5 ADA in lovelace
PAYMENT_UNIT=lovelace
SELLER_VKEY=your_wallet_verification_key

# API Keys
OPENAI_API_KEY=your_openai_api_key  # Required for CrewAI framework
APIFY_TOKEN=your_apify_api_token    # For web scraping

# Network
NETWORK=Preprod  # or Mainnet
```

**Where to get these values:**

- **PAYMENT_SERVICE_URL**: Deploy [Masumi Payment Service](https://docs.masumi.network/documentation/get-started/installation) on Railway
- **PAYMENT_API_KEY**: Found in Railway variables or Payment Service admin panel
- **AGENT_IDENTIFIER**: Register your agent via [POST /registry](https://docs.masumi.network/api-reference/payment-service/post-registry)
- **SELLER_VKEY**: Get from Payment Service admin panel → Selling Wallet
- **APIFY_TOKEN**: Sign up at [apify.com](https://apify.com) and create an API token

### 3. Deploy Masumi Payment Service

Follow the [Railway deployment guide](https://docs.masumi.network/documentation/get-started/installation/railway-templates):

1. Click "Deploy on Railway"
2. Provide Blockfrost API key
3. Wait for deployment (~5 minutes)
4. Generate public URL in Settings → Networking
5. Access admin panel at `/admin`
6. Top up selling wallet with [test ADA](https://dispenser.masumi.network/)

### 4. Register Your Agent

1. Get your wallet verification key from the admin panel
2. Call `POST /registry` to register your agent on Masumi
3. Wait for registration (check admin dashboard)
4. Copy your `agentIdentifier` to `.env`

### 5. Run the Agent

```bash
# Start the API server
python main.py api

# Server runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

## 📡 API Endpoints

All endpoints follow the [MIP-003](https://github.com/masumi-network/masumi-improvement-proposals/blob/main/MIPs/MIP-003/MIP-003) standard:

### `GET /availability`
Check if the agent is online

**Response:**
```json
{
  "status": "available",
  "type": "masumi-agent",
  "message": "Server operational."
}
```

### `GET /input_schema`
Get the expected input format

**Response:**
```json
{
  "input_data": [
    {
      "id": "text",
      "type": "string",
      "name": "Search Topic",
      "data": {
        "description": "The topic to search for Cardano leads",
        "placeholder": "developers"
      }
    }
  ]
}
```

### `POST /start_job`
Initiate a search and create payment request

**Request:**
```json
{
  "identifier_from_purchaser": "74657374313233",
  "input_data": {
    "text": "developers"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": "uuid-here",
  "blockchainIdentifier": "payment-hash",
  "payByTime": "timestamp",
  "submitResultTime": "timestamp",
  "unlockTime": "timestamp",
  "agentIdentifier": "your-agent-id",
  "sellerVkey": "your-wallet-vkey",
  "input_hash": "sha256-hash",
  "amounts": [{"amount": "5000000", "unit": "lovelace"}]
}
```

### `GET /status?job_id=<id>`
Check job status and retrieve results

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "completed",
  "result": {
    "leads": [
      {
        "name": "Cardano Foundation",
        "username": "CardanoStiftung",
        "handle": "https://x.com/CardanoStiftung",
        "description": "Official Cardano Foundation account...",
        "followers": "125000"
      }
    ]
  }
}
```

**Status values:**
- `awaiting_payment` - Waiting for blockchain confirmation
- `running` - Scraping X.com via Apify
- `completed` - Results ready
- `failed` - Error occurred

### `POST /provide_input`
Provide additional input if status is `awaiting_input`

**Request:**
```json
{
  "job_id": "uuid-here",
  "input_data": {
    "additional_field": "value"
  }
}
```

## 🧪 Testing

### Test the complete workflow:

```bash
# 1. Start a job
curl -X POST "http://localhost:8000/start_job" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier_from_purchaser": "74657374313233",
    "input_data": {"text": "developers"}
  }'

# 2. Make payment via Masumi Payment Service
# Go to https://your-payment-service.up.railway.app/docs
# Use POST /purchase with the response from step 1

# 3. Check status
curl "http://localhost:8000/status?job_id=<job_id_from_step_1>"
```

### 📸 Screenshots

**1. Making Payment via Masumi Payment Service**
![Payment Request](https://i.imgur.com/payment-screenshot.png)

**2. Masumi Dashboard - Agent Overview**
![Masumi Dashboard](https://i.imgur.com/dashboard-screenshot.png)

**3. Agent Results - Cardano Leads JSON Output**
![Results Output](https://i.imgur.com/results-screenshot.png)

## 🏗️ Architecture

```
┌─────────────────┐
│   Client App    │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  FastAPI Server     │
│  (Your Agent)       │
│  - /start_job       │
│  - /status          │
│  - /provide_input   │
└─────┬───────┬───────┘
      │       │
      │       ▼
      │  ┌──────────────┐
      │  │ Apify API    │
      │  │ (Web Scraper)│
      │  └──────────────┘
      │
      ▼
┌──────────────────────┐
│ Masumi Payment       │
│ Service (Railway)    │
│ - Creates payments   │
│ - Monitors blockchain│
└──────────┬───────────┘
           │
           ▼
    ┌──────────────┐
    │   Cardano    │
    │  Blockchain  │
    └──────────────┘
```

## 📁 Project Structure

```
.
├── crew_definition.py    # Agent logic & Apify integration
├── main.py              # FastAPI app & MIP-003 endpoints
├── logging_config.py    # Logging setup
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── README.md
```

## 🔧 How It Works

1. **Client calls `/start_job`** with search topic
2. **Agent creates payment request** via Masumi SDK
3. **Client pays via Masumi Payment Service** using the blockchain identifier
4. **Payment Service monitors Cardano blockchain** for transaction confirmation
5. **Payment confirmed → Agent triggered** via callback
6. **Agent calls Apify** with query: `site:x.com {topic} cardano`
7. **Apify scrapes Google** for X.com search results
8. **Parser extracts data** (name, username, URL, description, followers)
9. **Results formatted as JSON** using pydantic models
10. **Job status → `completed`** with results available via `/status`

## 🌐 Deployment

### Railway (Recommended)

1. Fork this repository
2. Deploy on Railway
3. Add environment variables in Railway dashboard
4. Generate public URL
5. Test at `https://your-agent.up.railway.app/docs`

### Local Development

```bash
python main.py api
```

Server runs on `http://localhost:8000`

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python)
- **Agent**: CrewAI
- **Web Scraping**: Apify Google Search Scraper
- **Payments**: Masumi Payment Service
- **Blockchain**: Cardano (Preprod/Mainnet)
- **Validation**: Pydantic
- **Deployment**: Railway
- **Database**: In-memory (use PostgreSQL for production)

## 📝 Use Cases

- **Marketing Teams**: Find Cardano influencers and content creators
- **Developers**: Build community databases and analytics tools
- **Projects**: Identify partnership and collaboration opportunities
- **Researchers**: Analyze Cardano ecosystem growth and trends
- **Community Managers**: Discover active participants for engagement

## ⚠️ Production Considerations

**Current implementation uses in-memory storage.** For production:

1. ✅ Replace `jobs = {}` with PostgreSQL/MongoDB
2. ✅ Add Redis for job queue management
3. ✅ Implement rate limiting
4. ✅ Add authentication for admin endpoints
5. ✅ Set up monitoring (Sentry, Datadog)
6. ✅ Configure CORS for your frontend
7. ✅ Use environment-based configuration

## 🤝 Contributing

This agent was built for the Masumi Hackathon. Feel free to fork and extend!

**Ideas for enhancement:**
- Add more social platforms (LinkedIn, GitHub)
- Sentiment analysis on leads
- Automated outreach templates
- Lead scoring based on activity
- Export to CSV/Google Sheets

## 📚 Resources

- [Masumi Documentation](https://docs.masumi.network)
- [MIP-003 Standard](https://github.com/masumi-network/masumi-improvement-proposals/blob/main/MIPs/MIP-003/MIP-003)
- [CrewAI Documentation](https://docs.crewai.com)
- [Apify Documentation](https://docs.apify.com)
- [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnets/tools/faucet)
- [Railway Documentation](https://docs.railway.app)

## 📄 License

MIT License - feel free to use this for your own projects!

## 👨‍💻 Author

**Amaan** - Full-stack Developer & AI Agent Builder

Built for the Masumi Network Hackathon 🚀

### Agent Details

**Agent Identifier**: `7e8bdaf2b2b919a3a4b94002cafb50086c0c845fe535d07a77ab7f77fada2d0c8d29be2c618092f68e1059d94bdff38d56b4329634c27d5e7878c5d9`

**Network**: Cardano Preprod Testnet

**Price**: 5 ADA per search

---

**Questions?** Open an issue or reach out on the Masumi Discord!
