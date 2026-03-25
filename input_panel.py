import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# ── Colors (shared palette) ────────────────────────────────────────────────────
PETAL_PINK   = "#FF6B9D"
PETAL_ROSE   = "#FF8FAB"
PETAL_LAVEND = "#C77DFF"
PETAL_VIOLET = "#9D4EDD"
PETAL_SOFT   = "#FFB3C6"
PETAL_GOLD   = "#FFD166"
PETAL_MINT   = "#06D6A0"
PETAL_SKY    = "#74C0FC"
BG_DARK      = "#0D0D1A"
BG_PANEL     = "#13132B"
BG_CARD      = "#1A1A35"
TEXT_MAIN    = "#F8F0FF"
TEXT_DIM     = "#9B8FB0"
BORDER_COLOR = "#2E2B50"

ALGORITHMS = {
    "Uninformed": ["BFS", "DFS", "IDS", "UCS"],
    "Informed":   ["Greedy", "A*"],
}
INFORMED_ALGOS = {"Greedy", "A*"}


def _section_label(parent, text):
    """Styled section header."""
    row = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8)
    row.pack(fill="x", padx=10, pady=(14, 4))
    ctk.CTkLabel(
        row, text=text,
        font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
        text_color=PETAL_LAVEND, anchor="w"
    ).pack(padx=10, pady=6, fill="x")
    return row


def _entry(parent, placeholder, width=None):
    e = ctk.CTkEntry(
        parent, placeholder_text=placeholder,
        fg_color=BG_DARK, border_color=BORDER_COLOR,
        text_color=TEXT_MAIN, placeholder_text_color=TEXT_DIM,
        font=ctk.CTkFont(family="Courier", size=12),
        corner_radius=8, **({"width": width} if width else {})
    )
    return e


def _petal_btn(parent, text, command, color=PETAL_PINK, width=120):
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=color, hover_color=PETAL_VIOLET,
        text_color=BG_DARK, font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
        corner_radius=20, width=width, height=32
    )


