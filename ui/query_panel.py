import tkinter as tk
from tkinter import scrolledtext
from typing import Callable, Optional


class QueryPanel(tk.Frame):
    """Right panel with query input and LLM response display."""

    def __init__(
        self,
        master: tk.Misc,
        on_submit: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._on_submit = on_submit

        self._input = scrolledtext.ScrolledText(self, height=5)
        self._input.pack(fill=tk.X, padx=4, pady=4)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=4)

        self._send_btn = tk.Button(button_frame, text="Send", command=self._handle_send)
        self._send_btn.pack(side=tk.LEFT)

        self._clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self._handle_clear,
        )
        self._clear_btn.pack(side=tk.LEFT, padx=(4, 0))

        self._response = scrolledtext.ScrolledText(self, state="disabled")
        self._response.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 4))

        self._status_var = tk.StringVar(value="")
        self._status_label = tk.Label(self, textvariable=self._status_var, anchor="w")
        self._status_label.pack(fill=tk.X, padx=4, pady=(0, 4))

    def _handle_send(self) -> None:
        query = self._input.get("1.0", tk.END).strip()
        if not query:
            return
        self.set_status("Running query...")
        self._on_submit(query)

    def _handle_clear(self) -> None:
        self._input.delete("1.0", tk.END)
        self.clear_response()
        self.set_status("")

    def append_response(self, text: str) -> None:
        self._response.configure(state="normal")
        self._response.insert(tk.END, text + "\n")
        self._response.configure(state="disabled")
        self._response.see(tk.END)

    def clear_response(self) -> None:
        self._response.configure(state="normal")
        self._response.delete("1.0", tk.END)
        self._response.configure(state="disabled")

    def set_status(self, text: str) -> None:
        self._status_var.set(text)

