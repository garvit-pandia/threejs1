# Changelog

## Round 3 — interaction fixes (live feature sweep)

A full browser-driven feature pass (all four camera presets via buttons and
keyboard, sun slider, pause/speed, planner preview + dispatch, row selection,
alert acknowledgement, marker hover tooltip, responsive matrix at
1680/1366/1280/1024/900/480, then a 17-minute soak) surfaced two real defects
and a first-paint polish item; all three are fixed here.

### Fixed

- **Preset highlight never cleared.** `setPreset` deselected via
  `#topbar .seg:first-of-type button`, but `#brand` is the first `div` child of
  `#topbar`, so no `.seg` is ever `:first-of-type` — the selector matched
  nothing and `.on` accumulated on every preset button (all four lit after
  clicking each once). Fixed to `#topbar .seg button`; exactly one preset pill
  is lit at all times across clicks and keys 1–4. The same dead selector in the
  600px media query had silently never applied either; it now does, and at
  480px the seg buttons measure `8px 9px` with the top bar still one 52px row,
  zero clipped children and no horizontal overflow.
- **Canvas cursor stuck on `pointer`.** The hover hit branch set
  `renderer.domElement.style.cursor` while the miss branch reset
  `document.body.style.cursor` — mismatched targets, so the pointer cursor
  never cleared after the first marker hover. The miss path now resets the
  canvas itself; verified `pointer` on a marker, `''` off it.
- **Shipment rows rendered empty for up to one UI tick.** Rows were created by
  `refreshShipmentRows` but only filled by the 0.28s-throttled loop, so the
  list flashed blank after boot and after each dispatch. `refreshShipmentRows`
  now calls `updateShipmentRow(s)` when it registers a row; rows are complete
  on creation.

### Verified (dev server, 5180)

`window.__app.ready === true`, `errors` empty; rows filled on first read after
load; single `.on` preset across button and keyboard paths; hover tooltip
renders on a paused marker and the cursor resets on leave; responsive matrix
1680/1366/1280/1024/900/480 — top bar 52px single row, no clipping, no
horizontal overflow.

## Round 1 — UI repair (critique verdict 4/10)

First round of the critique-and-improve loop. A dedicated critic agent reviewed
seven real renders (1680×1000, 1366×768, 900×620, 480×800, system, moon and
tooltip views) and rated the dashboard **4/10** — Visual design 5, Information
design 4, Interaction & accessibility 3, Robustness across viewport sizes 2.

Both headline blockers were reproduced with measurements before being fixed,
not taken on the critic's word.

### Fixed

- **Top/bottom bars stacked into empty glass.** `#topbar` and `#bottombar`
  inherited `.panel { flex-direction: column }`, so they laid their children out
  vertically: `#topbar` measured **244px** and `#bottombar` **166px**, together
  wasting **41% of a 1000px viewport** and letterboxing the globe. Both are now
  explicit rows → **54px** and **29px**
  (`#topbar,#bottombar{flex-direction:row;flex-wrap:wrap;align-items:center}`).
- **Type floor.** ~11 text styles sat below 10px (8.5–9.5px) over a
  `backdrop-filter: blur(16px)` surface, and several dim values fell under
  ~5:1 contrast. All functional text raised to ≥10.5px; `--dim` / `--muted`
  text colours lightened (`#63779a` → `#93a8c8`, `#8ea3c4` → `#a7bad6`).
- **Hit targets.** Buttons 26px → ≥34px tall; range input 3px track → 22px with
  a 13px → 19px thumb; selects → 36px; dispatch button → 40px.
- **`≤1000px` layout.** Previously the grid collapsed into overlapping panels
  that covered the 3D scene entirely (confirmed by screenshot). It is now a
  scrollable bottom sheet: panels size to their content, the upper ~38% stays a
  clean drag/zoom area, the legend bar fixes to the bottom, and the projected
  planet labels are hidden.

### Verified (dev server, 5180)

No panel overlap, no horizontal overflow, shipments reachable, scene
unobstructed, `window.__app.errors` empty, no console errors — at 1680×1000,
1366×768, 900×620 and 480×800. Maritime distances unchanged and still
real-world accurate (Shanghai→Rotterdam 20,560 km; Singapore→Los Angeles
14,511 km). `tools/seaway_check.py` still reports 0 corridors crossing >90 km
of terrain.

