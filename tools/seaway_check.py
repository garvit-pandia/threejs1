#!/usr/bin/env python3
"""Validate the seaway corridor graph against the ocean mask.

Samples every corridor edge finely (200 steps) on a great circle, measures the
longest contiguous run of land samples in km, and fails when a corridor crosses
more than CROSS_KM kilometres of terrain. Narrow canal/strait transits are
explicitly allowed.

Run: python3 tools/seaway_check.py
"""
import math, sys
from PIL import Image

CROSS_KM = 90            # a run longer than this means a real landmass crossing
ALLOW = {                 # canal / strait transits that legitimately touch land in the mask
    ('Panama', 'Gulf of Panama'), ('Gulf of Panama', 'Panama'),
    ('Red Sea', 'Suez'), ('Suez', 'Levantine Basin'),
    ('Bass Strait', 'AUSYD'), ('AUSYD', 'Bass Strait'),
    ('Tasman South', 'Bass Strait'), ('Bass Strait', 'Tasman South'),
    ('Alboran Sea', 'Gibraltar'), ('Gibraltar', 'Alboran Sea'),
    ('Durban Roads', 'ZADUR'), ('Sydney Coast', 'AUSYD'),
    ('Santos Roads', 'BRSSZ'), ('Elbe Approach', 'DEHAM'),
    ('Southern North Sea', 'NLRTM'), ('Malacca Strait', 'SGSIN'),
    ('CNSHA', 'East China Sea'), ('KRPUS', 'East China Sea'),
    ('English Channel', 'Dover Strait'), ('Channel East', 'Dover Strait'),
    ('Levantine Basin', 'South of Crete'), ('Colombo Roads', 'South of Sri Lanka'),
}

MASK = Image.open('public/textures/earth_specular.jpg').convert('L')
W, H = MASK.size
PX = MASK.load()

PORTS = [
    ('CNSHA', 'Shanghai', 31.23, 121.47), ('SGSIN', 'Singapore', 1.29, 103.85),
    ('NLRTM', 'Rotterdam', 51.95, 4.14), ('USLAX', 'Los Angeles', 33.74, -118.27),
    ('AEJEA', 'Jebel Ali', 25.01, 55.06), ('BRSSZ', 'Santos', -23.96, -46.33),
    ('KRPUS', 'Busan', 35.18, 129.08), ('DEHAM', 'Hamburg', 53.55, 9.99),
    ('USNYC', 'New York', 40.67, -74.01), ('INBOM', 'Mumbai', 18.95, 72.84),
    ('ZADUR', 'Durban', -29.87, 31.03), ('AUSYD', 'Sydney', -33.87, 151.21),
    ('Panama', 'Panama', 8.90, -79.55),
]

