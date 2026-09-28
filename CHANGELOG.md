# Changelog

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
