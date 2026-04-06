# RSP Dashboards

> **ONE: Ownership. Numbers. Execution.**

Business intelligence platform for **Ricoh South Pacific** — covering Sales, Service, Orders, Inventory, Finance, MPS, and Operations across New Zealand, Samoa, Solomon Islands, Tonga, and Vanuatu.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Frontend | Vanilla HTML / CSS / JS (no build step) |
| Data | Salesforce (SOQL / Apex), Xero, BMS, Unleashed |
| Database | Supabase (PostgreSQL) — MPS actions tracker |
| Auth | SHA-256 session-based (`auth.js`) · OAuth 2.0 planned |
| Hosting | Vercel · static · auto-deploy from `main` |

---

## Repo Structure

```
rsp-dashboards/
├── index.html                  # Main hub / navigation
├── login.html                  # Authentication gate
├── auth.js                     # Session validation (all pages)
├── vercel.json                 # Vercel static deployment config
├── supabase-setup.sql          # MPS database schema
├── build_costs.py              # Generates asset_cost.json from Salesforce data
├── asset_cost.json             # Per-machine cost data (toner, parts, equip, paper)
├── machine_costs.json          # Per-machine consumption costs
├── [dashboard].html            # 50+ individual dashboard files (see inventory below)
├── [images/logos]              # Brand assets and team photos
└── nextjs-app/                 # Next.js migration (in progress — see below)
```

---

## Dashboard Inventory

### Core Dashboards

| File | Description | Status |
|------|-------------|--------|
| `index.html` | Main hub — navigation to all dashboards | Live |
| `login.html` | Authentication gate | Live |
| `sales-dashboard.html` | Revenue, pipeline, territory performance, rep scorecards | Live |
| `service-dashboard.html` | Open cases, territory breakdown, SLA tracking, FTF rate | Live |
| `orders-dashboard.html` | Order volume, YTD tracking | Live |
| `inventory-dashboard.html` | Stock levels, consumption patterns, month-end close | Live |
| `operations-dashboard.html` | Operational metrics (Shikha v3) | Live |
| `mps-dashboard.html` | Managed Print Services: portfolio, contracts, actions | Live |
| `finance-dashboard.html` | P&L, cash flow, cost breakdown | Live |

### Sales

| File | Description | Status |
|------|-------------|--------|
| `sales-data-dictionary.html` | Field definitions for sales data | Live |
| `sales-opportunities.html` | Pipeline opportunities view | Live |
| `sales-rep-scorecard.html` | Individual rep performance scorecard | Live |
| `sales-operating-rhythm.html` | Sales rhythm / cadence tracker | Live |
| `leaderboard.html` | Sales rep rankings | Live |

### Service

| File | Description | Status |
|------|-------------|--------|
| `service-rhythm.html` | Service operating rhythm | Live |
| `tech-cases.html` | Technical cases tracker | Live |
| `cases-open.html` | Open cases view | Live |
| `callbacks.html` | Callbacks tracker | Live |
| `asset-downtime.html` | Asset downtime reporting | Live |
| `parts-consumption.html` | Parts consumption tracking | Live |
| `doa.html` | Dead on arrival reporting | Live |

### Finance