### Still open (Rounds 2+ deferred)

- Earth shader: night side near-black, city-light orange smear, rust-coloured
  terminator ring, white specular blob; atmosphere/halo neon stroke.
- Freight lanes and vessel markers are sub-pixel and invisible at System
  distance; status encoded by colour alone (red-green unsafe); the colour legend
  is detached from the shipment list it decodes.
- Information design: missing denominators/units; `Avg ETA` shown with 0 legs;
  contradictory sim readout (`1×` button vs `sim 2×` in the clock).
- Accessibility: no `:focus-visible` rings, no ARIA, hover-only discovery.
- Performance: ~5 FPS in this environment — diagnosed as fill-rate bound
  (11 → 8 → 5 FPS scaling purely with pixel count under llvmpipe), not a
  logic defect.

## Round 2 — scene, legibility and chrome

Second round, driven by the critic's remaining findings plus a wrap defect found
while reviewing the running app at 1440x900.

### Fixed

- **Top bar wrapped to a second row between 1280 and 1500 px.** Round 1's
  hit-target padding pushed the control row past the available width, so
  `#topbar` measured 95px at 1440 (two rows) while being 54px at 1680. The bar
  is now `flex-wrap: nowrap` with a definite 52px height and sheds
  non-essential chrome per density tier (mark badge, section labels, brand
  tagline, sun label, clock sub-line, status pill, clock, slider) at 1560 /
  1460 / 1360 / 1280 / 1200 / 1120 px. Measured: **52px, one row, zero clipped
  children and no horizontal overflow at every width from 1024 to 1680**.
- **Earth surface rebalanced** (critic F5). City lights `pow(lum,1.25)*2.55` →
  `pow(lum,1.65)*1.45` and `uNightBoost` 1.0 → 0.72 (the orange harbour smear is
  gone); terminator band `pow(twilight,7)*0.30` → `pow(twilight,9)*0.16` (rust
  ring gone); ocean glint exponent 190 → 380 and gain 0.55 → 0.28 (white blob
  gone); night floor `0.115` → `0.20` so the dark side stays readable rather
  than black; cloud opacity 0.86 → 0.58 so clouds stop washing out the lights.
- **Atmosphere and halo de-glared** (critic F6). Halo `3.6R` → `2.3R` with a
  tighter `exp` falloff and alpha 0.9 → 0.62, colour `0x3f8fe0` → `0x2a6cb8`;
  atmosphere rim power 3.2 → 4.4 and gain 1.55 → 1.05; sun glow sprite 430 →
  280 with opacity 0.85 → 0.50.
- **Freight is visible at distance** (critic F7). Planned dashes enlarged
  (`dashSize` 0.34 → 0.55, opacity 0.34 → 0.50, active legs 0.32 → 0.50);
  vessel cone 0.30×1.05 → 0.42×1.35; marker glow 2.6 → 3.4; port dots 1.5 → 2.1.
- **Status no longer depends on colour alone.** The vessel mesh is now swapped
  per status — cone (in transit), octahedron (delayed), cube (at risk), sphere
  (delivered) — matching new ▲ ◆ ■ ● glyphs in the shipment rows, so the
  encoding survives deuteranopia.
- **Legend moved next to what it decodes** (critic F8). An inline key row now
  sits directly above the Live Shipments list; the duplicate detached legend was
  removed from the bottom bar, which keeps only the run totals and the hint.
- **Contradictory simulation readout removed.** The clock sub-line no longer
  prints a speed that could disagree with the speed button; speed is shown once,
  on the button. The pause button label now also tracks programmatic pauses.

### Verified (dev server, 5180)

`window.__app.errors` empty; 12 shipments and 2 alerts live; exactly one light
(`["DirectionalLight"]`); top bar 52px single-row at 1024/1100/1200/1280/1366/
1440/1500/1680 with no clipping and no horizontal overflow; corridor validator
still reports `111 edges · 0 crossing > 90 km of land`.

### Still open (Round 3)

- Accessibility: no `:focus-visible` rings, no ARIA labelling, no
  reduced-motion mode, touch gestures untuned.
- Information design: `Avg ETA` still reads oddly with few legs to average;
  some units lack explicit windows.
- Performance under software rasterisation (llvmpipe) remains fill-rate bound.