WAYPOINTS = [
    # East Asia
    ('East China Sea', 30.00, 126.50), ('Pacific Exit', 30.80, 133.20),
    ('NW Pacific', 32.50, 146.00), ('North Pacific', 33.00, -165.00),
    ('East of Taiwan', 22.50, 124.20), ('Luzon Strait', 20.50, 121.50),
    ('Philippine Sea', 12.00, 130.00), ('South China Sea', 13.00, 114.00),
    ('Natuna Sea', 3.00, 106.50), ('Singapore Strait', 1.24, 104.20),
    ('Malacca Strait', 2.00, 102.60), ('Malacca West', 3.10, 101.30),
    ('Malacca North', 4.20, 100.00), ('Northern Malacca', 5.60, 97.80),
    ('Banda Aceh', 6.00, 95.50),
    # Indonesia / Australia
    ('Sulu Sea', 8.00, 119.50), ('Celebes Sea', 3.50, 123.50),
    ('Sulawesi Sea', 2.50, 119.50), ('Makassar Strait', 0.00, 118.60),
    ('Flores Sea', -8.00, 119.50), ('Banda Sea', -5.50, 128.00),
    ('Arafura Sea', -9.00, 135.00), ('Torres Approach', -10.50, 146.00),
    ('Coral Sea', -18.00, 155.00), ('Tasman Sea', -30.00, 158.00),
    ('Tasman South', -36.00, 152.00), ('Sydney Coast', -33.50, 154.00),
    ('Bass Strait', -39.50, 146.80), ('Great Aus Bight', -36.50, 128.00),
    ('SW Australia', -35.00, 105.00),
    # Indian Ocean
    ('Indian Ocean', -25.00, 80.00), ('South of Sri Lanka', 4.80, 80.60),
    ('Colombo Roads', 6.50, 79.50), ('Bay of Bengal', 14.00, 88.00),
    ('Arabian Sea', 15.50, 62.00), ('Oman Basin', 22.50, 60.60),
    ('Hormuz', 26.40, 56.40), ('Socotra Passage', 12.80, 54.50),
    ('Gulf of Aden', 12.30, 47.60), ('Bab el-Mandeb', 12.60, 43.40),
    ('Red Sea', 20.00, 38.00), ('Suez', 30.10, 32.60),
    # Mediterranean
    ('Levantine Basin', 33.00, 30.50), ('South of Crete', 34.00, 24.00),
    ('Central Med', 35.00, 18.00), ('Ionian Sea', 35.60, 15.20),
    ('Sicily Channel', 36.60, 12.50), ('Sardinia Channel', 38.00, 9.60),
    ('Algerian Basin', 37.20, 3.50), ('Alboran Sea', 36.20, -1.80),
    ('Gibraltar', 35.90, -5.60),
    # Atlantic Europe
    ('Cape St Vincent', 36.60, -9.30), ('Finisterre', 43.90, -9.80),
    ('Biscay', 45.60, -6.00), ('Ushant', 48.70, -5.80),
    ('English Channel', 49.95, -2.30), ('Channel East', 50.15, 0.20),
    ('Dover Strait', 51.05, 1.45), ('Southern North Sea', 52.60, 3.00),
    ('German Bight', 54.20, 6.60), ('Elbe Approach', 54.00, 8.20),
    ('North Atlantic', 46.00, -38.00),
    # Americas
    ('New York Roads', 39.80, -71.50), ('Bermuda Rise', 30.00, -60.00),
    ('Atlantic Approach', 21.00, -57.00), ('Anegada Passage', 19.30, -64.60),
    ('Caribbean', 15.50, -68.50), ('Venezuela Basin', 13.50, -70.00),
    ('Colombia Basin', 12.00, -77.50), ('Gulf of Panama', 6.00, -80.50),
    ('Equatorial Atlantic', 2.00, -38.00), ('NE Brazil', -9.00, -30.50),
    ('Abrolhos', -18.00, -38.00), ('South Brazil', -30.00, -45.00),
    ('Santos Roads', -25.60, -44.20), ('South Atlantic', -25.00, -25.00),
    ('Agulhas Bank', -35.80, 22.50), ('Southern Agulhas', -36.50, 27.00),
    ('Durban Roads', -30.50, 31.60), ('Cape of Good Hope', -35.00, 19.50),
    # Pacific
    ('Central Pacific', 12.00, -115.00), ('South Pacific', -20.00, -140.00),
]

