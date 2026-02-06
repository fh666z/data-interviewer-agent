from pathlib import Path
from typing import Optional

import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image, ImageTk
import tkinter as tk


class VisualizationPanel(tk.Frame):
    """Left panel responsible for displaying charts derived from the data."""

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._image_label = tk.Label(self)
        self._image_label.pack(fill=tk.BOTH, expand=True)
        self._current_photo: Optional[ImageTk.PhotoImage] = None

    def clear(self) -> None:
        self._image_label.config(image="")
        self._current_photo = None

    def show_figure(self, fig: go.Figure) -> None:
        """Render a Plotly figure as an image and display it."""
        tmp_path = Path("_tmp_plot.png")
        pio.write_image(fig, tmp_path)
        image = Image.open(tmp_path)
        image = image.resize((self.winfo_width() or 800, self.winfo_height() or 600))
        photo = ImageTk.PhotoImage(image)
        self._current_photo = photo
        self._image_label.config(image=photo)

