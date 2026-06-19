---

# Automation Frontend Dashboard

A high-performance, enterprise-grade financial dashboard built with Next.js 15 and React 19. This application serves as the graphical interface for the Axeane Automation Engine, facilitating seamless data ingestion, accounting rule auditing, and automated web-form injection.

---
# Automation Frontend Dashboard

## 🌟 Overview

This frontend is architected to be completely **backend-agnostic**. While natively designed to bridge with a Python/Playwright automation sidecar via a Tauri desktop shell, it operates entirely through an isolated Service Layer that decouples the user interface from the underlying OS execution environments.

---

## 🚀 Key Features

* 📊 **Unified Financial Workflow**: Five specialized modular views (Settings, Browser, Import, Review, Execution) that perfectly mirror complex accounting processing cycles.
* 🧮 **Rule Preview Engine**: Interactive "Formula Cards" that allow accountants to visually audit generated split journal entries ($\text{Debits} == \text{Credits}$) before launching automation.
* 🤖 **Advanced Browser Management**: Absolute control over Chrome DevTools Protocol (CDP) socket bridges, persistent cookie profiles, and headless/visible application launch states.
* 📟 **Live Execution Terminal**: A real-time, stream-buffered virtual console for monitoring active Playwright automation logs, warnings, and interceptor telemetry.
* 🎨 **Finance-Dense Material 3 UI**: A high-density, ultra-high-contrast interface built using Tailwind CSS 4 design tokens—engineered for heavy, multi-row data scanning.

---

## 🏗️ Folder Architecture

The workspace follows a strict three-layer modular design pattern to ensure cross-platform maintainability:

```text
src/
├── app/                  # Next.js 15 App Router pages & view wrappers
├── components/           # Shared presentation widgets (Cards, Tables, Terminal)
├── metadata/             # LAYER 1: Static configurations, default paths, & UI constants
├── modules/              # LAYER 2: React hooks (Controllers), state machines, & polling logic
└── services/             # LAYER 3: Core endpoint HTTP bridge communication layers
    └── endpoint.ts       # Central fetch engine mapped to FastAPI specifications

```

### Architectural Layer Breakdown

1. **Metadata Layer (`/metadata`)**: Governs static UI constants, dropdown option trees, default browser configurations, and regional Tunisian TVA matrices.
2. **Logic Layer (`/modules`)**: House-custom React hooks (`useAutomationController`, `useSessionPoller`) that handle reactive state transformations, polling schedules, and async worker hooks.
3. **Service Layer (`/services`)**: Houses the pure HTTP pipeline. Outlines schema bindings mirroring backend FastAPI entities.

---

## 🛠️ Tech Stack

* **Framework**: Next.js 15+ (App Router, Client-Side SPA Focus)
* **Runtime Library**: React 19 (Hooks & Suspense Architectures)
* **Styling Engine**: Tailwind CSS 4.0 (Variable-driven theme engine)
* **Iconography**: Lucide React
* **Networking**: Native Fetch API wrapped inside type-safe async drivers
* **Language**: TypeScript 5.x (Strict compilation targets)

---

## 📥 Getting Started

### Prerequisites

* Node.js `18.0.0` or higher
* Package Manager: `npm` or `pnpm`

### Installation & Launch

```bash
# Clone the workspace repository
git clone [repository-url]
cd frontend

# Install system dependency trees
npm install

# Initialize local environment variables
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
cp .env.example .env.local

# Fire up the Next.js development engine
npm run dev

```

The interface will initialize locally at **`http://localhost:3000`**.

---

## 🤝 Relationship with Backend

The UI layer communicates directly with an active automation gateway instance. By default, it looks for a Python/FastAPI environment bound to: `http://localhost:8000`.

### Lifecycle State Mappings

When integrating or testing frontend controllers against backend modules, ensure state handlers conform to the engine's core lifecycle flags:

| UI App View | Triggered Action | API Endpoint | Engine Status |
| --- | --- | --- | --- |
| **Import View** | File Selection Drop | `POST /api/upload` | `idle` |
| **Import View** | Process Execution Trigger | `POST /api/parse` | `parsing` → `completed` |
| **Review View** | Mount Preview State | `GET /api/formulas` | `completed` |
| **Execution View** | Engaged Run Profile | `POST /api/execute` | `executing` |
| **Terminal View** | Polling Stream Hook | `GET /api/status` | `executing` | `error` |

---

## 🛡️ Security & State Guardrails

* **Data Transient Isolation**: The UI does not store client accounting entries inside localStorage or long-term caches. All state indexes are transient and bound to active session UUID keys.
* **Stream Interrupts**: Leaving or closing the Execution tab does not drop the backend script thread. Users must explicitly click **"Stop Automation"** (`POST /api/stop`) to force remote browser processes to detach cleanly.
* **Credential Masking**: User credentials for target accounting portals are never buffered by UI telemetry logs; password form variables feed strictly down hidden memory pipes directly into the Playwright entry forms.
