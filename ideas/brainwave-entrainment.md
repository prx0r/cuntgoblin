# Brainwave Entrainment — SoundWorld

*2026-08-18T07:15:00Z*

---

## What You Have (verified working)

A Rust-native, multi-layered ambient entrainment engine:

- 3 modes: binaural, isochronic, mixed (unique combination)
- 5 bands: delta (0.5-4 Hz), theta (4-8), alpha (8-12), beta (12-30), gamma (30-50)
- 5 audio layers: neural beat + musical pad + tempo pulse + echo/delay + reverb
- Session arcs: multi-phase tracks (warm → build → peak → cooldown → settle)
- Machine verification: Goertzel analysis proves WAV contains target frequency
- Visual alignment: concentric rings pulse at beat frequency
- 24-bit WAV + 320kbps MP3 output
- API-driven: POST /commands → verified WAV

---

## Competitive Landscape

| Project | Stars | What it lacks vs SoundWorld |
|---------|-------|----------------------------|
| Brain.fm | N/A | Proprietary, no verification |
| NeuralBeat | 31 | No music, no sessions, no verification |
| ruv-neural | 28 | No multi-band, no music |
| binaural-generator | 24 | No verification, no sessions |
| SBaGenX | 8 | No music, no GUI, no sessions |

**Key gap: No open-source project combines multi-mode entrainment + generative music + session arcs + machine verification + Rust performance + API access.**

---

## The Market

- Meditation/wellness apps: $5-6B (2023) → $16-20B by 2030
- Neurofeedback devices: $3-5B
- Binaural beats niche: ~$500M-1B

**Pricing precedent:**
- Brain.fm: $7-15/mo
- Calm/Headspace: $70/yr
- myNoise: $5/mo
- Generic binaural apps: $3-10/mo

---

## Products

### 1. Brainwave-as-a-Service API (8.2/10)

```http
POST /brainwave/generate
```

```json
{
  "band": "gamma",
  "carrier_hz": 500,
  "mode": "binaural",
  "minutes": 20,
  "apply_visual": true
}
```

→ 24-bit WAV + verification report

**Pricing:**
- Free: 5 renders/day
- Pro: $9/mo unlimited
- B2B: $99/mo API key

### 2. MCP Server for Brainwave (8.5/10)

```bash
hermes mcp add brainwave --command soundworld --args brainwave
```

Any AI agent can generate focus/sleep/meditation audio.

**Unique: no MCP server for brainwave exists anywhere.**

### 3. Brainwave Content Packs (7.2/10)

Pre-made sessions:
- Deep Sleep 45min
- Focus Progressive 30min
- Meditation Theta 20min

Sell on Gumroad/Stripe: $5-20 per pack or $9/mo subscription.

### 4. Embeddable Brainwave Widget (7.0/10)

JavaScript widget for blogs/educators. Pro tier: custom branding.

---

## Revenue Projections

| Scenario | Year 1 | Year 2 |
|----------|--------|--------|
| API only (100 users) | $10K | $30K |
| API + content packs | $15K | $50K |
| API + packs + B2B | $25K | $100K |

---

## What Needs to Be Built

| Priority | Task |
|----------|------|
| P0 | Fix build (brainwave.rs compiles, API serves WAV) |
| P0 | MCP server wiring |
| P1 | More presets (sleep, meditation, gamma burst) |
| P1 | Landing page with session preview player |
| P2 | Stripe integration |
| P2 | Content pack exports |

---

## The Honest Risk

Science says effects are "small and inconsistent." Brain.fm spent millions on RCTs.

**But you can compete on:**
- Accessibility (free/open, API-first, agent-native)
- Verification (prove the WAV is what it claims)
- Integration (MCP, agents, music production)
- Niche (AI agent generating focus music is novel)

**The Monroe Institute charges $500+ for Hemi-Sync CDs. Your API does the same for free.**

---

*End of thesis*