class InputPanel:
    """
    Builds and manages the left-side control panel.
    Calls back into the main app via `callbacks` dict:
        callbacks["on_graph_change"](nodes, edges, heuristics)
        callbacks["on_run"](algo, start, goal, nodes, edges, heuristics)
        callbacks["on_clear"]()
        callbacks["set_status"](msg, color)
    """

    def __init__(self, parent: ctk.CTkScrollableFrame, callbacks: dict):
        self.parent = parent
        self.cb = callbacks

        # Internal state
        self.nodes: dict[str, None] = {}        # node_name -> None
        self.edges: list[tuple] = []            # (u, v, weight)
        self.heuristics: dict[str, float] = {}  # node_name -> h value

        self._build()

    # ══════════════════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════════════════
    def _build(self):
        self._build_algo_section()
        self._build_node_section()
        self._build_edge_section()
        self._build_heuristic_section()
        self._build_search_section()
        self._build_lists_section()
        self._build_action_buttons()

    # ── Algorithm selector ────────────────────────────────────────────────────
    def _build_algo_section(self):
        _section_label(self.parent, "① Algorithm")

        card = ctk.CTkFrame(self.parent, fg_color=BG_CARD, corner_radius=10)
        card.pack(fill="x", padx=10, pady=2)

        # Uninformed
        ctk.CTkLabel(card, text="Uninformed Search",
                     font=ctk.CTkFont(family="Georgia", size=11),
                     text_color=PETAL_GOLD).pack(anchor="w", padx=12, pady=(8, 2))

        self.algo_var = tk.StringVar(value="BFS")
        for algo in ALGORITHMS["Uninformed"]:
            ctk.CTkRadioButton(
                card, text=algo, variable=self.algo_var, value=algo,
                command=self._on_algo_change,
                fg_color=PETAL_PINK, hover_color=PETAL_LAVEND,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(family="Courier", size=12)
            ).pack(anchor="w", padx=24, pady=2)

        # Informed
        ctk.CTkLabel(card, text="Informed Search",
                     font=ctk.CTkFont(family="Georgia", size=11),
                     text_color=PETAL_MINT).pack(anchor="w", padx=12, pady=(10, 2))

        for algo in ALGORITHMS["Informed"]:
            ctk.CTkRadioButton(
                card, text=algo, variable=self.algo_var, value=algo,
                command=self._on_algo_change,
                fg_color=PETAL_MINT, hover_color=PETAL_LAVEND,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(family="Courier", size=12)
            ).pack(anchor="w", padx=24, pady=2)

        ctk.CTkFrame(card, height=8, fg_color="transparent").pack()

    def _on_algo_change(self):
        is_informed = self.algo_var.get() in INFORMED_ALGOS
        state = "normal" if is_informed else "disabled"
        self.h_entry.configure(state=state)
        self.add_h_btn.configure(state=state)
        color = PETAL_MINT if is_informed else TEXT_DIM
        self.h_hint.configure(text_color=color)

    # ── Node input ────────────────────────────────────────────────────────────
    def _build_node_section(self):
        _section_label(self.parent, "② Add Nodes")

        card = ctk.CTkFrame(self.parent, fg_color=BG_CARD, corner_radius=10)
        card.pack(fill="x", padx=10, pady=2)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=10)

        self.node_entry = _entry(row, "Node name  e.g. A")
        self.node_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.node_entry.bind("<Return>", lambda e: self._add_node())

        _petal_btn(row, "＋ Add", self._add_node, PETAL_PINK, width=80).pack(side="left")

    def _add_node(self):
        name = self.node_entry.get().strip()
        if not name:
            return
        if name in self.nodes:
            self.cb["set_status"](f"Node '{name}' already exists", PETAL_GOLD)
            return
        self.nodes[name] = None
        self.node_entry.delete(0, "end")
        self._refresh_lists()
        self._notify_change()
        self.cb["set_status"](f"Node '{name}' added  🌸", PETAL_PINK)

    # ── Edge input ────────────────────────────────────────────────────────────
    def _build_edge_section(self):
        _section_label(self.parent, "③ Add Edges")

        card = ctk.CTkFrame(self.parent, fg_color=BG_CARD, corner_radius=10)
        card.pack(fill="x", padx=10, pady=2)

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(10, 4))

        self.edge_from = _entry(row1, "From")
        self.edge_from.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.edge_to = _entry(row1, "To")
        self.edge_to.pack(side="left", fill="x", expand=True)

        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))

        self.edge_weight = _entry(row2, "Weight (default 1)")
        self.edge_weight.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.edge_weight.bind("<Return>", lambda e: self._add_edge())

        _petal_btn(row2, "＋ Add", self._add_edge, PETAL_ROSE, width=80).pack(side="left")

    def _add_edge(self):
        u = self.edge_from.get().strip()
        v = self.edge_to.get().strip()
        w_str = self.edge_weight.get().strip()

        if not u or not v:
            self.cb["set_status"]("Enter both From and To nodes", PETAL_GOLD)
            return
        if u not in self.nodes:
            self.cb["set_status"](f"Node '{u}' not found — add it first", PETAL_GOLD)
            return
        if v not in self.nodes:
            self.cb["set_status"](f"Node '{v}' not found — add it first", PETAL_GOLD)
            return

        try:
            w = float(w_str) if w_str else 1.0
            if w < 0:
                raise ValueError
        except ValueError:
            self.cb["set_status"]("Weight must be a positive number", PETAL_GOLD)
            return

        if any(e[0] == u and e[1] == v for e in self.edges):
            self.cb["set_status"](f"Edge {u}→{v} already exists", PETAL_GOLD)
            return

        self.edges.append((u, v, w))
        for widget in [self.edge_from, self.edge_to, self.edge_weight]:
            widget.delete(0, "end")
        self._refresh_lists()
        self._notify_change()
        self.cb["set_status"](f"Edge {u} → {v}  (w={w}) added  🌷", PETAL_ROSE)

    # ── Heuristic input ───────────────────────────────────────────────────────
    def _build_heuristic_section(self):
        _section_label(self.parent, "④ Heuristics  (Informed only)")

        card = ctk.CTkFrame(self.parent, fg_color=BG_CARD, corner_radius=10)
        card.pack(fill="x", padx=10, pady=2)

        self.h_hint = ctk.CTkLabel(
            card, text="Select Greedy or A* to enable",
            font=ctk.CTkFont(family="Georgia", size=10, slant="italic"),
            text_color=TEXT_DIM
        )
        self.h_hint.pack(anchor="w", padx=12, pady=(6, 2))

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(4, 4))

        self.h_node = _entry(row1, "Node name")
        self.h_node.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.h_entry = _entry(row1, "h value")
        self.h_entry.pack(side="left", fill="x", expand=True)
        self.h_entry.configure(state="disabled")
        self.h_entry.bind("<Return>", lambda e: self._add_heuristic())

        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))

        self.add_h_btn = _petal_btn(row2, "+ Add Heuristic",
                                    self._add_heuristic, PETAL_MINT, width=200)
        self.add_h_btn.pack(side="left")
        self.add_h_btn.configure(state="disabled")

    def _add_heuristic(self):
        node = self.h_node.get().strip()
        h_str = self.h_entry.get().strip()

        if not node or not h_str:
            self.cb["set_status"]("Enter node name and h value", PETAL_GOLD)
            return
        if node not in self.nodes:
            self.cb["set_status"](f"Node '{node}' not found", PETAL_GOLD)
            return
        try:
            h = float(h_str)
            if h < 0:
                raise ValueError
        except ValueError:
            self.cb["set_status"]("h value must be ≥ 0", PETAL_GOLD)
            return

        self.heuristics[node] = h
        self.h_node.delete(0, "end")
        self.h_entry.delete(0, "end")
        self._refresh_lists()
        self.cb["set_status"](f"h({node}) = {h}  ✦", PETAL_MINT)

    # ── Search config ─────────────────────────────────────────────────────────
    def _build_search_section(self):
        _section_label(self.parent, "⑤ Search")

        card = ctk.CTkFrame(self.parent, fg_color=BG_CARD, corner_radius=10)
        card.pack(fill="x", padx=10, pady=2)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=10)

        self.start_entry = _entry(row, "Start node")
        self.start_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.goal_entry = _entry(row, "Goal node")
        self.goal_entry.pack(side="left", fill="x", expand=True)

        run_btn = _petal_btn(card, "🔍  Run Search", self._run_search,
                             PETAL_VIOLET, width=200)
        run_btn.pack(pady=(0, 12))

    def _run_search(self):
        algo  = self.algo_var.get()
        start = self.start_entry.get().strip()
        goal  = self.goal_entry.get().strip()

        if not self.nodes:
            self.cb["set_status"]("Add nodes first!", PETAL_GOLD); return
        if not start:
            self.cb["set_status"]("Enter a start node", PETAL_GOLD); return
        if not goal:
            self.cb["set_status"]("Enter a goal node", PETAL_GOLD); return
        if start not in self.nodes:
            self.cb["set_status"](f"Start node '{start}' not in graph", PETAL_GOLD); return
        if goal not in self.nodes:
            self.cb["set_status"](f"Goal node '{goal}' not in graph", PETAL_GOLD); return

        if algo in INFORMED_ALGOS:
            missing = [n for n in self.nodes if n not in self.heuristics]
            if missing:
                self.cb["set_status"](
                    f"Missing h values for: {', '.join(missing)}", PETAL_GOLD)
                return

        self.cb["on_run"](algo, start, goal,
                          list(self.nodes.keys()),
                          self.edges,
                          self.heuristics)

    # ── Live lists ────────────────────────────────────────────────────────────
    def _build_lists_section(self):
        _section_label(self.parent, "📋 Current Graph")

        self.list_card = ctk.CTkFrame(self.parent, fg_color=BG_CARD, corner_radius=10)
        self.list_card.pack(fill="x", padx=10, pady=2)

        self.list_box = ctk.CTkTextbox(
            self.list_card, height=140, fg_color=BG_DARK,
            text_color=TEXT_DIM,
            font=ctk.CTkFont(family="Courier", size=11),
            corner_radius=8
        )
        self.list_box.pack(fill="x", padx=8, pady=8)
        self.list_box.configure(state="disabled")
        self._refresh_lists()

    def _refresh_lists(self):
        if not hasattr(self, "list_box"):
            return
        lines = []
        lines.append(f"Nodes ({len(self.nodes)}):  " +
                     "  ".join(self.nodes.keys()) if self.nodes else "Nodes:  —")
        lines.append("")
        if self.edges:
            lines.append(f"Edges ({len(self.edges)}):")
            for u, v, w in self.edges:
                lines.append(f"  {u} → {v}   w={w}")
        else:
            lines.append("Edges:  —")
        if self.heuristics:
            lines.append("")
            lines.append("Heuristics:")
            for n, h in self.heuristics.items():
                lines.append(f"  h({n}) = {h}")

        self.list_box.configure(state="normal")
        self.list_box.delete("1.0", "end")
        self.list_box.insert("end", "\n".join(lines))
        self.list_box.configure(state="disabled")

    # ── Action buttons ────────────────────────────────────────────────────────
    def _build_action_buttons(self):
        row = ctk.CTkFrame(self.parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(10, 20))

        _petal_btn(row, "🗑  Clear All", self._clear_all,
                   "#3D1A2E", width=130).pack(side="left", padx=(0, 8))

        _petal_btn(row, "📋 Sample", self._load_sample,
                   BG_CARD, width=110).pack(side="left")

    def _clear_all(self):
        self.nodes.clear()
        self.edges.clear()
        self.heuristics.clear()
        self._refresh_lists()
        self._notify_change()
        self.cb["on_clear"]()
        self.cb["set_status"]("Graph cleared", TEXT_DIM)

    def _load_sample(self):
        """Load a small sample graph for quick testing."""
        self.nodes.clear()
        self.edges.clear()
        self.heuristics.clear()

        for n in ["A", "B", "C", "D", "E", "G"]:
            self.nodes[n] = None

        self.edges = [
            ("A", "B", 1), ("A", "C", 4),
            ("B", "D", 2), ("B", "E", 5),
            ("C", "E", 1), ("D", "G", 3),
            ("E", "G", 2),
        ]
        self.heuristics = {
            "A": 6, "B": 4, "C": 4,
            "D": 2, "E": 2, "G": 0,
        }
        self._refresh_lists()
        self._notify_change()
        self.cb["set_status"]("Sample graph loaded  🌸", PETAL_PINK)

    # ── Internal ──────────────────────────────────────────────────────────────
    def _notify_change(self):
        self.cb["on_graph_change"](
            list(self.nodes.keys()), self.edges, self.heuristics
        )
