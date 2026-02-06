import re
import threading
import tkinter as tk
from pathlib import Path
from typing import Any, Dict, Optional
from tkinter import filedialog, messagebox, ttk

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        
        # Display the DataFrame contents in the visualization panel
        self._viz_panel.show_dataframe(df)
        
        messagebox.showinfo("CSV Loaded", f"Loaded {len(df)} rows from {file_path}")

    def _on_query(self, query: str) -> None:
        if self._agent is None:
            self._query_panel.set_status("Please open a CSV file first.")
            return
        
        # Disable the send button to prevent multiple queries
        self._query_panel.set_send_enabled(False)
        
        # Run the query in a background thread
        thread = threading.Thread(
            target=self._run_query_thread,
            args=(query,),
            daemon=True
        )
        thread.start()

    def _run_query_thread(self, query: str) -> None:
        """Run the query in a background thread and schedule UI updates."""
        try:
            result = run_query(self._agent, query)
            # Schedule UI update on the main thread
            self.after(0, self._handle_query_result, result)
        except Exception as exc:  # noqa: BLE001
            # Schedule error handling on the main thread
            self.after(0, self._handle_query_error, exc)

    def _handle_query_result(self, result: Dict[str, Any]) -> None:
        """Handle query result on the main thread."""
        # Show intermediate reasoning steps (if any), then the final answer,
        # all formatted as Agent messages in the conversation view.
        steps = result.get("steps") or []
        if steps:
            for step in steps:
                self._query_panel.append_response(f"Agent: {step}")

        text = result.get("text", "") or ""
        if text:
            self._query_panel.append_response(f"Agent: {text}")
            # Try to extract and execute any plotting code returned by the agent.
            self._maybe_run_plot_code(text)

        # Add a blank line to visually separate conversation turns.
        self._query_panel.append_response("")
        self._query_panel.set_status("Done.")
        # Re-enable the send button
        self._query_panel.set_send_enabled(True)

    def _handle_query_error(self, exc: Exception) -> None:
        """Handle query error on the main thread."""
        self._query_panel.set_status("Error running query.")
        messagebox.showerror("Query Error", str(exc))
        # Re-enable the send button
        self._query_panel.set_send_enabled(True)

    def _extract_python_code(self, text: str) -> Optional[str]:
        """Extract the first Python code block (```python ... ```) from text."""
        match = re.search(r"```python(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if not match:
            return None
        return match.group(1).strip()

    def _maybe_run_plot_code(self, text: str) -> None:
        """If the agent returned plotting code, execute it and show the figure."""
        if self._df is None:
            return

        code = self._extract_python_code(text)
        if not code:
            return

        try:
            # Prepare execution environment with df and Plotly available.
            global_ns: Dict[str, Any] = {
                "__name__": "__agent_plot__",
                "df": self._df,
                "go": go,
                "px": px,
                "pd": pd,
            }
            local_ns: Dict[str, Any] = {}
            exec(code, global_ns, local_ns)  # noqa: S102

            # Heuristic: look for a Plotly Figure named 'fig' or 'figure'.
            for name in ("fig", "figure"):
                candidate = local_ns.get(name) or global_ns.get(name)
                if isinstance(candidate, go.Figure):
                    self._viz_panel.show_figure(candidate)
                    return

            # Fallback: search any Figure object in locals/globals.
            for val in list(local_ns.values()) + list(global_ns.values()):
                if isinstance(val, go.Figure):
                    self._viz_panel.show_figure(val)
                    return
        except Exception as exc:  # noqa: BLE001
            # Don't break the app if plotting fails; just show an error.
            messagebox.showerror("Plot Execution Error", str(exc))


def run_ui() -> None:
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    run_ui()