EDGES = [
    # East Asia
    ('CNSHA', 'East China Sea'), ('KRPUS', 'East China Sea'),
    ('East China Sea', 'Pacific Exit'), ('East China Sea', 'East of Taiwan'),
    ('Pacific Exit', 'NW Pacific'),
    ('NW Pacific', 'North Pacific'), ('NW Pacific', 'Luzon Strait'),
    ('East of Taiwan', 'South China Sea'), ('East of Taiwan', 'Luzon Strait'),
    ('Luzon Strait', 'Philippine Sea'), ('Luzon Strait', 'South China Sea'),
    ('Philippine Sea', 'Celebes Sea'),
    ('South China Sea', 'Natuna Sea'), ('South China Sea', 'Sulu Sea'),
    ('Sulu Sea', 'Celebes Sea'), ('Celebes Sea', 'Sulawesi Sea'),
    ('Natuna Sea', 'Singapore Strait'),
    ('Singapore Strait', 'SGSIN'), ('Singapore Strait', 'Malacca Strait'),
    ('Malacca Strait', 'Malacca West'), ('Malacca West', 'Malacca North'),
    ('Malacca North', 'Northern Malacca'), ('Northern Malacca', 'Banda Aceh'),
    ('Banda Aceh', 'South of Sri Lanka'),
    # Indonesia -> Australia
    ('Sulawesi Sea', 'Makassar Strait'), ('Makassar Strait', 'Flores Sea'),
    ('Flores Sea', 'Banda Sea'), ('Banda Sea', 'Arafura Sea'),
    ('Arafura Sea', 'Torres Approach'), ('Torres Approach', 'Coral Sea'),
    ('Coral Sea', 'Sydney Coast'), ('Sydney Coast', 'AUSYD'),
    ('Coral Sea', 'Tasman Sea'), ('Tasman Sea', 'Tasman South'),
    ('Tasman Sea', 'Bass Strait'), ('Tasman South', 'Bass Strait'),
    ('Bass Strait', 'AUSYD'), ('Bass Strait', 'Great Aus Bight'),
    ('Great Aus Bight', 'SW Australia'), ('SW Australia', 'Indian Ocean'),
    # Indian Ocean
    ('South of Sri Lanka', 'Colombo Roads'), ('South of Sri Lanka', 'Bay of Bengal'),
    ('Colombo Roads', 'Arabian Sea'),
    ('Indian Ocean', 'Colombo Roads'), ('INBOM', 'Arabian Sea'),
    ('Arabian Sea', 'Gulf of Aden'), ('Arabian Sea', 'Oman Basin'),
    ('Arabian Sea', 'Socotra Passage'), ('Socotra Passage', 'Gulf of Aden'),
    # Persian Gulf
    ('AEJEA', 'Hormuz'), ('Hormuz', 'Oman Basin'), ('Oman Basin', 'Socotra Passage'),
    # Red Sea / Suez / Med
    ('Gulf of Aden', 'Bab el-Mandeb'), ('Bab el-Mandeb', 'Red Sea'), ('Red Sea', 'Suez'),
    ('Suez', 'Levantine Basin'), ('Levantine Basin', 'South of Crete'),
    ('South of Crete', 'Central Med'), ('Central Med', 'Ionian Sea'),
    ('Ionian Sea', 'Sicily Channel'), ('Sicily Channel', 'Sardinia Channel'),
    ('Sardinia Channel', 'Algerian Basin'), ('Algerian Basin', 'Alboran Sea'),
    ('Alboran Sea', 'Gibraltar'),
    # Europe
    ('Gibraltar', 'Cape St Vincent'), ('Cape St Vincent', 'Finisterre'),
    ('Finisterre', 'Biscay'), ('Biscay', 'Ushant'), ('Ushant', 'English Channel'),
    ('English Channel', 'Channel East'), ('Channel East', 'Dover Strait'),
    ('Dover Strait', 'Southern North Sea'), ('Southern North Sea', 'NLRTM'),
    ('Southern North Sea', 'German Bight'), ('German Bight', 'Elbe Approach'),
    ('Elbe Approach', 'DEHAM'), ('English Channel', 'North Atlantic'),
    ('Finisterre', 'North Atlantic'),
    # Atlantic
    ('North Atlantic', 'New York Roads'), ('New York Roads', 'USNYC'),
    ('New York Roads', 'Bermuda Rise'), ('Bermuda Rise', 'Atlantic Approach'),
    ('Atlantic Approach', 'Anegada Passage'), ('Anegada Passage', 'Caribbean'),
    ('Caribbean', 'Venezuela Basin'), ('Venezuela Basin', 'Colombia Basin'),
    ('Colombia Basin', 'Gulf of Panama'), ('Gulf of Panama', 'Panama'),
    ('Caribbean', 'Equatorial Atlantic'), ('Equatorial Atlantic', 'NE Brazil'),
    ('NE Brazil', 'Abrolhos'), ('Abrolhos', 'South Brazil'),
    ('South Brazil', 'Santos Roads'), ('Santos Roads', 'BRSSZ'),
    ('South Brazil', 'South Atlantic'), ('South Atlantic', 'NE Brazil'),
    # Africa south
    ('South Atlantic', 'Agulhas Bank'), ('South Atlantic', 'Cape of Good Hope'),
    ('Cape of Good Hope', 'Agulhas Bank'), ('Agulhas Bank', 'Southern Agulhas'),
    ('Southern Agulhas', 'Durban Roads'), ('Durban Roads', 'ZADUR'),
    ('Indian Ocean', 'Cape of Good Hope'), ('Indian Ocean', 'SW Australia'),
    # Pacific
    ('Panama', 'Gulf of Panama'), ('Gulf of Panama', 'Central Pacific'),
    ('Central Pacific', 'USLAX'), ('Central Pacific', 'North Pacific'),
    ('North Pacific', 'USLAX'), ('North Pacific', 'South Pacific'),
    ('South Pacific', 'Tasman Sea'),
]

