#!/usr/bin/env python3
"""Fetch MassGIS L3 polygons for the P04 shortlist and crop 2021 lidar hillshade."""

from __future__ import annotations

import io
import json
import math
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

PARCEL_QUERY = (
    "https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/"
    "Massachusetts_Property_Tax_Parcels/FeatureServer/0/query"
)
HILLSHADE_TILE = (
    "https://tiles.arcgis.com/tiles/hGdibHYSPO59RG1h/arcgis/rest/services/"
    "LiDAR_ShadedRelief_18Nant_21EC/MapServer/tile/{z}/{y}/{x}"
)
UA = "LidarSiteStudies/1.0 (https://maxwellhowegis.com/lidar-test/; mhowe.gis@gmail.com)"

SHORTLIST = [
    {"rank": 1, "label": "West Central St", "town": "Franklin", "acres": 87.1, "pad_ac": 7.4, "yd3": 31047, "psf": 1.94, "cost_m": 0.62, "loc_id": "M_204691_871172"},
    {"rank": 2, "label": "23 R Tulip Way", "town": "Medway", "acres": 24.7, "pad_ac": 7.4, "yd3": 35803, "psf": 2.24, "cost_m": 0.72, "loc_id": "M_203505_876162"},
    {"rank": 3, "label": "High St", "town": "Bellingham", "acres": 33.7, "pad_ac": 7.4, "yd3": 50468, "psf": 3.16, "cost_m": 1.01, "loc_id": "F_665652_2859365"},
    {"rank": 4, "label": "Hartford Ave", "town": "Bellingham", "acres": 20.8, "pad_ac": 7.4, "yd3": 57217, "psf": 3.58, "cost_m": 1.14, "loc_id": "F_663068_2865769"},
    {"rank": 5, "label": "4 Technology Dr", "town": "Milford", "acres": 18.5, "pad_ac": 7.4, "yd3": 61756, "psf": 3.86, "cost_m": 1.24, "loc_id": "F_661108_2872867"},
    {"rank": 6, "label": "High St", "town": "Bellingham", "acres": 47.8, "pad_ac": 16.3, "yd3": 144167, "psf": 4.06, "cost_m": 2.88, "loc_id": "F_665869_2861822"},
    {"rank": 7, "label": "Hixon St", "town": "Bellingham", "acres": 32.1, "pad_ac": 7.4, "yd3": 67733, "psf": 4.24, "cost_m": 1.35, "loc_id": "F_661803_2869494"},
    {"rank": 8, "label": "Maple St", "town": "Milford", "acres": 12.5, "pad_ac": 7.4, "yd3": 81825, "psf": 5.12, "cost_m": 1.64, "loc_id": "F_660279_2873847"},
    {"rank": 9, "label": "East Main St", "town": "Milford", "acres": 119.2, "pad_ac": 7.4, "yd3": 93991, "psf": 5.88, "cost_m": 1.88, "loc_id": "F_659179_2884652"},
    {"rank": 10, "label": "Pine Island Road", "town": "Hopkinton", "acres": 110.2, "pad_ac": 16.3, "yd3": 233019, "psf": 6.56, "cost_m": 4.66, "loc_id": "F_642689_2894382"},
    {"rank": 11, "label": "Farm St", "town": "Bellingham", "acres": 16.3, "pad_ac": 7.4, "yd3": 110234, "psf": 6.90, "cost_m": 2.20, "loc_id": "F_668365_2873635"},
    {"rank": 12, "label": "Lumber Street", "town": "Hopkinton", "acres": 16.5, "pad_ac": 7.4, "yd3": 129444, "psf": 8.10, "cost_m": 2.59, "loc_id": "F_648742_2897904"},
    {"rank": 13, "label": "306 Maple St", "town": "Bellingham", "acres": 11.5, "pad_ac": 7.4, "yd3": 141798, "psf": 8.87, "cost_m": 2.84, "loc_id": "F_669974_2861180"},
    {"rank": 14, "label": "Fisher St", "town": "Holliston", "acres": 17.3, "pad_ac": 7.4, "yd3": 175079, "psf": 10.95, "cost_m": 3.50, "loc_id": "M_202617_878687"},
]

