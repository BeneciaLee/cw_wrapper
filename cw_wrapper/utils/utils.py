import random
import pickle as pk
import numpy as np
import matplotlib.pyplot as plt
from typing import Any


def visualization_single_trace(wave: np.ndarray,
                               show: bool = True,
                               linewidth: float = 0.8
                               ) -> plt.Figure:
    trace_img: plt.Figure = plt.figure(figsize=(8.0, 4.5))
    trace_ax: plt.Axes = trace_img.add_subplot(1, 1, 1)
    trace_ax.set_title(f"Power Consumption Trace")
    trace_ax.set_xlabel("Sample points")
    trace_ax.set_ylabel(f"Power Consumption")
    trace_ax.plot(wave, linewidth=linewidth)
    if show:
        trace_img.show()
    return trace_img


def make_random_hex(n_byte: int) -> str:
    result = []
    for _ in range(n_byte):
        result.append(format(random.randint(0, 0xff), "02X"))
    return ''.join(result)


def load_pickle_object(locate_and_name: str) -> Any:
    with open(locate_and_name, 'rb') as f:
        obj = pk.load(f)
    return obj


def store_pickle_object(target_object, locate_and_name: str) -> None:
    with open(locate_and_name, 'wb') as f:
        pk.dump(target_object, f)
    pass
