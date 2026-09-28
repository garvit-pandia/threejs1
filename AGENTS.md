# AGENTS.md — working rules for `threejs1`

Guidance for agents and humans working in this repo. Read this before editing.

**Dev URL:** http://localhost:5180 — pinned in `vite.config.js`
(`server.port: 5180, strictPort: true`)
**Preview URL:** http://localhost:5181 — pinned (`preview.port: 5181, strictPort: true`)

This repo is part of the `~/projects2` workspace and inherits its protocol from
`../AGENTS.md`: ports are registered in `../PORT-REGISTRY.md` before use, and
`server.watch.usePolling` must stay enabled (native file watching serves stale
modules under WSL2).

---

## 1. Single-file rule

All application code lives in **`index.html`** — markup, CSS, the Three.js
scene, the simulation and the UI wiring. Do not create new modules, components
or build steps. The only other source files permitted are:

```
public/textures/*        texture assets
tools/seaway_check.py    the offline corridor validator
docs/screenshots/*       renders referenced by the README
```

If a change feels like it needs a module, it does not — put it in `index.html`.

## 2. Hard invariants

These are load-bearing. Breaking one is a regression even if it looks fine.

### One sun

`scene` contains exactly **one** `DirectionalLight` and **no** ambient or
hemisphere fill. The night side of every body is dark because the sun is the
only source. Do not add a fill light to "brighten the dark side" — raise
`toneMappingExposure`, or the night floor inside `earthMaterial`'s fragment
shader (`mix(0.20, 1.0, dayMix)`), instead.

Verify with `window.__app.audit().lights` — it must equal `["DirectionalLight"]`.

### Lanes stay on water

Freight lanes are routed through the maritime corridor graph
(`WAYPOINTS` + `EDGES` in `index.html`), never along raw great circles. After
**any** change to a port, waypoint, edge or coastal coordinate:

```
python3 tools/seaway_check.py     # must print "0 crossing > 90 km of land"
```

The script keeps its own copy of the same graph and must stay in sync with the
one embedded in `index.html`. Canal and strait transits that legitimately touch
land belong in the script's `ALLOW` set — not in a raised `CROSS_KM` threshold.

### Layout contract

- `#topbar` and `#bottombar` are `.panel`s, whose base rule sets
  `flex-direction: column`. Both **must** explicitly override to `row`. An
  inherited-column regression once cost 41% of the viewport.
- `#topbar` is `flex-wrap: nowrap` with a fixed height and sheds chrome per
  density tier (1560 / 1460 / 1360 / 1280 / 1200 / 1120 px). Never let it wrap
  to a second row — add a tier instead.
- No functional text below **10.5 px**; interactive targets at least **34 px**
  tall.
- `@media (max-width: 1000px)` turns the grid into a scrollable bottom sheet.
  A new panel must size to content there and clear the fixed `#bottombar`.

### Texture colour spaces

Colour maps load as `SRGBColorSpace`; data maps (`earth_specular.jpg`,
`earth_normal.jpg`) load as `NoColorSpace`. Getting this wrong washes out or
over-darkens the surface.

### Custom shaders

Custom `ShaderMaterial` fragment shaders include `#include <tonemapping_fragment>`
(three's fragment prefix defines the `toneMapping()` function) but **not**
`#include <colorspace_fragment>`, because `linearToOutputTexel()` is only
defined for built-in materials — including it fails to compile.

## 3. Commands

```bash
npm install
npm run dev                       # dev server  → http://localhost:5180
npm run build                     # production bundle
npm run preview                   # serve build → http://localhost:5181
python3 tools/seaway_check.py     # corridor graph validator (exit 1 on failure)
```

## 4. How to verify a change

There is **no unit-test suite** — this is a visual, continuously simulated app,
so verify it by driving it. Never claim a UI change works from the diff alone.

1. Run the dev server and confirm
   `window.__app.ready === true` and `window.__app.errors` is empty.
2. Drive the actual surface: dispatch a route from the planner, click a
   shipment row, acknowledge an alert, cycle all four camera presets, move the
   sun slider, pause and change speed.
3. Check the invariants in §2, plus `window.__app.audit().lights`.
4. Check layout at **1680 / 1500 / 1440 / 1366 / 1280 / 1200 / 1100 / 1024 px**:
   the top bar must stay one row (52 px), with no clipped children and no
   horizontal document overflow.
5. `python3 tools/seaway_check.py` if you touched geography.

`window.__app` is the verification surface and its names are **stable API** —
keep them working:

`shipments`, `alerts`, `stats`, `errors`, `materials`, `sim`,
`audit()`, `addShipment()`, `setSunAzimuth()`, `setPaused()`, `cameraPreset()`,
`focus()`, `planetKeys()`, `shipmentSnapshot()`, `cameraInfo()`.

## 5. Code style

- The file is one long ES module. Keep sections in their existing order and
  honour the `/* ---- section ---- */` banners; declarations are order-sensitive
  (helpers before the modules that call them).
- Prefer `assert`-style scripted edits: when patching with a script, assert the
  exact match count before replacing, so a stale string fails loudly instead of
  silently skipping an edit.
- Keep the design tokens in `:root` (colours, `--mono`, `--ui`) as the single
  source of truth for the glass look.
- Delete dead code and unused uniforms rather than commenting them out.

## 6. Documentation duties

- **`README.md`** — user-facing: what the app does, how to run it, assets and
  licences, known limitations. Update it when behaviour or commands change.
- **`CHANGELOG.md`** — every round of review or notable fix, with the measured
  before/after numbers.
- **This file** — the invariants above. If you discover a new load-bearing
  rule, add it here.

## 7. Port discipline

Before binding or killing anything: read `../PORT-REGISTRY.md` and run
`ss -ltnp`. Never bind an owned or reserved port (9222 and 46537 are
untouchable). `EADDRINUSE` means *open the owner's URL*, not *kill the
occupant*. Claiming a new port requires all four steps in the workspace
protocol — registry row, pinned `strictPort`, and updated README/AGENTS URLs.
