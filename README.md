# TrendCart - A Retail Shopping Assistant 🛒

A conversational AI shopping assistant powered by Google's Agent Development Kit (ADK), Vertex AI, and Google Cloud services. The assistant helps store customers discover products, explore color options, check live inventory, generate AI product imagery and videos, and manage a shopping cart with structured A2UI components.
---
<div align="center">

<img src="assets/build-with-gemini-banner.png" alt="Build with Gemini" width="100%" />

# 🚀 Build with Gemini ·

### The starter kit of the Build with Gemini World Tour, and a showcase of what participants built with it.

Clone this repo, open [Antigravity](https://antigravity.google), and build your own agent-first app on Google Cloud. Every project in the [gallery below](#-featured-projects) was built the same way: prototyped with Antigravity and `agents-cli`, equipped with Memory, tools, and storage, deployed to Agent Platform, and given a face on Cloud Run.

<br/>

![Build with Gemini](https://img.shields.io/badge/Build%20with%20Gemini-World%20Tour-4285F4?logo=google&logoColor=white)
![Track 3](https://img.shields.io/badge/Track%203-Agent--First%20Apps-EA4335)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Agent%20Platform-4285F4?logo=googlecloud&logoColor=white)
![Built with ADK](https://img.shields.io/badge/Built%20with-ADK%20%2B%20agents--cli-34A853)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)
![Projects](https://img.shields.io/badge/Projects-8-blue)

<sub>📖 <a href="https://cszhu.github.io/build-with-gemini/">Lab Guide</a> · 🛠️ <a href="https://google.github.io/agents-cli/guide/getting-started/">agents-cli</a> · 🤖 <a href="https://google.github.io/adk-docs/">ADK</a></sub>

</div>

---

## 📚 Table of Contents

- [🧩 Anatomy of a Track 3 Project](#-anatomy-of-a-track-3-project)

- [🧠 What's in this Repo](#-whats-in-this-repo)
- [🧰 Build Your Own](#-build-your-own)
- [📚 Resources](#-resources)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🧩 Anatomy

Every app in this collection is built from the same set of Google Cloud building blocks introduced in the lab. Once you understand this shape, you can read any project here at a glance:

| Layer | What it does | Powered by |
|---|---|---|
| 🤖 **The Agent** | The core reasoning loop | [ADK](https://google.github.io/adk-docs/) + [`agents-cli`](https://google.github.io/agents-cli/guide/getting-started/), scaffolded with [Antigravity](https://antigravity.google) |
| 🧠 **Memory** | Remembers facts across sessions | [Agent Platform Memory Bank](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank) |
| 🗄️ **Structured data** | Inventory, records, lists | [Firestore](https://console.cloud.google.com/firestore) |
| 🖼️ **Files & blobs** | Images, media, assets | [Cloud Storage](https://console.cloud.google.com/storage) |
| 🔧 **Tools** | Take real actions and fetch real data | ADK function tools |
| 🎨 **Media generation** | Creates images (and video) on demand | `gemini-3.1-flash-lite-image` (Nano Banana 2 Lite) · Omni (video) |
| 🧪 **Code sandbox** | Safely runs generated code | Agent Platform code execution |
| 🪟 **Agent-first UI** | Cards and tables instead of plain text | [A2UI](https://adk.dev/integrations/a2ui/) |
| 🌐 **Frontend** | A shareable web face | FastAPI proxy on [Cloud Run](https://cloud.google.com/run) |

---

## 🧠 What's in this Repo

The `.agents/` folder teaches Antigravity how to build agents on Google Cloud.

### Skills

A **skill** is a bundle of instructions that loads automatically when it's relevant, so the agent gets the workflow right in fewer steps instead of rediscovering it each time.

| Skill | What it does |
| --- | --- |
| [`pick-your-agent-project`](.agents/skills/pick-your-agent-project/SKILL.md) | Brainstorm your app idea and write a project brief |
| [`troubleshoot-lab-setup`](.agents/skills/troubleshoot-lab-setup/SKILL.md) | Verify your environment and fix common setup errors |
| [`memory-bank-setup`](.agents/skills/setup-memory-bank/SKILL.md) | Add cross-session memory to your agent with Vertex AI Memory Bank |
| [`enable-a2ui`](.agents/skills/enable-a2ui/SKILL.md) | Make your agent reply with rich UI cards (A2UI) in the ADK dev UI |
| [`build-agent-frontend`](.agents/skills/build-agent-frontend/SKILL.md) | Generate a FastAPI chat frontend and ship it to Cloud Run |
| [`record-demo`](.agents/skills/record-demo/SKILL.md) | Record a branded demo video of your agent, with an optional AI soundtrack |
| [`publish-to-github`](.agents/skills/publish-to-github/SKILL.md) | Publish your finished project to your own GitHub and submit it for swag |

---

## 🌟 Capabilities & Features

### 🛒 Product Discovery & Shopping Cart
* **Catalog Search**: Search products by keyword, category, or maximum price (`search_products`).
* **Product Details & Stock**: Retrieve full product specifications, color variants, and live inventory availability (`get_product_details`, `check_inventory`).
* **Shopping Cart Management**: Add, view, and remove items from an in-memory shopping cart (`add_to_cart`, `view_cart`, `remove_from_cart`).
* **Python Code Execution**: Secure sandbox (`code_executor`) used for subtotal, tax, and discount computations.

### 🎨 Visual Media Generation
* **Product Studio Photos**: Generates studio-quality product photographs using `gemini-3.1-flash-lite-image` (`generate_product_image`).
* **3D Showcase Videos**: Generates short 3D product showcase videos using Google's Omni model `gemini-omni-flash-preview` (`generate_product_video`).

### 🧠 Memory & Personalization
* **Memory Bank**: Preloads session memories (`PreloadMemoryTool`) and generates persistent memories after agent turns (`generate_memories_callback`).

### 🗺️ Store Location & Contextual Tools
* **Google Maps Integration**: Geocodes customer addresses (`geocode_address`) and finds nearby retail store locations (`find_nearby_places`).
* **Utility Tools**: Real-time currency conversion (`convert_currency`), local weather (`get_weather`), and local time (`get_current_time`).

### 📊 Live Database Operations
* **Firestore Integration**: Query and update live product catalog items, stock levels, and order statuses directly in Google Cloud Firestore (`read_firestore_products`, `get_firestore_product`, `write_firestore_product`, `update_firestore_stock`, `get_order_status`).

### 📱 Adaptive UI (A2UI)
* **Structured UI Rendering**: Formats product recommendations, cart summaries, and generated imagery into responsive A2UI card layouts via `a2ui_callback`.

---

## ☁️ Wired-Up Google Cloud Services

The following Google Cloud services are directly integrated into the codebase:

1. **Vertex AI / Gemini Models**:
   * `gemini-2.5-flash`: Primary reasoning, tool orchestration, and UI generation model.
   * `gemini-3.1-flash-lite-image`: AI image generation for product visuals.
   * `gemini-omni-flash-preview`: Omni video generation model (global region).
2. **Google Cloud Firestore**: NoSQL database backing live product items, stock inventory, and order tracking.
3. **Google Cloud Storage (GCS)**: Public asset storage bucket hosting generated product images and videos.
4. **Google Maps Platform**: Geocoding and Places API for store locator tools.
5. **Agent Engine / ADK Agent Runtime**: Cloud deployment target specified in `agents-cli-manifest.yaml`.

---

### Pre-configured tools (MCP)

[`.agents/mcp_config.json`](.agents/mcp_config.json) wires up two [Model Context Protocol](https://modelcontextprotocol.io/) servers that authenticate with your gcloud credentials, so the agent can look things up instead of guessing:

- **Firebase**: work directly with Firestore and other Firebase services
- **Google Developer Knowledge**: grounded access to Google's official docs (Cloud, Firebase, ADK, Agent Platform)

### Layout

```text
.agents/
├── mcp_config.json    # Firebase + Developer Knowledge MCP servers
├── rules/             # workspace rules (only deploy when asked)
└── skills/            # the workshop skills listed above
```

---

## 🚀 Setup & Local Execution Instructions

### Prerequisites
* Python 3.10+
* `uv` or `pip` package manager
* Google Cloud SDK (`gcloud`) authenticated with access to Firestore and Vertex AI

### Environment Variables
Set the following environment variables in your terminal or `.env` file:

```bash
export PROJECT_ID="<your-gcp-project-id>"
export AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>"
export AGENT_DIRECTORY="app"
```

### Installation & Launch

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Run Agent Locally**:
   ```bash
   uv run python -m app.agent
   ```

3. **Run Web Frontend**:
   Navigate to the `frontend/` directory, install frontend dependencies, and start the proxy server:
   ```bash
   cd frontend
   pip install -r requirements.txt
   python main.py
   ```
   Open your browser to the local port indicated by the server output (default `PORT=8080`).


## 📚 Resources

- **[Lab guide](https://cszhu.github.io/build-with-gemini/)**: the step-by-step workshop
- [Antigravity](https://antigravity.google)
- [agents-cli](https://google.github.io/agents-cli/guide/getting-started/)
- [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform)

---

## 🚧 Status & Planned Capabilities

* **Implemented**: Product discovery, catalog search, inventory checks, AI photo & video generation, Firestore database sync, Memory Bank, A2UI cards, and shopping cart management.
* **Planned, Not Yet Implemented**: Payment gateway integration and order checkout processing (currently scoped out to focus on cart building and discovery).

---

## 🤝 Contributing

**Built something?** Publish it with the `publish-to-github` skill and submit it through the form it gives you. Submissions get you swag, and standout projects get added to the [Featured Projects](#-featured-projects) gallery above.

**Found a bug?** If you hit a rough edge in a skill or the lab, please [open an issue](https://github.com/cszhu/build-with-gemini/issues).

---

## 📄 License

This is not an officially supported Google product and is provided for the Build with Gemini workshop for demonstration purposes only.
