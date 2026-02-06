import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Optional

import pandas as pd

from agent.dataframe_agent import create_dataframe_agent, run_query
from ui.query_panel import QueryPanel
from ui.visualization_panel import VisualizationPanel
from utils.csv_loader import load_csv


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Data Interviewer Agent")
        self.geometry("1200x800")

        self._df: Optional[pd.DataFrame] = None
        self._agent = None

        self._create_menu()
        self._create_layout()

    def _create_menu(self) -> None:
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open CSV", command=self._open_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def _create_layout(self) -> None:
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        self._viz_panel = VisualizationPanel(paned, borderwidth=1, relief=tk.SUNKEN)
        self._query_panel = QueryPanel(paned, on_submit=self._on_query)

        paned.add(self._viz_panel, weight=1)
        paned.add(self._query_panel, weight=1)

    def _open_csv(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            df = load_csv(Path(file_path))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error loading CSV", str(exc))
            return
        self._df = df
        try:
            self._agent = create_dataframe_agent(df)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error creating agent", str(exc))
            self._agent = None
            return
        messagebox.showinfo("CSV Loaded", f"Loaded {len(df)} rows from {file_path}")

    def _on_query(self, query: str) -> None:
        if self._agent is None:
            self._query_panel.set_status("Please open a CSV file first.")
            return
        try:
            result = run_query(self._agent, query)
        except Exception as exc:  # noqa: BLE001
            self._query_panel.set_status("Error running query.")
            messagebox.showerror("Query Error", str(exc))
            return

        text = result.get("text", "")
        self._query_panel.append_response(text)
        self._query_panel.set_status("Done.")


def run_ui() -> None:
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    run_ui()

