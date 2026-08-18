# Methodology and interpretation guide

This document records the shared logic behind the Lidar Site Studies demonstrations. The [public methodology page](https://mapzimus.github.io/ground-truth/methodology.html) is the most readable version for a client or collaborator.

## Purpose

The workflow is an early decision screen. It is intended to:

- compare sites or concepts consistently;
- expose terrain questions hidden by vegetation;
- identify whether public data is current enough;
- prepare a focused list for field and professional diligence.

It does not establish boundary, title, legal access, wetland jurisdiction, zoning compliance, soil conditions, permit eligibility, or final design quantities.

## Shared workflow

1. Define the parcel, target use, conceptual pad, and decision question.
2. review source dates, metadata, coordinate reference systems, coverage, and published accuracy;
3. generate or use bare-earth and above-ground elevation surfaces;
4. derive slope, flow, roughness, canopy, and related screening layers as needed;
5. combine terrain with mapped parcels, wetlands, hydrography, and stated buffers;
6. search conceptual pad positions and calculate raster cut/fill to a level balance grade;
7. compare critical calculations against a second implementation or published derivative;
8. document the questions that still require fieldwork or a licensed professional.

## Quantities and costs

Earthwork values are cell-by-cell raster calculations for conceptual level pads. They are not grading plans. Unless expressly stated, they omit shrink/swell, stripping, unsuitable material, rock, dewatering, haul/disposal, access grading, drainage, utilities, pavement, structures, mobilization, escalation, overhead, and profit.

The demonstrations use **$20 per cubic yard as an illustrative comparison assumption**, with a $10–$40 sensitivity range in some studies. It is not a current quote, estimate, or bid.

The ±10 cm tests are **data-sensitivity checks**. They show how a uniform elevation shift affects the model; they are not construction contingencies.

## Accuracy language

Comparing a processed ground model with a state DEM made from the same lidar flight checks processing consistency. It does not independently verify absolute field accuracy. Work that will support surveying, design, or construction decisions requires a project-specific scope, appropriate control, and licensed-professional involvement where applicable.

## Reproducibility

The case pages state their point counts, surface resolution, comparison results, screen thresholds, and buffer assumptions. Processing scripts are not included in this presentation repository, but can be discussed with the author. A client delivery should also include an input inventory, exact source versions, processing record, assumptions, and dated limitation memo.
