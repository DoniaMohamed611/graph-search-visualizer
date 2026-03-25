"""
visualizer.py  —  Petal-themed graph visualizer
Correctly highlights the path in gold by matching node pairs regardless of direction.
"""

import math, tkinter as tk, random

BG_DARK      = "#0D0D1A"
PETAL_PINK   = "#FF6B9D"
PETAL_ROSE   = "#FF8FAB"
PETAL_LAVEND = "#C77DFF"
PETAL_GOLD   = "#FFD166"
PETAL_MINT   = "#06D6A0"
PETAL_SKY    = "#74C0FC"
TEXT_MAIN    = "#F8F0FF"
TEXT_DIM     = "#9B8FB0"
EDGE_COLOR   = "#2E2B50"
EDGE_VISITED = "#4A3F6B"

NODE_COLORS = [
    PETAL_PINK, PETAL_LAVEND, PETAL_MINT,
    PETAL_SKY,  PETAL_ROSE,   "#FF9A3C",
    "#A8FF78",  "#F72585",    "#4CC9F0",
]

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _blend(c1, c2, t):
    r1,g1,b1 = _hex_to_rgb(c1)
    r2,g2,b2 = _hex_to_rgb(c2)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


class GraphVisualizer:
    PETAL_N = 6
    NODE_R  = 26
    PETAL_R = 14

    def __init__(self, parent):
        self.parent      = parent
        self.canvas      = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.positions   = {}
        self.nodes       = []
        self.edges       = []
        self.heuristics  = {}
        self.path        = []
        self.visited     = []
        self.node_colors = {}

        self._anim_step  = 0
        self._anim_id    = None
        self._drag_node  = None
        self._drag_ox    = 0
        self._drag_oy    = 0

        self.canvas.bind("<Configure>",       lambda e: self._redraw())
        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    # ── public API ────────────────────────────────────────────────────────────

    def update_graph(self, nodes, edges, heuristics=None):
        self.nodes      = nodes
        self.edges      = edges
        self.heuristics = heuristics or {}
        self._assign_colors()
        self._place_new_nodes()
        self._redraw()

    def show_result(self, result):
        self.path    = result.path
        self.visited = result.visited
        self._stop_anim()
        self._anim_step = 0
        self._animate_visited()

    def clear(self):
        self.nodes=[]; self.edges=[]; self.path=[]; self.visited=[]
        self.positions={}; self.node_colors={}
        self._stop_anim()
        self.canvas.delete("all")

    # ── drag ─────────────────────────────────────────────────────────────────

    def _node_at(self, x, y):
        for n, (nx, ny) in self.positions.items():
            if math.hypot(x-nx, y-ny) <= self.NODE_R + self.PETAL_R:
                return n
        return None

    def _on_press(self, e):
        self._drag_node = self._node_at(e.x, e.y)
        if self._drag_node:
            nx, ny = self.positions[self._drag_node]
            self._drag_ox = e.x - nx
            self._drag_oy = e.y - ny

    def _on_drag(self, e):
        if self._drag_node:
            self.positions[self._drag_node] = (e.x - self._drag_ox,
                                               e.y - self._drag_oy)
            self._redraw()

    def _on_release(self, e):
        self._drag_node = None

    # ── layout ────────────────────────────────────────────────────────────────

    def _assign_colors(self):
        for i, n in enumerate(self.nodes):
            if n not in self.node_colors:
                self.node_colors[n] = NODE_COLORS[i % len(NODE_COLORS)]

    def _place_new_nodes(self):
        for n in list(self.positions):
            if n not in self.nodes:
                del self.positions[n]

        new_nodes = [n for n in self.nodes if n not in self.positions]
        if not new_nodes:
            return

        w  = self.canvas.winfo_width()  or 800
        h  = self.canvas.winfo_height() or 500
        cx, cy = w/2, h/2
        r  = min(cx, cy) * 0.62

        if not self.positions:
            total = len(self.nodes)
            for i, node in enumerate(self.nodes):
                angle = 2*math.pi*i/total - math.pi/2
                self.positions[node] = (cx + r*math.cos(angle),
                                        cy + r*math.sin(angle))
        else:
            n   = len(new_nodes)
            off = random.uniform(0, 2*math.pi)
            for i, node in enumerate(new_nodes):
                angle = 2*math.pi*i/max(n,1) + off
                self.positions[node] = (cx + r*math.cos(angle),
                                        cy + r*math.sin(angle))

    # ── drawing ───────────────────────────────────────────────────────────────

    def _redraw(self):
        self.canvas.delete("all")
        if not self.nodes:
            return
        self._draw_bg_particles()
        self._draw_edges()
        self._draw_nodes()
        self._draw_legend()

    def _draw_bg_particles(self):
        w = self.canvas.winfo_width()  or 800
        h = self.canvas.winfo_height() or 500
        rng = random.Random(42)
        for _ in range(60):
            x=rng.uniform(0,w); y=rng.uniform(0,h); s=rng.uniform(0.5,2.5)
            c=rng.choice(["#1A1A3A","#1E1E40","#16163A","#20203E"])
            self.canvas.create_oval(x-s,y-s,x+s,y+s,fill=c,outline="")

    def _is_path_edge(self, u, v):
        """Check if edge (u,v) is part of the solution path — direction independent."""
        if len(self.path) < 2:
            return False
        for i in range(len(self.path) - 1):
            a, b = self.path[i], self.path[i+1]
            if (u == a and v == b) or (u == b and v == a):
                return True
        return False

    def _draw_edges(self):
        visited_set = set(self.visited)

        for u, v, w in self.edges:
            if u not in self.positions or v not in self.positions:
                continue
            x1, y1 = self.positions[u]
            x2, y2 = self.positions[v]

            is_path    = self._is_path_edge(u, v)
            both_visit = u in visited_set and v in visited_set

            if is_path:
                # Draw glowing gold path
                for width, color in [(10, "#2A1E00"), (7, "#5C3D00"),
                                     (4, PETAL_GOLD), (2, "#FFF5B0")]:
                    self.canvas.create_line(x1, y1, x2, y2,
                                            fill=color, width=width,
                                            smooth=True, capstyle="round")
                # Draw arrow in correct direction along the path
                self._draw_path_arrow(u, v, x1, y1, x2, y2)

            elif both_visit:
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill=EDGE_VISITED, width=2, dash=(6,4))
            else:
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill=EDGE_COLOR, width=1.5)

            # Weight label
            mx, my = (x1+x2)/2, (y1+y2)/2
            dx, dy = x2-x1, y2-y1
            length = math.hypot(dx, dy) or 1
            ox, oy = -dy/length*14, dx/length*14
            lcolor = PETAL_GOLD if is_path else TEXT_DIM
            self.canvas.create_text(mx+ox, my+oy,
                text=str(int(w) if w == int(w) else w),
                fill=lcolor, font=("Courier", 10, "bold"))

    def _draw_path_arrow(self, u, v, x1, y1, x2, y2):
        """Draw arrow in the correct direction of travel along the path."""
        # Find direction in path
        ax, ay, bx, by = x1, y1, x2, y2
        for i in range(len(self.path)-1):
            if self.path[i] == v and self.path[i+1] == u:
                # reverse direction
                ax, ay, bx, by = x2, y2, x1, y1
                break

        dx, dy = bx-ax, by-ay
        length = math.hypot(dx, dy) or 1
        ux, uy = dx/length, dy/length
        r = self.NODE_R + 4
        tx, ty = bx - ux*r, by - uy*r
        px, py = -uy, ux
        size = 9
        p1 = (tx - ux*size + px*size*0.5, ty - uy*size + py*size*0.5)
        p2 = (tx - ux*size - px*size*0.5, ty - uy*size - py*size*0.5)
        self.canvas.create_polygon(tx, ty, p1[0], p1[1], p2[0], p2[1],
                                   fill=PETAL_GOLD, outline="#FFF5B0", width=1)

    def _draw_nodes(self):
        path_set    = set(self.path)
        visited_set = set(self.visited[:self._anim_step])
        for node in self.nodes:
            if node not in self.positions:
                continue
            x, y  = self.positions[node]
            color = self.node_colors.get(node, PETAL_PINK)
            self._draw_petal_node(x, y, node, color,
                                  node in path_set,
                                  node in visited_set)

    def _draw_petal_node(self, x, y, label, color, in_path, in_visited):
        R=self.NODE_R; PR=self.PETAL_R; N=self.PETAL_N

        # Glow rings
        if in_path:
            for r_off, a in [(R+18,"#3D2E00"),(R+12,"#7A5900"),(R+6,"#5C4400")]:
                self.canvas.create_oval(x-r_off,y-r_off,x+r_off,y+r_off,
                                        fill=a, outline="")
        elif in_visited:
            for r_off, a in [(R+12,"#1A2E2E"),(R+6,"#0D4040")]:
                self.canvas.create_oval(x-r_off,y-r_off,x+r_off,y+r_off,
                                        fill=a, outline="")

        # Petals
        for i in range(N):
            angle = 2*math.pi*i/N
            px_ = x + (R*0.85)*math.cos(angle)
            py_ = y + (R*0.85)*math.sin(angle)
            if in_path:
                pc=_blend(color,PETAL_GOLD,0.5); oc=PETAL_GOLD
            elif in_visited:
                pc=_blend(color,PETAL_MINT,0.4); oc=PETAL_MINT
            else:
                pc=_blend(color,BG_DARK,0.25); oc=_blend(color,"#FFFFFF",0.2)
            self.canvas.create_oval(px_-PR,py_-PR,px_+PR,py_+PR,
                                    fill=pc, outline=oc, width=1)

        # Center circle
        if in_path:      cf=PETAL_GOLD; co="#FFF0A0"; tc=BG_DARK
        elif in_visited: cf=PETAL_MINT; co="#A0FFF0"; tc=BG_DARK
        else:            cf=color;      co=_blend(color,"#FFFFFF",0.5); tc=BG_DARK

        self.canvas.create_oval(x-R,y-R,x+R,y+R,fill=cf,outline=co,width=2)
        self.canvas.create_text(x, y, text=label, fill=tc,
                                font=("Georgia",13,"bold"))

        # Heuristic label
        if label in self.heuristics:
            self.canvas.create_text(x, y+R+14,
                text=f"h={self.heuristics[label]}",
                fill=PETAL_LAVEND, font=("Courier",9))

    def _draw_legend(self):
        w  = self.canvas.winfo_width() or 800
        x, y = w-170, 18
        pad, rh = 10, 22
        self.canvas.create_rectangle(x-pad,y-pad,x+150,y+rh*4+pad,
                                     fill="#13132B",outline="#2E2B50",width=1)
        self.canvas.create_text(x+65,y+4,text="✦  Legend",
                                fill=TEXT_MAIN,font=("Georgia",10,"bold"),
                                anchor="center")
        for i,(c,lbl) in enumerate([
            (PETAL_GOLD,"Path node"),
            (PETAL_MINT,"Visited node"),
            ("#9B8FB0", "Unvisited node"),
        ]):
            cy2 = y+rh*(i+1)+4
            self.canvas.create_oval(x,cy2-7,x+14,cy2+7,fill=c,outline="")
            self.canvas.create_text(x+22,cy2,text=lbl,fill=TEXT_DIM,
                                    font=("Courier",9),anchor="w")
        self.canvas.create_text(x+65,y+rh*4+2,
                                text="🖱 drag nodes to reposition",
                                fill="#4A3F6B",font=("Courier",8),anchor="center")

    # ── animation ─────────────────────────────────────────────────────────────

    def _animate_visited(self):
        if self._anim_step <= len(self.visited):
            self._redraw()
            self._anim_step += 1
            self._anim_id = self.canvas.after(180, self._animate_visited)
        else:
            self._redraw()

    def _stop_anim(self):
        if self._anim_id:
            self.canvas.after_cancel(self._anim_id)
            self._anim_id = None
