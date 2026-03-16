# RSP Service Dashboard

Live service operations dashboard for **Ricoh South Pacific**, pulling data from Salesforce and deployed via Vercel.

## What it shows

- **Open cases** by service territory (NZ, Samoa, Solomon Islands, Tonga, Vanuatu)
- **Status breakdown** per territory
- **Work type breakdown** per territory
- **Cases open >72 hours** per territory
- **Average days to close** — Service Call work type, current month vs prior month
- **First time fix rate** — Service Call work type, current month vs prior month

## Tech stack

| Layer | Tool |
|-------|------|
| Frontend | Vanilla HTML/CSS/JS (no build step) |
| Data | Salesforce (queried via Apex / SOQL) |
| Hosting | Vercel (auto-deploy from `main`) |
| Auth *(planned)* | Salesforce Connected App + OAuth 2.0 |

## Repo structure

```
rsp-dashboards/
├── public/
│   └── index.html          # Main dashboard (self-contained)
├── src/
│   └── data/
│       └── snapshot.json   # Static data snapshot (used until live API is wired)
├── vercel.json             # Vercel routing config
├── .gitignore
└── README.md
```

## Local development

No build step required — just open `public/index.html` in a browser.

```bash
# Or serve locally with any static server, e.g.:
npx serve public
```

## Deployment (Vercel)

1. Push to `main` branch
2. Vercel auto-detects the static site and deploys `public/` as the root
3. Live URL is assigned automatically

To connect your own Vercel project:

```bash
npm i -g vercel
vercel --cwd .
```

## Roadmap

- [ ] Salesforce Connected App + OAuth flow for live data on page load
- [ ] Auto-refresh every 15 minutes
- [ ] Territory filter / drill-down
- [ ] SLA breach alerts (email / Teams webhook)
- [ ] Rolling 12-month trend charts (FTF rate, avg days to close)
- [ ] Mobile-optimised layout

## Data as of

16 March 2026 — manually refreshed. Live Salesforce integration coming in next phase.

---

*Ricoh South Pacific · East Tamaki, Auckland*
