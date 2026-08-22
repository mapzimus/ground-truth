# Data sources and credits

Source pages were reviewed on **August 18, 2026**. Exact file versions and download dates vary by case. A new engagement should refresh and record them before analysis.

## Elevation and lidar

- [USGS 3D Elevation Program](https://www.usgs.gov/3d-elevation-program)
- [MassGIS Lidar Terrain Data](https://www.mass.gov/info-details/massgis-data-lidar-terrain-data)

The detailed case studies use the spring 2021 Central-Eastern Massachusetts lidar acquisition. MassGIS describes it as Quality Level 1 and distributes 0.5-meter terrain products. USGS 3DEP products are public data; their source metadata still needs to travel with any analysis.

The I-495 corridor page displays MassGIS's public [2021 lidar shaded-relief tiles](https://www.mass.gov/info-details/massgis-data-lidar-terrain-data) generated from that half-meter bare-earth DEM, with MassGIS Level 3 parcel outlines for all 54 screened sites.

## Parcels and assessor records

- [MassGIS Property Tax Parcels](https://www.mass.gov/info-details/massgis-data-property-tax-parcels)

Level 3 parcels and assessor extracts support the corridor screen. They are administrative mapping records, not surveyed property boundaries or title evidence. Assessor data has a fiscal-year vintage that should be recorded when the screen is refreshed.

## Wetlands and hydrography

- [MassDEP Wetlands (2005), distributed by MassGIS](https://www.mass.gov/info-details/massgis-data-massdep-wetlands-2005)
- [MassDEP Hydrography (1:25,000)](https://www.mass.gov/info-details/massgis-data-massdep-hydrography-125000)

These layers are planning screens. MassDEP states that its mapped wetland boundaries are not Wetlands Protection Act delineations. Lidar Site Studies therefore describes buffers as **mapped-buffer screens**, never field-confirmed wetland limits.

## Imagery

- [Esri World Imagery service item and current provider credits](https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9)

Selected context figures use Esri World Imagery. Providers vary by location and scale. The imagery is shown for orientation and visual context; it is not the source of the bare-earth terrain quantities in the demonstrations.

## State boundaries

- [US Census Bureau cartographic boundary files, 1:5,000,000 states](https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_us_state_5m.zip)

The study-page locus maps are drawn from the 2022 Census state boundaries by `scripts/build-locus-maps.py`. They are orientation graphics: generalized outlines at roughly 750 m per pixel, with site markers placed at town scale.

## Road centerlines

- [OpenStreetMap](https://www.openstreetmap.org/copyright) — I-495 mainline centerline on the corridor map, © OpenStreetMap contributors, licensed [ODbL](https://opendatacommons.org/licenses/odbl/). Drawn for orientation only; it is not a right-of-way, easement, or survey boundary.

## Reference figures

- Interstate 495 length in Massachusetts, 121.56 miles (195.63 km), used only to scale the corridor screen's candidate rate on the corridor page. See [Interstate 495 (Massachusetts)](https://en.wikipedia.org/wiki/Interstate_495_(Massachusetts)) and [AARoads](https://www.aaroads.com/guides/i-495-ma). The extrapolation built on it is arithmetic from one studied stretch, not a statewide survey, and the corridor page says so.

## Operating and professional references

- [FAA Part 107 overview](https://www.faa.gov/newsroom/small-unmanned-aircraft-systems-uas-regulations-part-107)
- [FAA Part 107 airspace authorizations](https://www.faa.gov/uas/commercial_operators/part_107_airspace_authorizations)
- [Massachusetts statutes and regulations for engineers and land surveyors](https://www.mass.gov/lists/statutes-and-regulations-for-engineers-and-land-surveyors)

These links are provided to make the operating boundary visible. The governing rules and licensing board—not this repository—determine what a particular commercial scope requires.
