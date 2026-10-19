# https://github.com/Comfy-Org/ComfyUI/blob/v0.42.0/comfy_extras/nodes_slg.py (SkipLayerGuidanceDiTSimple)

import re
from typing import Callable

import torch

from backend.patcher.base import set_model_options_patch_replace

UNCOND = 1


def parse_layers(text: str | None) -> list[int]:
    return [int(i) for i in re.findall(r"\d+", text or "")]


def _skip_uncond(args: dict, extra_args: dict) -> dict:
    """skip the block for the uncond rows only, since Forge runs cond and uncond in the same batch"""
    img = args["img"]
    cond_or_uncond = args["transformer_options"].get("cond_or_uncond", [])

    if UNCOND not in cond_or_uncond:
        return extra_args["original_block"](args)

    rows = img.shape[0] // len(cond_or_uncond)
    keep = [i * rows + r for i, c in enumerate(cond_or_uncond) if c != UNCOND for r in range(rows)]

    if not keep:
        return {"img": img}

    index = torch.tensor(keep, device=img.device)
    batched = lambda t: t.index_select(0, index) if isinstance(t, torch.Tensor) and t.shape[0] == img.shape[0] else t

    sub_args = args.copy()
    sub_args["img"] = img.index_select(0, index)
    sub_args["mod"] = tuple(batched(m) for m in args["mod"])
    sub_args["vec"] = batched(args.get("vec"))

    out = extra_args["original_block"](sub_args)["img"]
    return {"img": img.index_copy(0, index, out)}


def skip_uncond_layers(layers: list[int] | Callable[[], list[int]]) -> Callable:
    """conditioning modifier that skips the given single blocks in the negative branch"""

    def modifier(model, x, timestep, uncond, cond, cond_scale, model_options, seed):
        _layers = layers() if callable(layers) else layers

        if uncond is not None and _layers:
            model_options = model_options.copy()
            for layer in _layers:
                model_options = set_model_options_patch_replace(model_options, _skip_uncond, "dit", "single_block", layer)

        return model, x, timestep, uncond, cond, cond_scale, model_options, seed

    return modifier
