from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk


class VisualizationPanel(tk.Frame):
    """Left panel responsible for displaying charts derived from the data."""

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._image_label = tk.Label(self)
        self._image_label.pack(fill=tk.BOTH, expand=True)
        self._current_photo: Optional[ImageTk.PhotoImage] = None
        self._table_frame: Optional[tk.Frame] = None

    def clear(self) -> None:
        """Clear the current display."""
        self._image_label.config(image="")
        self._current_photo = None
        if self._table_frame:
            self._table_frame.destroy()
            self._table_frame = None

    def show_dataframe(self, df: pd.DataFrame) -> None:
        """Display a DataFrame as a table in the panel."""
        # Clear any existing display
        self.clear()

        # Create a frame for the table with scrollbars
        self._table_frame = tk.Frame(self)
        self._table_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Create Treeview widget for table display
        tree = ttk.Treeview(self._table_frame, show="headings")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbars
        vsb = ttk.Scrollbar(self._table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(self._table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure columns
        columns = list(df.columns)
        tree["columns"] = columns
        tree["show"] = "headings"

        # Set column headings and widths
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.W)

        # Insert data (limit to first 1000 rows for performance)
        max_rows = min(1000, len(df))
        for i in range(max_rows):
            values = [str(df.iloc[i][col]) for col in columns]
            tree.insert("", tk.END, values=values)

        # Show message if data was truncated
        if len(df) > max_rows:
            info_label = tk.Label(
                self._table_frame,
                text=f"Showing first {max_rows} of {len(df)} rows",
                font=("Arial", 9),
            )
            info_label.pack(side=tk.BOTTOM, fill=tk.X)

    def show_figure(self, fig: go.Figure) -> None:
        """Render a Plotly figure as an image and display it."""
        # Clear any existing table display
        if self._table_frame:
            self._table_frame.destroy()
            self._table_frame = None

        tmp_path = Path("_tmp_plot.png")
        pio.write_image(fig, tmp_path)
        image = Image.open(tmp_path)
        image = image.resize((self.winfo_width() or 800, self.winfo_height() or 600))
        photo = ImageTk.PhotoImage(image)
        self._current_photo = photo
        self._image_label.config(image=photo)

