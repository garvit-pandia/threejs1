# threejs1 — project rules

**Dev URL:** http://localhost:5180 (pinned in `vite.config.js`: `port: 5180, strictPort: true`)
**Production preview:** http://localhost:5181 (`preview: { port: 5181, strictPort: true }`)

Freight-tracking logistics dashboard. **Single-file app**: all application code
(HTML, CSS, Three.js scene, UI, simulation) lives in `index.html`.
Assets are the only other source files (`public/textures/*`).

## Rules

- Keep it single-file. New features go into `index.html`, not new modules.
- Never change the dev port without following the workspace port protocol
  (`~/projects2/PORT-REGISTRY.md` row + `strictPort` + this file).
- `server.watch.usePolling` MUST stay enabled (WSL2 serves stale modules otherwise).
- Verify by running the dev server and driving it in a real browser
  (screenshots + `window.__app` state), not by unit tests.
- Runtime texture budget: keep the 2K/4K maps in `public/textures` (≈3.4 MB total).
  Do not swap them for remote URLs — the app must work offline after checkout.

## Seaway corridors

Freight lanes follow a maritime corridor graph (waypoints + edges) embedded in
`index.html` — great circles would cut straight over continents. The graph is
validated against the ocean mask (`public/textures/earth_specular.jpg`) by:

```
python3 tools/seaway_check.py     # fails if any corridor crosses > 90 km of terrain
```

Whenever you add, move, or re-link a waypoint/port, re-run that script **and**
re-check the embedded copy in `index.html` (the two lists must stay identical).
Canal/strait transits that legitimately touch terrain in the mask live in the
`ALLOW` set of the script.

## Layout contract

- `#topbar` and `#bottombar` are **rows**: they must keep
  `flex-direction: row` (they are `.panel`s, whose default is `column` — an
  inherited-column regression previously cost 41% of the viewport).
- `@media (max-width: 1000px)` turns the panel grid into a scrollable bottom
  sheet. If you add a panel, confirm it still sizes to content there and that
  it clears the fixed `#bottombar`.
- Type floor: no functional text below 10.5px; interactive targets ≥34px tall.

## Verification surface

`window.__app` exposes the verification surface (`shipments`, `alerts`, `stats`,
`errors`) plus helpers `addShipment`, `setSunAzimuth`, `setPaused`, `cameraPreset`,
`focus`, `shipmentSnapshot`. Keep these names stable — smoke checks depend on them.
