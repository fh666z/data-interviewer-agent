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

        # Conversation area on top
        self._response = scrolledtext.ScrolledText(self, state="disabled")
        self._response.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 4))

        # Status label
        self._status_var = tk.StringVar(value="")
        self._status_label = tk.Label(self, textvariable=self._status_var, anchor="w")
        self._status_label.pack(fill=tk.X, padx=4, pady=(0, 4))

        # Input field below conversation
        self._input = scrolledtext.ScrolledText(self, height=5)
        self._input.pack(fill=tk.X, padx=4, pady=4)
        # Pressing Enter in the input field will send the query.
        self._input.bind("<Return>", self._handle_enter)

        # Buttons below input
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

    def _handle_send(self) -> None:
        query = self._input.get("1.0", tk.END).strip()
        if not query:
            return
        # Log the user's message in the conversation area.
        self.append_response(f"User: {query}")
        # Clear the input pane after sending.
        self._input.delete("1.0", tk.END)
        self.set_status("Running query...")
        self._on_submit(query)

    def _handle_enter(self, event: tk.Event) -> str:  # type: ignore[type-arg]
        """Handle the Enter key inside the input field by sending the query.

        Returning \"break\" prevents Tkinter from inserting a newline.
        """
        self._handle_send()
        return "break"

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

    def set_send_enabled(self, enabled: bool) -> None:
        """Enable or disable the send button."""
        self._send_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)