FAILED = [
    {"id": "fail-01", "label": "Off Lumber Street", "town": "Hopkinton", "acres": 11.7, "constrained": 50, "loc_id": "F_649041_2895731"},
    {"id": "fail-02", "label": "0 Lumber Street", "town": "Hopkinton", "acres": 20.4, "constrained": 76, "loc_id": "F_649502_2894587"},
    {"id": "fail-03", "label": "253 Lumber Street", "town": "Hopkinton", "acres": 14.3, "constrained": 71, "loc_id": "F_650439_2894503"},
    {"id": "fail-04", "label": "0 Granite Street", "town": "Hopkinton", "acres": 29.3, "constrained": 71, "loc_id": "F_651014_2895063"},
    {"id": "fail-05", "label": "0 South St", "town": "Holliston", "acres": 10.4, "constrained": 38, "loc_id": "M_201898_878945"},
    {"id": "fail-06", "label": "Rear Purchase St", "town": "Milford", "acres": 12.6, "constrained": 86, "loc_id": "F_645667_2888042"},
    {"id": "fail-07", "label": "Silver Hill Rd", "town": "Milford", "acres": 34.6, "constrained": 85, "loc_id": "F_646041_2887686"},
    {"id": "fail-08", "label": "Rear Haven St", "town": "Milford", "acres": 15.3, "constrained": 44, "loc_id": "F_651445_2893313"},
    {"id": "fail-09", "label": "400 Deer St", "town": "Milford", "acres": 25.0, "constrained": 57, "loc_id": "F_651469_2889092"},
    {"id": "fail-10", "label": "10 Country Way", "town": "Hopkinton", "acres": 10.4, "constrained": 52, "loc_id": "F_640282_2902892"},
    {"id": "fail-11", "label": "80 Deer St", "town": "Milford", "acres": 13.3, "constrained": 99, "loc_id": "F_653127_2887105", "image": "p04_lidar_fail_deer.jpg"},
    {"id": "fail-12", "label": "Rear Cedar St", "town": "Milford", "acres": 11.5, "constrained": 84, "loc_id": "F_654195_2893373"},
    {"id": "fail-13", "label": "Rear Cedar St", "town": "Milford", "acres": 10.4, "constrained": 24, "loc_id": "F_656153_2885604"},
    {"id": "fail-14", "label": "I-495 remnant", "town": "Milford", "acres": 18.5, "constrained": 100, "loc_id": "F_657021_2885160", "image": "p04_lidar_fail_i495.jpg"},
    {"id": "fail-15", "label": "Maple St", "town": "Milford", "acres": 24.0, "constrained": 74, "loc_id": "F_660258_2875097"},
    {"id": "fail-16", "label": "Off Medway Rd", "town": "Milford", "acres": 12.3, "constrained": 100, "loc_id": "F_661497_2878188"},
    {"id": "fail-17", "label": "0 Hartford Av", "town": "Bellingham", "acres": 24.1, "constrained": 64, "loc_id": "F_659776_2865936"},
    {"id": "fail-18", "label": "Downey Street", "town": "Hopkinton", "acres": 11.9, "constrained": 27, "loc_id": "F_641850_2900713"},
    {"id": "fail-19", "label": "0 Hartford Av", "town": "Bellingham", "acres": 44.5, "constrained": 72, "loc_id": "F_663644_2864200"},
    {"id": "fail-20", "label": "187 Farm St", "town": "Bellingham", "acres": 11.9, "constrained": 95, "loc_id": "F_664328_2871891"},
    {"id": "fail-21", "label": "0 North Main St", "town": "Bellingham", "acres": 31.6, "constrained": 90, "loc_id": "F_664657_2862986"},
    {"id": "fail-22", "label": "0 Maple St", "town": "Bellingham", "acres": 106.1, "constrained": 69, "loc_id": "F_665067_2862387"},
    {"id": "fail-23", "label": "0 Maple St", "town": "Bellingham", "acres": 10.2, "constrained": 35, "loc_id": "F_669646_2858085"},
    {"id": "fail-24", "label": "0 Oak St", "town": "Bellingham", "acres": 12.1, "constrained": 46, "loc_id": "F_670911_2866211"},
    {"id": "fail-25", "label": "36 R Alder St", "town": "Medway", "acres": 35.6, "constrained": 100, "loc_id": "M_201944_876835", "image": "p04_lidar_fail_alder.jpg"},
    {"id": "fail-26", "label": "0 Oak Grove", "town": "Medway", "acres": 13.0, "constrained": 44, "loc_id": "M_202070_877231"},
    {"id": "fail-27", "label": "26 Alder St", "town": "Medway", "acres": 11.3, "constrained": 82, "loc_id": "M_202200_876756"},
    {"id": "fail-28", "label": "0 R Stone End Rd", "town": "Medway", "acres": 25.3, "constrained": 84, "loc_id": "M_202369_878100"},
    {"id": "fail-29", "label": "0 Mine Brook", "town": "Franklin", "acres": 15.0, "constrained": 51, "loc_id": "M_204523_872293"},
    {"id": "fail-30", "label": "0 Mine Brook", "town": "Franklin", "acres": 23.0, "constrained": 64, "loc_id": "M_204785_872082"},
    {"id": "fail-31", "label": "0 Old Town Road", "town": "Hopkinton", "acres": 13.2, "constrained": 61, "loc_id": "F_642923_2896824"},
    {"id": "fail-32", "label": "300 Fisher St", "town": "Franklin", "acres": 18.3, "constrained": 82, "loc_id": "M_207397_869446"},
    {"id": "fail-33", "label": "0 King St", "town": "Franklin", "acres": 24.4, "constrained": 51, "loc_id": "M_207604_868174"},
    {"id": "fail-34", "label": "555 King St", "town": "Franklin", "acres": 12.6, "constrained": 55, "loc_id": "M_207925_868195"},
    {"id": "fail-35", "label": "0 Summer St", "town": "Franklin", "acres": 10.4, "constrained": 33, "loc_id": "M_209971_869018"},
    {"id": "fail-36", "label": "0 Uncas Pond", "town": "Franklin", "acres": 15.6, "constrained": 14, "loc_id": "M_210148_868642", "image": "p04_lidar_fail_uncas.jpg"},
    {"id": "fail-37", "label": "0 Lumber Street", "town": "Hopkinton", "acres": 27.8, "constrained": 74, "loc_id": "F_645921_2903103"},
    {"id": "fail-38", "label": "0 Lumber Street", "town": "Hopkinton", "acres": 27.5, "constrained": 73, "loc_id": "F_645642_2901891"},
    {"id": "fail-39", "label": "0 West Main Street", "town": "Hopkinton", "acres": 10.1, "constrained": 62, "loc_id": "F_646735_2904666"},
    {"id": "fail-40", "label": "Off Teresa Road", "town": "Hopkinton", "acres": 40.3, "constrained": 81, "loc_id": "F_647385_2900853"},
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def lonlat_to_tile(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    n = 2 ** zoom
    x = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def ring_bounds(coords: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in coords]
    ys = [point[1] for point in coords]
    return min(xs), min(ys), max(xs), max(ys)


def geometry_bounds(geom: dict) -> tuple[float, float, float, float]:
    rings = []
    if geom["type"] == "Polygon":
        rings = geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        rings = [ring for polygon in geom["coordinates"] for ring in polygon]
    bounds = [ring_bounds(ring) for ring in rings]
    return (
        min(item[0] for item in bounds),
        min(item[1] for item in bounds),
        max(item[2] for item in bounds),
        max(item[3] for item in bounds),
    )


def pad_bounds(bounds: tuple[float, float, float, float], factor: float) -> tuple[float, float, float, float]:
    minx, miny, maxx, maxy = bounds
    dx = (maxx - minx) * factor
    dy = (maxy - miny) * factor
    return minx - dx, miny - dy, maxx + dx, maxy + dy


def mosaic_hillshade(bounds: tuple[float, float, float, float], zoom: int) -> tuple[Image.Image, tuple[float, float, float, float]]:
    minx, miny, maxx, maxy = bounds
    x0, y_north = lonlat_to_tile(minx, maxy, zoom)
    x1, y_south = lonlat_to_tile(maxx, miny, zoom)
    tile_x0, tile_y0 = math.floor(x0), math.floor(y_north)
    tile_x1, tile_y1 = math.ceil(x1) - 1, math.ceil(y_south) - 1
    if tile_x1 < tile_x0 or tile_y1 < tile_y0:
        raise ValueError(f"empty tile window: x {tile_x0}:{tile_x1} y {tile_y0}:{tile_y1}")
    width = (tile_x1 - tile_x0 + 1) * 256
    height = (tile_y1 - tile_y0 + 1) * 256
    canvas = Image.new("RGB", (width, height), (18, 19, 15))
    urls = []
    for ty in range(tile_y0, tile_y1 + 1):
        for tx in range(tile_x0, tile_x1 + 1):
            urls.append((tx, ty, HILLSHADE_TILE.format(z=zoom, y=ty, x=tx)))

    def load_tile(item):
        tx, ty, url = item
        try:
            image = Image.open(io.BytesIO(fetch_bytes(url))).convert("RGB")
        except Exception:
            image = Image.new("RGB", (256, 256), (18, 19, 15))
        return tx, ty, image

    with ThreadPoolExecutor(max_workers=12) as pool:
        for tx, ty, image in pool.map(load_tile, urls):
            canvas.paste(image, ((tx - tile_x0) * 256, (ty - tile_y0) * 256))

    left = int(round((x0 - tile_x0) * 256))
    top = int(round((y_north - tile_y0) * 256))
    right = int(round((x1 - tile_x0) * 256))
    bottom = int(round((y_south - tile_y0) * 256))
    crop = canvas.crop((left, top, max(left + 8, right), max(top + 8, bottom)))
    return crop, (x0, y_north, x1, y_south)


def project_ring(ring: list[list[float]], zoom: int, window: tuple[float, float, float, float], size: tuple[int, int]) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = window
    width, height = size
    points = []
    for lon, lat in ring:
        x, y = lonlat_to_tile(lon, lat, zoom)
        px = int(round((x - x0) / (x1 - x0) * width))
        py = int(round((y - y0) / (y1 - y0) * height))
        points.append((px, py))
    return points


def draw_parcel(image: Image.Image, geom: dict, zoom: int, window: tuple[float, float, float, float], fill: tuple[int, int, int, int], outline: tuple[int, int, int, int]) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rings = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [polygon[0] for polygon in geom["coordinates"]]
    for ring in rings:
        pts = project_ring(ring, zoom, window, image.size)
        if len(pts) >= 3:
            draw.polygon(pts, fill=fill, outline=outline)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def fetch_by_loc_ids(ids: list[str]) -> dict:
    loc_ids = "', '".join(ids)
    params = {
        "where": f"LOC_ID IN ('{loc_ids}')",
        "outFields": "LOC_ID,SITE_ADDR,CITY,LOT_SIZE,LOT_UNITS,USE_CODE,BLDG_VAL,PROP_ID",
        "outSR": "4326",
        "f": "geojson",
        "geometryPrecision": "5",
        "maxAllowableOffset": "0.00002",
    }
    data = fetch_json(PARCEL_QUERY + "?" + urllib.parse.urlencode(params))
    missing = [loc for loc in ids if loc not in {feature["properties"]["LOC_ID"] for feature in data["features"]}]
    if missing:
        raise SystemExit(f"missing parcels: {missing}")
    return {feature["properties"]["LOC_ID"]: feature for feature in data["features"]}


def fetch_parcels() -> dict:
    by_id = fetch_by_loc_ids([item["loc_id"] for item in SHORTLIST + FAILED])
    features = []
    for item in SHORTLIST:
        src = by_id[item["loc_id"]]
        features.append({
            "type": "Feature",
            "properties": {
                "id": f"pass-{item['rank']:02d}",
                "passed": True,
                **item,
                "site_addr": src["properties"]["SITE_ADDR"],
                "assess_acres": src["properties"]["LOT_SIZE"],
                "use_code": src["properties"]["USE_CODE"],
            },
            "geometry": src["geometry"],
        })
    for item in FAILED:
        src = by_id[item["loc_id"]]
        props = {key: value for key, value in item.items() if key != "image"}
        features.append({
            "type": "Feature",
            "properties": {
                "passed": False,
                "rank": None,
                **props,
                "site_addr": src["properties"]["SITE_ADDR"],
                "assess_acres": src["properties"]["LOT_SIZE"],
                "use_code": src["properties"]["USE_CODE"],
            },
            "geometry": src["geometry"],
        })
    return {"type": "FeatureCollection", "features": features}


def save_jpeg(image: Image.Image, path: Path, size: tuple[int, int]) -> None:
    fitted = image.copy()
    fitted.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (18, 19, 15))
    canvas.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    canvas.save(path, "JPEG", quality=82, optimize=True, progressive=True)


def crop_site(feature: dict, fill: tuple[int, int, int, int], outline: tuple[int, int, int, int], path: Path) -> None:
    bounds = pad_bounds(geometry_bounds(feature["geometry"]), 0.45)
    zoom = 16 if (bounds[2] - bounds[0]) < 0.012 else 15
    image, window = mosaic_hillshade(bounds, zoom)
    image = draw_parcel(image, feature["geometry"], zoom, window, fill, outline)
    save_jpeg(image, path, (1200, 960))
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    collection = fetch_parcels()
    geo_path = DATA / "p04-parcels.geojson"
    geo_path.write_text(json.dumps(collection, separators=(",", ":")))
    print(f"wrote {geo_path} ({geo_path.stat().st_size} bytes, {len(collection['features'])} parcels)")

    by_loc = {feature["properties"]["loc_id"]: feature for feature in collection["features"]}
    passed_fill, passed_line = (90, 168, 92, 70), (255, 180, 0, 230)
    failed_fill, failed_line = (166, 106, 58, 90), (196, 140, 80, 230)

    for feature in collection["features"]:
        props = feature["properties"]
        if props.get("passed") and props.get("rank") and props["rank"] <= 5:
            crop_site(feature, passed_fill, passed_line, ASSETS / f"p04_lidar_{props['rank']:02d}.jpg")

    for item in FAILED:
        if "image" not in item:
            continue
        crop_site(by_loc[item["loc_id"]], failed_fill, failed_line, ASSETS / item["image"])

    corridor_bounds = None
    for feature in collection["features"]:
        bounds = geometry_bounds(feature["geometry"])
        if corridor_bounds is None:
            corridor_bounds = bounds
        else:
            corridor_bounds = (
                min(corridor_bounds[0], bounds[0]),
                min(corridor_bounds[1], bounds[1]),
                max(corridor_bounds[2], bounds[2]),
                max(corridor_bounds[3], bounds[3]),
            )
    assert corridor_bounds is not None
    corridor_bounds = pad_bounds(corridor_bounds, 0.12)
    image, window = mosaic_hillshade(corridor_bounds, 13)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for feature in collection["features"]:
        geom = feature["geometry"]
        rings = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [polygon[0] for polygon in geom["coordinates"]]
        passed = feature["properties"]["passed"]
        fill = passed_fill if passed else failed_fill
        outline = passed_line if passed else failed_line
        for ring in rings:
            pts = project_ring(ring, 13, window, image.size)
            if len(pts) >= 3:
                draw.polygon(pts, fill=fill, outline=outline)
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    out = ASSETS / "p04_lidar_corridor.jpg"
    save_jpeg(image, out, (1400, 980))
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
