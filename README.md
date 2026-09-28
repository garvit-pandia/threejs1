# TERRA FREIGHT — 3D freight-tracking dashboard

A single-file Three.js command dashboard: a realistic 3D Earth at the centre of a
starry solar system, wrapped in glass UI panels for live shipment tracking, route
planning, delivery statistics and risk alerts.

**Dev:** `npm install && npm run dev` → http://localhost:5180
**Production check:** `npm run build && npm run preview` → http://localhost:5181

## What's in it

| Area | Detail |
|---|---|
| Earth | 4K day + 4K night maps, cloud layer, ocean specular glint, normal mapping, soft day/night terminator, additive atmosphere rim + horizon halo, night-side city lights |
| Sun | one `DirectionalLight` lighting every body; billboard sun sprite; azimuth slider (0–360°) drives the terminator live |
| Moon | 2K lunar map, tidally locked, inclined orbit (5.14°) around Earth, driven by the simulation clock |
| Planets | Jupiter, Saturn (with alpha-textured tilted ring system), Mars, Neptune — all lit by the same sun, each with its own axial tilt and spin |
| Background | ~9,750 twinkling stars in three layers with a galactic band |
| Lanes | great-circle shipping routes with animated dashed tracks, travelling vessel markers, per-leg progress |
| Panels | Live Shipments, Route Planner, Delivery Statistics, Risk Alerts — all frosted glass with live data |
| Simulation | 12 seeded lanes, 12 ports, 7 cargo classes, 3 priorities, hazard/chokepoint risk model, random incidents, delivery + on-time accounting |

## Controls

- **drag** orbit · **scroll** zoom
- **Earth / System / Moon / Follow** camera presets (keys `1`–`4`)
- **Pause / 1×–4×** simulation control (`Space` toggles pause)
- **sun** slider rotates the light and therefore the day/night terminator
- click a shipment row, alert or vessel marker to select and focus it
- hover a vessel marker for a telemetry tooltip

## Assets

`public/textures/` — equirectangular planetary maps (≈3.4 MB):

- Earth day/night (4K), clouds, normal, ocean specular — from the three.js
  `examples/textures/planets` set
- Moon (1024), Jupiter, Saturn (+ ring alpha), Mars, Neptune (2K) — from
  [solarsystemscope.com](https://www.solarsystemscope.com/textures/) (CC BY 4.0)

The app is fully offline after checkout; textures are never fetched from a CDN
at runtime. If a texture is missing it falls back to an error log entry in
`window.__app.errors` and a procedural placeholder.

## Layout

Three columns above 1000px: a stats/alert rail, the 3D view, and a
shipments/planner rail, with single-row top and bottom bars.

At **≤1000px** the panels move into a scrollable bottom sheet occupying the
lower ~62% of the viewport; the upper part stays a clean drag/zoom area for the
globe, the top bar pins to the top, and the legend bar pins to the bottom.

Every interactive control is at least 34px tall, and no functional text is
smaller than 10.5px.

## Maintenance

`tools/seaway_check.py` validates the embedded maritime corridor graph against
the ocean mask and exits non-zero if any corridor crosses more than 90 km of
terrain. Run it after any change to ports or waypoints:

```
python3 tools/seaway_check.py
```

## Quality loop

The dashboard has been through a critique-and-improve loop with a dedicated
reviewer agent scoring real screenshots against the running app. Findings and
the resulting changes are recorded in `CHANGELOG.md`; that file also lists the
known-open issues.

## Verification surface

`window.__app` exposes `shipments`, `alerts`, `stats`, `errors` and the helpers
`addShipment(from, to, cargo, priority)`, `setSunAzimuth(deg)`, `setPaused(bool)`,
`cameraPreset(name)`, `focus(id)`, `shipmentSnapshot()`, `cameraInfo()`.
