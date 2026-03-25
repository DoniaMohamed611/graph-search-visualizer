import customtkinter as ctk
import tkinter as tk
from input_panel import InputPanel
from algorithms  import run_algorithm
from visualizer  import GraphVisualizer

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PETAL_PINK   = "#FF6B9D"
PETAL_SOFT   = "#FFB3C6"
PETAL_MINT   = "#06D6A0"
PETAL_LAVEND = "#C77DFF"
PETAL_GOLD   = "#FFD166"
PETAL_ROSE   = "#FF8FAB"
BG_DARK      = "#0D0D1A"
BG_PANEL     = "#13132B"
BG_CARD      = "#1A1A35"
TEXT_MAIN    = "#F8F0FF"
TEXT_DIM     = "#9B8FB0"


class GraphSearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("✦ Petal Graph Search ✦")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=BG_DARK)
        self.last_result = None
        self._build_ui()

    def _build_ui(self):
        # ── Top bar ────────────────────────────────────────────────────────
        topbar = ctk.CTkFrame(self, height=64, fg_color=BG_PANEL, corner_radius=0)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        dot_canvas = tk.Canvas(topbar, width=48, height=64,
                               bg=BG_PANEL, highlightthickness=0)
        dot_canvas.pack(side="left", padx=(16,0))
        for i, color in enumerate([PETAL_PINK, PETAL_LAVEND, PETAL_MINT]):
            dot_canvas.create_oval(8,14+i*14,20,26+i*14,fill=color,outline="")

        ctk.CTkLabel(topbar, text="✦  Petal Graph Search System  ✦",
            font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
            text_color=PETAL_SOFT).pack(side="left", padx=12)
        ctk.CTkLabel(topbar, text="BFS · DFS · IDS · UCS · Greedy · A*",
            font=ctk.CTkFont(family="Georgia", size=12),
            text_color=TEXT_DIM).pack(side="left", padx=4)

        # ── Body ───────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        body.pack(fill="both", expand=True)

        # Left input panel
        self.left_panel = ctk.CTkScrollableFrame(
            body, width=320, fg_color=BG_PANEL, corner_radius=0)
        self.left_panel.pack(side="left", fill="y", padx=(0,1))

        # Right side
        right = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        # ── Bottom strip: result + visited log ─────────────────────────────
        bottom = ctk.CTkFrame(right, fg_color=BG_PANEL, corner_radius=0, height=110)
        bottom.pack(side="bottom", fill="x")
        bottom.pack_propagate(False)

        # Result info (left of bottom)
        result_col = ctk.CTkFrame(bottom, fg_color="transparent")
        result_col.pack(side="left", fill="y", padx=(16,0), pady=8)

        self.result_title = ctk.CTkLabel(result_col, text="",
            font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
            text_color=PETAL_MINT, anchor="w")
        self.result_title.pack(anchor="w")

        self.result_path = ctk.CTkLabel(result_col, text="",
            font=ctk.CTkFont(family="Courier", size=12),
            text_color=TEXT_MAIN, anchor="w")
        self.result_path.pack(anchor="w")

        self.result_cost = ctk.CTkLabel(result_col, text="",
            font=ctk.CTkFont(family="Courier", size=12),
            text_color=PETAL_GOLD, anchor="w")
        self.result_cost.pack(anchor="w")

        # Divider
        ctk.CTkFrame(bottom, width=1, fg_color="#2E2B50").pack(
            side="left", fill="y", padx=16, pady=8)

        # Visited log (right of bottom)
        log_col = ctk.CTkFrame(bottom, fg_color="transparent")
        log_col.pack(side="left", fill="both", expand=True, pady=8)

        ctk.CTkLabel(log_col, text="Visited order:",
            font=ctk.CTkFont(family="Georgia", size=11),
            text_color=PETAL_LAVEND, anchor="w").pack(anchor="w")

        self.visited_log = ctk.CTkLabel(log_col, text="—",
            font=ctk.CTkFont(family="Courier", size=11),
            text_color=TEXT_DIM, anchor="w", wraplength=700, justify="left")
        self.visited_log.pack(anchor="w")

        # ── Visualizer canvas ──────────────────────────────────────────────
        viz_frame = tk.Frame(right, bg=BG_DARK)
        viz_frame.pack(fill="both", expand=True)
        self.visualizer = GraphVisualizer(viz_frame)

        # ── Status bar ─────────────────────────────────────────────────────
        self.statusbar = ctk.CTkFrame(self, height=30,
                                      fg_color=BG_PANEL, corner_radius=0)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)
        self.status_lbl = ctk.CTkLabel(self.statusbar,
            text="  ✦  Ready — add nodes to get started",
            font=ctk.CTkFont(family="Courier", size=11),
            text_color=PETAL_MINT, anchor="w")
        self.status_lbl.pack(side="left", fill="x", padx=8)

        # ── Wire InputPanel ────────────────────────────────────────────────
        callbacks = {
            "on_graph_change": self._on_graph_change,
            "on_run":          self._on_run,
            "on_clear":        self._on_clear,
            "set_status":      self.set_status,
        }
        self.input_panel = InputPanel(self.left_panel, callbacks)

    # ── callbacks ──────────────────────────────────────────────────────────

    def _on_graph_change(self, nodes, edges, heuristics):
        self.visualizer.update_graph(nodes, edges, heuristics)

    def _on_run(self, algo, start, goal, nodes, edges, heuristics):
        self.set_status(f"Running {algo}: {start} → {goal} …", PETAL_LAVEND)
        # Clear previous search highlights before running new one
        self.visualizer.path    = []
        self.visualizer.visited = []
        self.visualizer._stop_anim()
        self.visualizer._redraw()
        self.update()
        try:
            result = run_algorithm(algo, nodes, edges, start, goal, heuristics)
            self.last_result = result
            self.visualizer.update_graph(nodes, edges, heuristics)
            self.visualizer.show_result(result)
            self._show_result(result)
        except Exception as e:
            self.set_status(f"Error: {e}", PETAL_GOLD)

    def _show_result(self, result):
        visited_str = "  →  ".join(result.visited) if result.visited else "—"
        self.visited_log.configure(text=visited_str)

        if result.found:
            path_str = "  →  ".join(result.path)
            self.result_title.configure(
                text=f"✦  {result.algo}  —  Path Found! 🌸",
                text_color=PETAL_MINT)
            self.result_path.configure(text=f"Path:  {path_str}")
            self.result_cost.configure(text=f"Total Cost:  {result.cost:.2f}")
            self.set_status(result.message, PETAL_MINT)
        else:
            self.result_title.configure(
                text=f"✦  {result.algo}  —  Not Found 🥀",
                text_color=PETAL_ROSE)
            self.result_path.configure(text=result.message)
            self.result_cost.configure(
                text=f"Nodes visited: {len(result.visited)}")
            self.set_status(result.message, PETAL_ROSE)

    def _on_clear(self):
        self.visualizer.clear()
        self.result_title.configure(text="")
        self.result_path.configure(text="")
        self.result_cost.configure(text="")
        self.visited_log.configure(text="—")

    def set_status(self, msg, color=PETAL_MINT):
        self.status_lbl.configure(text=f"  ✦  {msg}", text_color=color)


if __name__ == "__main__":
    app = GraphSearchApp()
    app.mainloop()
