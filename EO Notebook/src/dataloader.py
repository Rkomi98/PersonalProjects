"""PyTorch data loader for lazy EO tile access from Zarr + GeoParquet index."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import xarray as xr
from torch.utils.data import DataLoader, Dataset


class EOTileDataset(Dataset):
    """Lazy dataset that reads tiles on demand from a Zarr cube."""

    def __init__(
        self,
        tile_index_path: str | Path,
        zarr_path: str | Path,
        stats_path: str | Path | None = None,
        split: str | None = None,
        tile_size: int = 256,
        feature_name: str = "cube",
        bands: list[str] | None = None,
        dtype: torch.dtype = torch.float32,
    ) -> None:
        self.tile_index_path = Path(tile_index_path)
        self.zarr_path = Path(zarr_path)
        self.stats_path = Path(stats_path) if stats_path is not None else None
        self.split = split
        self.tile_size = tile_size
        self.feature_name = feature_name
        self.bands = bands
        self.dtype = dtype

        self.index = pd.read_parquet(self.tile_index_path)
        if self.split is not None:
            self.index = self.index[self.index["split"] == self.split].reset_index(drop=True)

        self._zarr: xr.Dataset | None = None
        self._mean: torch.Tensor | None = None
        self._std: torch.Tensor | None = None
        self._load_stats_if_available()

    def _load_stats_if_available(self) -> None:
        if self.stats_path is None or not self.stats_path.exists():
            return
        with self.stats_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        mean = payload.get("mean")
        std = payload.get("std")
        if mean is not None and std is not None:
            self._mean = torch.tensor(mean, dtype=self.dtype)[:, None, None]
            std_safe = [s if s > 1e-6 else 1.0 for s in std]
            self._std = torch.tensor(std_safe, dtype=self.dtype)[:, None, None]

    @property
    def zarr(self) -> xr.Dataset:
        # One lazy open per worker/process.
        if self._zarr is None:
            self._zarr = xr.open_zarr(self.zarr_path, consolidated=False)
        return self._zarr

    def __len__(self) -> int:
        return len(self.index)

    def _read_tile(self, row: pd.Series) -> np.ndarray:
        x0 = int(row["x0"])
        y0 = int(row["y0"])
        t0 = int(row.get("time_idx", 0))

        da = self.zarr[self.feature_name].isel(
            time=t0,
            y=slice(y0, y0 + self.tile_size),
            x=slice(x0, x0 + self.tile_size),
        )
        if self.bands is not None:
            da = da.sel(band=self.bands)
        return da.transpose("band", "y", "x").to_numpy()

    def __getitem__(self, idx: int) -> dict[str, Any]:
        row = self.index.iloc[idx]
        tile = torch.tensor(self._read_tile(row), dtype=self.dtype)

        if self._mean is not None and self._std is not None:
            tile = (tile - self._mean) / self._std

        sample: dict[str, Any] = {
            "image": tile,
            "tile_id": row.get("tile_id", idx),
            "split": row.get("split"),
        }
        if "label" in row and pd.notna(row["label"]):
            sample["label"] = int(row["label"])
        return sample


def make_dataloader(
    tile_index_path: str | Path,
    zarr_path: str | Path,
    stats_path: str | Path | None = None,
    split: str = "train",
    batch_size: int = 8,
    num_workers: int = 2,
    shuffle: bool = True,
    **dataset_kwargs: Any,
) -> DataLoader:
    """Construct a PyTorch DataLoader for EO tiles."""
    dataset = EOTileDataset(
        tile_index_path=tile_index_path,
        zarr_path=zarr_path,
        stats_path=stats_path,
        split=split,
        **dataset_kwargs,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle if split == "train" else False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=False,
    )