| File | Description | Status |
|------|-------------|--------|
| `finance-data-dictionary.html` | Field definitions for finance data | Live |
| `finance-drilldown.html` | Finance drill-down detail view | Live |
| `finance-close.html` | Month-end close dashboard | Live |
| `finance-close-shikha.html` | Month-end close (Shikha's view) | Live |
| `finance-cfo.html` | CFO executive dashboard | Coming Soon |

### Inventory

| File | Description | Status |
|------|-------------|--------|
| `inventory-dictionary.html` | Field definitions for inventory data | Live |
| `inventory-drilldown.html` | Inventory drill-down detail view | Live |
| `inventory-worklist.html` | Inventory worklist | Live |
| `inventory-month-end-close.html` | Inventory month-end close | Live |

### MPS (Managed Print Services)

| File | Description | Status |
|------|-------------|--------|
| `mps-data-dictionary.html` | Field definitions for MPS data | Live |
| `mps-portfolio.html` | Machine portfolio overview | Live |
| `mps-contracts.html` | Contracts tracker | Live |
| `mps-actions.html` | Actions tracker (Supabase-backed) | Live |
| `mps-machine.html` | Individual machine detail | Live |
| `mps-playbook.html` | MPS playbook / reference | Live |

### Operations

| File | Description | Status |
|------|-------------|--------|
| `ops-dashboard.html` | Operations dashboard | Live |
| `ops-dashboard-drilldown.html` | Operations drill-down | Live |
| `ops-rhythm.html` | Operations rhythm tracker | Live |
| `shikha_ops_dashboard.html` | Operations dashboard (Shikha) | Live |
| `shikha_ops_dashboard_v3.html` | Operations dashboard v3 (Shikha) | Live |

### Specialist / Regional

| File | Description | Status |
|------|-------------|--------|
| `slob-upgrades.html` | SLOB upgrades tracker | Live |
| `slob-upgrades2.html` | SLOB upgrades (alternate view) | Live |
| `vijen-tracker.html` | Vijen personal tracker | Live |
| `orders-ytd-2026.html` | Orders YTD 2026 detailed view | Live |
| `conversations.html` | Conversations tracker | Live |
| `case-origin.html` | Case origin breakdown | Live |
| `data-dictionary.html` | General data dictionary | Live |
| `ssc.html` | SSC report | Live |
| `rvl-cir.html` | RVL / CIR report | Live |
| `aptc-proposal.html` | APTC proposal | Live |
| `tonga-pacific-australia-skills.html` | Tonga / Pacific Australia Skills regional report | Live |
| `worldbanksamoa.html` | World Bank Samoa project report | Live |

### Scaffolds / Dev

| File | Description | Status |
|------|-------------|--------|
| `jack-scaffold.html` | Dev scaffold — Jack | Internal |
| `jane-scaffold.html` | Dev scaffold — Jane | Internal |
| `julia-scaffold.html` | Dev scaffold — Julia | Internal |

---

## Local Development

No build step required. Open any `.html` file directly in a browser, or use a local server for correct relative path resolution:

```bash
# Python (no install required)
python3 -m http.server 8080

# Node (npx, no install required)
npx serve .
```

Then visit `http://localhost:8080` — you'll be prompted to log in first.

---

## Authentication

All pages (except `login.html`) are protected by `auth.js`:

- Checks `sessionStorage` for key `rsp_auth`
- If missing or invalid, redirects to `login.html`
- `login.html` verifies the entered password against a SHA-256 hash, then sets the session and redirects back

To change the password, update the hash in `login.html` and `auth.js`.

---

## Deployment (Vercel)

The project is a zero-build static site. `vercel.json` sets:

```json
{
  "framework": null,
  "buildCommand": null,
  "outputDirectory": "./"
}
```

Push to `main` → Vercel auto-deploys the entire root as the public directory.

To connect a new Vercel project:

```bash
npm i -g vercel
vercel --cwd .
```

---

## Data & Integrations

| Source | Used For | Status |
|--------|----------|--------|
| Salesforce | Sales, service, orders, MPS data | Manual export (SOQL snapshots) |
| Supabase | MPS actions tracker (`mps_actions`, `mps_accounts` tables) | Live read/write |
| Xero | Finance / P&L data | Manual export |
| BMS | Operations metrics | Manual export |
| Unleashed | Inventory stock levels | Manual export |

**Cost data pipeline:**
`build_costs.py` queries Salesforce `ProductConsumed` records and generates `asset_cost.json` and `machine_costs.json`, applying FX conversion for NZD, SBD (Solomon Islands), WST (Samoa), VUV (Vanuatu), and TOP (Tonga).

> Data last refreshed: **16 March 2026**. Live Salesforce integration is planned for the next phase.

---

## Next.js Migration

The project is being migrated to [Next.js](https://nextjs.org/) to enable component reuse, server-side data fetching, TypeScript, and a proper auth system (NextAuth.js).

**Approach:** New folder `/nextjs-app/` inside this repo. Legacy dashboards remain live on `main` throughout the migration — no hard cutover.

**Target stack:**

| Layer | Tool |
|-------|------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Database | Supabase client |
| Auth | NextAuth.js (Salesforce OAuth provider) |
| Data | Salesforce Connected App API |
| Hosting | Vercel (same project, new output directory) |

**Migration order:**
1. `/nextjs-app/` project scaffold and base layout
2. Auth (login → NextAuth → session)
3. Main hub (`index.html` → `/app/page.tsx`)
4. High-traffic dashboards — Sales, Service
5. Remaining dashboards in priority order
6. Retire legacy HTML files once feature parity is confirmed

---

## Roadmap

- [ ] Next.js migration (`/nextjs-app/`) — in progress
- [ ] Salesforce Connected App + OAuth 2.0 live data
- [ ] Auto-refresh every 15 minutes
- [ ] Territory filter / drill-down on all dashboards
- [ ] SLA breach alerts (email / Microsoft Teams webhook)
- [ ] Rolling 12-month trend charts (FTF rate, avg days to close)
- [ ] CEO & CFO executive dashboards
- [ ] Mobile-optimised layout

---

*Ricoh South Pacific · East Tamaki, Auckland*
