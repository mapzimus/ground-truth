# Ground Truth — Lidar Test Projects

Live site: **https://mapzimus.github.io/ground-truth/**

A series of lidar terrain-analysis test projects on real Massachusetts development
parcels. Each project takes free public lidar and turns it into the numbers that
decide a project — earthwork, buildable land, drainage, road access, clearing,
sightlines — with the same pipeline run on every site so results compare directly.

## Projects

| # | Page | Site | Question |
|---|------|------|----------|
| 01 | [devens.html](devens.html) | Devens, MA | Earthwork priced three ways on the pad where a real building went |
| 02 | [middleboro.html](middleboro.html) | Middleborough, MA | 150 wooded acres, a withdrawn warehouse, and what the land says |
| 03 | [hopkinton.html](hopkinton.html) | Hopkinton–Milford line, MA | Same warehouse, three pad positions, three price tags |
| 04 | [p04.html](p04.html) | I-495 corridor, 9 towns | 54 vacant parcels screened; 14 can hold a building |

## Data and methods

- **Lidar:** USGS 3DEP, 2021 Central-Eastern Massachusetts (published accuracy 10 cm RMSE)
- **Parcels, wetlands, streams:** MassGIS L3 tax parcels and DEP layers
- **Processing:** PDAL point-cloud pipeline → ground / treetop / canopy-height models;
  volumes by cell-wise raster math, cross-checked in QGIS
- All data public; scripts and pipeline files available on request

## Structure

Static site, no build step: one self-contained HTML file per page, images in
`assets/`. Deployed via GitHub Pages (`.nojekyll` disables Jekyll processing).

## Contact

Max Howe · MS, Geographic Information Science · mhowe.gis@gmail.com
