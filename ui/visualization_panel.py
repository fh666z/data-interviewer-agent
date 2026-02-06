from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import io


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

        # Hide the image label when showing dataframe
        self._image_label.pack_forget()

        # Create a frame for the table with scrollbars, anchored at top
        self._table_frame = tk.Frame(self)
        self._table_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4, anchor="nw")

        # Create a container frame for proper layout, anchored at top
        container = tk.Frame(self._table_frame)
        container.pack(fill=tk.BOTH, expand=True, anchor="nw")

        # Create Treeview widget for table display
        tree = ttk.Treeview(container, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for proper resizing
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=vsb.set)

        # Add horizontal scrollbar
        hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        tree.configure(xscrollcommand=hsb.set)

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
            info_label.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=2)

    def show_figure(self, fig: go.Figure) -> None:
        """Render a Plotly figure as an image and display it."""
        # Clear any existing table display
        if self._table_frame:
            self._table_frame.destroy()
            self._table_frame = None

        # Show the image label when showing figure
        self._image_label.pack(fill=tk.BOTH, expand=True)

        tmp_path = Path("_tmp_plot.png")
        pio.write_image(fig, tmp_path)
        image = Image.open(tmp_path)
        image = image.resize((self.winfo_width() or 800, self.winfo_height() or 600))
        photo = ImageTk.PhotoImage(image)
        self._current_photo = photo
        self._image_label.config(image=photo)

    def show_matplotlib_figure(self, fig: plt.Figure) -> None:
        """Render a matplotlib figure as an image and display it."""
        # Clear any existing table display
        if self._table_frame:
            self._table_frame.destroy()
            self._table_frame = None

        # Show the image label when showing figure
        self._image_label.pack(fill=tk.BOTH, expand=True)

        # Save matplotlib figure to a BytesIO buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Load and resize the image
        image = Image.open(buf)
        image = image.resize((self.winfo_width() or 800, self.winfo_height() or 600))
        photo = ImageTk.PhotoImage(image)
        self._current_photo = photo
        self._image_label.config(image=photo)
        
        # Close the figure to free memory
        plt.close(fig)
