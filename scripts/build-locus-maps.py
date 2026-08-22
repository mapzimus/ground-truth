#!/usr/bin/env python3
"""Render the study-page locus maps as SVG from Census state boundaries.

The originals were raster images drawn for the old dark theme: a thin
anti-aliased outline on near-black. Recolouring them for the light theme left
the coastline as faint stipple, so they are rebuilt as vector instead — crisp
at any size, a few KB each, and reproducible from a public source.

Source: US Census Bureau cartographic boundary file, 1:5,000,000 states.
        https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_us_state_5m.zip

Site markers are town-scale positions, which is all this map resolves: one
pixel here is roughly 750 m, so the dot covers the study area either way.

Usage:  python3 scripts/build-locus-maps.py
Needs:  pyshp  (pip install pyshp)
"""

from __future__ import annotations

import io
import math
import urllib.request
import zipfile
from pathlib import Path

import shapefile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

BOUNDARIES = "https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_us_state_5m.zip"
UA = "LidarSiteStudies/1.0 (https://maxwellhowegis.com/lidar-test/; mhowe.gis@gmail.com)"

WIDTH, HEIGHT, MARGIN = 480, 300, 16

# The map is drawn at 480px but displayed at 300 (see .locus in site.css). Geometry
# wants the higher resolution; annotation wants to be sized for what the reader
# actually sees, so labels, markers and strokes are specified at display scale and
# multiplied up. Numbers below are the sizes as rendered on the page.
DISPLAY_WIDTH = 300
K = WIDTH / DISPLAY_WIDTH

LABEL_SIZE = 11 * K
LABEL_GAP = 7 * K
DOT_ACTIVE = 3.2 * K
DOT_HALO = 4.9 * K
DOT_IDLE_R = 2.0 * K
STROKE_STATE = 1.0 * K
STROKE_NEIGHBOUR = 0.65 * K

# Quad Sheet palette — keep in step with :root in site.css.
PAPER = "#f4f0e6"
NEIGHBOUR_FILL = "#ece6d8"
NEIGHBOUR_LINE = "#cdc3ab"
STATE_FILL = "#e3dbc6"
CONTOUR = "#7a5327"
CONTOUR_DEEP = "#5e3f1d"
DOT_IDLE = "#7d765f"

# Study sites, north to south. "anchor" places the label clear of the coast.
SITES = [
    {"key": "devens",     "label": "Devens",       "lon": -71.6104, "lat": 42.5395, "anchor": "end"},
    {"key": "hopkinton",  "label": "Hopkinton",    "lon": -71.5200, "lat": 42.1800, "anchor": "end"},
    {"key": "middleboro", "label": "Middleborough", "lon": -70.9330, "lat": 41.9026, "anchor": "end"},
]


def load_states():
    """Return [(postal_code, [ring, ...]), ...] with rings as (lon, lat) lists."""
    request = urllib.request.Request(BOUNDARIES, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=120) as response:
        blob = response.read()

    archive = zipfile.ZipFile(io.BytesIO(blob))
    base = next(n[:-4] for n in archive.namelist() if n.endswith(".shp"))
    reader = shapefile.Reader(
        shp=io.BytesIO(archive.read(base + ".shp")),
        dbf=io.BytesIO(archive.read(base + ".dbf")),
        shx=io.BytesIO(archive.read(base + ".shx")),
    )
    fields = [f[0] for f in reader.fields[1:]]

    states = []
    for record in reader.iterShapeRecords():
        code = dict(zip(fields, record.record)).get("STUSPS")
        shape = record.shape
        bounds = list(shape.parts) + [len(shape.points)]
        rings = [shape.points[bounds[i]:bounds[i + 1]] for i in range(len(shape.parts))]
        states.append((code, rings))
    return states


def make_projection(bbox):
    """Equirectangular, longitude scaled by cos(mean latitude). Fine at one state."""
    lon_min, lat_min, lon_max, lat_max = bbox
    k = math.cos(math.radians((lat_min + lat_max) / 2))

    span_x = (lon_max - lon_min) * k
    span_y = lat_max - lat_min
    scale = min((WIDTH - 2 * MARGIN) / span_x, (HEIGHT - 2 * MARGIN) / span_y)

    off_x = (WIDTH - span_x * scale) / 2
    off_y = (HEIGHT - span_y * scale) / 2

    def project(lon, lat):
        return (
            off_x + (lon - lon_min) * k * scale,
            off_y + (lat_max - lat) * scale,
        )

    return project


