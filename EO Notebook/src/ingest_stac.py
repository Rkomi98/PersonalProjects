"""Utilities for STAC discovery and COG access for EO pipelines."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rioxarray as rxr
import yaml
from pyproj import Transformer
from rasterio.windows import from_bounds

try:
    from pystac_client import Client
except ImportError as exc:  # pragma: no cover
    raise ImportError("pystac-client is required to use STAC discovery.") from exc


PC_STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load YAML configuration from disk."""
    with Path(config_path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config: dict[str, Any], config_path: str | Path) -> None:
    """Save YAML configuration to disk."""
    with Path(config_path).open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)


def get_stac_client(provider: str) -> Client:
    """Return a STAC client from a short provider label."""
    provider_key = provider.lower()
    if provider_key in {"planetary-computer", "pc", "microsoft"}:
        try:
            import planetary_computer
        except ImportError:
            # Fallback: still return a usable client, but assets may require manual signing.
            return Client.open(PC_STAC_API_URL)
        return Client.open(PC_STAC_API_URL, modifier=planetary_computer.sign_inplace)
    if provider_key.startswith("http"):
        return Client.open(provider)
    raise ValueError(
        f"Unsupported provider '{provider}'. Use 'planetary-computer' or a STAC URL."
    )


def search_stac_items(config: dict[str, Any]) -> list[Any]:
    """Query STAC items for the configured AOI/date/cloud constraints."""
    stac_cfg = config["stac"]
    provider = stac_cfg["provider"]
    collections = stac_cfg["collections"]
    date_range = stac_cfg["date_range"]
    cloud_cfg = stac_cfg.get("cloud_cover", {})

    max_cloud = cloud_cfg.get("max", 25)
    cloud_field = cloud_cfg.get("field", "eo:cloud_cover")

    client = get_stac_client(provider)
    search = client.search(
        collections=collections,
        intersects=config["aoi"]["geometry"],
        datetime=f"{date_range['start']}/{date_range['end']}",
        query={cloud_field: {"lt": max_cloud}},
    )
    items = list(search.items())
    return items


def items_to_frame(items: Iterable[Any]) -> pd.DataFrame:
    """Convert STAC items into a tabular summary for QA/debug."""
    records = []
    for item in items:
        props = item.properties
        records.append(
            {
                "id": item.id,
                "collection": item.collection_id,
                "datetime": props.get("datetime"),
                "cloud_cover": props.get("eo:cloud_cover"),
                "epsg": props.get("proj:epsg"),
                "bbox": item.bbox,
            }
        )
    frame = pd.DataFrame(records)
    if not frame.empty and "datetime" in frame.columns:
        frame["datetime"] = pd.to_datetime(frame["datetime"], utc=True, errors="coerce")
    return frame.sort_values("datetime").reset_index(drop=True)


def _sign_href_for_provider(href: str, provider: str) -> str:
    """Sign cloud assets when required by provider."""
    provider_key = provider.lower()
    if provider_key in {"planetary-computer", "pc", "microsoft"}:
        try:
            import planetary_computer
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "planetary-computer is required for signed Planetary Computer assets."
            ) from exc
        return planetary_computer.sign(href)
    return href


def get_asset_href(item: Any, asset_key: str, provider: str) -> str:
    """Get (and sign, if required) an asset URL from an item."""
    if asset_key not in item.assets:
        raise KeyError(f"Asset '{asset_key}' not found in item '{item.id}'.")
    return _sign_href_for_provider(item.assets[asset_key].href, provider)


def open_cog_with_rioxarray(
    asset_href: str,
    chunks: dict[str, int] | None = None,
):
    """Open a COG as an xarray DataArray."""
    return rxr.open_rasterio(asset_href, masked=True, chunks=chunks)


def read_cog_window(
    asset_href: str,
    bounds: tuple[float, float, float, float],
    bounds_crs: str = "EPSG:4326",
    band: int = 1,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Read a bounded window from a COG.

    This is useful to demonstrate HTTP range request access patterns with COGs.
    """
    with rasterio.open(asset_href) as src:
        target_bounds = bounds
        if str(src.crs) != bounds_crs:
            transformer = Transformer.from_crs(bounds_crs, src.crs, always_xy=True)
            minx, miny = transformer.transform(bounds[0], bounds[1])
            maxx, maxy = transformer.transform(bounds[2], bounds[3])
            target_bounds = (minx, miny, maxx, maxy)

        window = from_bounds(*target_bounds, transform=src.transform)
        array = src.read(band, window=window)
        window_transform = src.window_transform(window)

        profile = {
            "crs": src.crs.to_string() if src.crs else None,
            "dtype": str(array.dtype),
            "shape": array.shape,
            "nodata": src.nodata,
            "transform": tuple(window_transform),
        }
    return array, profile


def to_geodataframe(config: dict[str, Any]) -> gpd.GeoDataFrame:
    """Build a GeoDataFrame from the configured AOI geometry."""
    return gpd.GeoDataFrame.from_features(
        [{"type": "Feature", "geometry": config["aoi"]["geometry"], "properties": {}}],
        crs="EPSG:4326",
    )