NODES = {}
for code, name, lat, lon in PORTS:
    NODES[code] = (lat, lon)
    NODES[name] = (lat, lon)
for name, lat, lon in WAYPOINTS:
    NODES[name] = (lat, lon)


def ll2v(lat, lon):
    r, t = math.radians(lat), math.radians(lon)
    return (math.cos(r) * math.sin(t), math.sin(r), math.cos(r) * math.cos(t))


def v2ll(v):
    n = math.sqrt(sum(c * c for c in v))
    x, y, z = (c / n for c in v)
    return math.degrees(math.asin(y)), math.degrees(math.atan2(x, z))


def gc(a, b, t):
    va, vb = ll2v(*a), ll2v(*b)
    dot = max(-1, min(1, sum(p * q for p, q in zip(va, vb))))
    om = math.acos(dot)
    if om < 1e-6:
        return a
    s = math.sin(om)
    w1, w2 = math.sin((1 - t) * om) / s, math.sin(t * om) / s
    return v2ll(tuple(w1 * p + w2 * q for p, q in zip(va, vb)))


def is_land(lat, lon):
    x = int(round((lon + 180) / 360 * W)) % W
    y = min(H - 1, max(0, int(round((90 - lat) / 180 * H))))
    return PX[x, y] < 40


def edge_report(a_name, b_name, steps=200):
    a, b = NODES[a_name], NODES[b_name]
    total_km = 6371 * math.acos(max(-1, min(1, sum(p * q for p, q in zip(ll2v(*a), ll2v(*b))))))
    step_km = total_km / steps
    hits, run, worst, worst_at = 0, 0, 0.0, None
    for i in range(steps + 1):
        lat, lon = gc(a, b, i / steps)
        if is_land(lat, lon):
            hits += 1
            run += 1
            if run * step_km > worst:
                worst, worst_at = run * step_km, (round(lat, 1), round(lon, 1))
        else:
            run = 0
    return hits, worst, worst_at, total_km


def main():
    bad = []
    for a, b in EDGES:
        for n in (a, b):
            if n not in NODES:
                print(f'MISSING NODE {n}')
                bad.append((a, b, 9999, None))
        if a not in NODES or b not in NODES:
            continue
        hits, worst, at, total = edge_report(a, b)
        allowed = (a, b) in ALLOW or (b, a) in ALLOW
        if worst > CROSS_KM and not allowed:
            bad.append((a, b, worst, at))
            print(f'✘ {worst:7.0f} km of terrain   {a:22s} -> {b:22s} at {at}  (edge {total:.0f} km)')
    print(f'\n{len(EDGES)} edges · {len(bad)} crossing > {CROSS_KM} km of land')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