def clip_ring(points, rect):
    """Sutherland-Hodgman clip of a projected ring to the view rectangle.

    Without this every state ships its full national geometry and the file runs
    to megabytes for a 480px map.
    """
    x0, y0, x1, y1 = rect
    edges = (
        (lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
        (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
        (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
        (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1)),
    )
    for inside, intersect in edges:
        if not points:
            return []
        clipped = []
        for i, current in enumerate(points):
            previous = points[i - 1]
            if inside(current):
                if not inside(previous):
                    clipped.append(intersect(previous, current))
                clipped.append(current)
            elif inside(previous):
                clipped.append(intersect(previous, current))
        points = clipped
    return points


def simplify(points, tolerance=0.35):
    """Drop points that sit within `tolerance` px of the running direction."""
    if len(points) < 3:
        return points
    kept = [points[0]]
    for point in points[1:-1]:
        last = kept[-1]
        if abs(point[0] - last[0]) >= tolerance or abs(point[1] - last[1]) >= tolerance:
            kept.append(point)
    kept.append(points[-1])
    return kept


def path_of(rings, project, precision=1):
    """Project, clip to just past the frame, thin, and emit as SVG path data."""
    bleed = (-8, -8, WIDTH + 8, HEIGHT + 8)
    out = []
    for ring in rings:
        if len(ring) < 3:
            continue
        points = simplify(clip_ring([project(lon, lat) for lon, lat in ring], bleed))
        if len(points) < 3:
            continue
        head = points[0]
        body = "".join(f"L{x:.{precision}f},{y:.{precision}f}" for x, y in points[1:])
        out.append(f"M{head[0]:.{precision}f},{head[1]:.{precision}f}{body}Z")
    return "".join(out)


def bbox_of(rings):
    xs = [p[0] for ring in rings for p in ring]
    ys = [p[1] for ring in rings for p in ring]
    return (min(xs), min(ys), max(xs), max(ys))


def build(states, active):
    massachusetts = next(rings for code, rings in states if code == "MA")
    project = make_projection(bbox_of(massachusetts))

    neighbours = ""
    for code, rings in states:
        if code == "MA":
            continue
        path = path_of(rings, project)
        if path:
            neighbours += f'<path d="{path}"/>'


    markers = []
    for site in SITES:
        x, y = project(site["lon"], site["lat"])
        if site["key"] == active:
            dx = -LABEL_GAP if site["anchor"] == "end" else LABEL_GAP
            markers.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{DOT_HALO:.1f}" fill="{PAPER}" opacity="0.9"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{DOT_ACTIVE:.1f}" fill="{CONTOUR}"/>'
                f'<text x="{x + dx:.1f}" y="{y + LABEL_SIZE * 0.35:.1f}" '
                f'text-anchor="{site["anchor"]}" class="lbl">{site["label"]}</text>'
            )
        else:
            markers.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{DOT_IDLE_R:.1f}" fill="{DOT_IDLE}"/>'
            )

    title = next(s["label"] for s in SITES if s["key"] == active)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" \
width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="Location of the \
{title} study area within Massachusetts">
<title>{title} study area within Massachusetts</title>
<style>
.lbl {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: {LABEL_SIZE:.1f}px; font-weight: 600; letter-spacing: 0.05em;
        fill: {CONTOUR_DEEP}; paint-order: stroke; stroke: {PAPER}; stroke-width: {3 * K:.1f};
        stroke-linejoin: round; }}
</style>
<clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}"/></clipPath>
<g clip-path="url(#frame)">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>
<g fill="{NEIGHBOUR_FILL}" stroke="{NEIGHBOUR_LINE}" stroke-width="{STROKE_NEIGHBOUR:.2f}" \
stroke-linejoin="round">{neighbours}</g>
<path d="{path_of(massachusetts, project)}" fill="{STATE_FILL}" stroke="{CONTOUR}" \
stroke-width="{STROKE_STATE:.2f}" stroke-linejoin="round"/>
{"".join(markers)}
</g>
</svg>
"""


if __name__ == "__main__":
    states = load_states()
    for site in SITES:
        target = ASSETS / f"{site['key']}_locus.svg"
        target.write_text(build(states, site["key"]), encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)")
