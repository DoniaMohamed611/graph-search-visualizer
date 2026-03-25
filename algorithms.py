
from collections import deque
import heapq
from dataclasses import dataclass

@dataclass
class SearchResult:
    found:   bool
    path:    list
    cost:    float
    visited: list
    algo:    str
    message: str

def _build_adj(nodes, edges):
    """Build adjacency list: {node: [(neighbor, weight), ...]}"""
    adj = {n: [] for n in nodes}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj

def _build_adj_dict(nodes, edges):
    """Build dict-of-dicts for UCS: {node: {neighbor: weight}}"""
    adj = {n: {} for n in nodes}
    for u, v, w in edges:
        adj[u][v] = w
        adj[v][u] = w
    return adj

def _build_simple_adj(nodes, edges):
    """Build simple adjacency list (no weights): {node: [neighbor, ...]}"""
    adj = {n: [] for n in nodes}
    for u, v, w in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def _path_cost(path, adj_weighted):
    cost = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        for nb, w in adj_weighted[u]:
            if nb == v:
                cost += w
                break
    return cost


# ── BFS ───────────────────────────────────────────────────────────────────────
def bfs(nodes, edges, start, goal):
    adj     = _build_simple_adj(nodes, edges)
    adj_w   = _build_adj(nodes, edges)

    visited = set([start])
    queue   = deque([[start]])
    visited_order = []

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node not in visited_order:
            visited_order.append(node)

        if node == goal:
            cost = _path_cost(path, adj_w)
            return SearchResult(True, path, cost, visited_order, "BFS",
                                f"Path found! Cost = {cost:.2f}")

        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return SearchResult(False, [], 0, visited_order, "BFS",
                        f"Node '{goal}' was NOT found from '{start}'.")
# ── DFS ───────────────────────────────────────────────────────────────────────
def dfs(nodes, edges, start, goal):
    adj     = _build_simple_adj(nodes, edges)
    adj_w   = _build_adj(nodes, edges)

    stack   = [[start]]
    visited = set()
    visited_order = []

    while stack:
        path = stack.pop()
        node = path[-1]

        if node not in visited_order:
            visited_order.append(node)

        if node == goal:
            cost = _path_cost(path, adj_w)
            return SearchResult(True, path, cost, visited_order, "DFS",
                                f"Path found! Cost = {cost:.2f}")

        if node not in visited:
            visited.add(node)

            for neighbor in adj[node]:
                if neighbor not in visited:
                    stack.append(path + [neighbor])

    return SearchResult(False, [], 0, visited_order, "DFS",
                        f"Node '{goal}' was NOT found from '{start}'.")
# ── IDS ───────────────────────────────────────────────────────────────────────
def ids(nodes, edges, start, goal):
    adj     = _build_simple_adj(nodes, edges)
    adj_w   = _build_adj(nodes, edges)

    def dls(node, goal, depth, path, visited_order):
        if node not in visited_order:
            visited_order.append(node)

        if node == goal:
            return path

        if depth == 0:
            return None

        for neighbor in adj[node]:
            if neighbor not in path:
                result = dls(neighbor, goal, depth - 1, path + [neighbor], visited_order)
                if result:
                    return result

        return None

    max_depth = len(nodes)

    for depth in range(max_depth + 1):
        visited_order = []
        result = dls(start, goal, depth, [start], visited_order)

        if result:
            cost = _path_cost(result, adj_w)
            return SearchResult(True, result, cost, visited_order, "IDS",
                                f"Path found at depth {depth}! Cost = {cost:.2f}")

    return SearchResult(False, [], 0, visited_order, "IDS",
                        f"Node '{goal}' was NOT found from '{start}'.")
# ── UCS ───────────────────────────────────────────────────────────────────────
def ucs(nodes, edges, start, goal):
    adj = _build_adj(nodes, edges)

    pq = [(0, start, [start])]
    visited = set()
    visited_order = []

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue

        visited.add(node)

        if node not in visited_order:
            visited_order.append(node)

        if node == goal:
            return SearchResult(True, path, cost, visited_order, "UCS",
                                f"Path found! Cost = {cost:.2f}")

        for neighbor, weight in adj[node]:
            if neighbor not in visited:
                heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))

    return SearchResult(False, [], 0, visited_order, "UCS",
                        f"Node '{goal}' was NOT found from '{start}'.")
# ── Greedy Best-First ─────────────────────────────────────────────────────────
def greedy(nodes, edges, start, goal, heuristic):
    adj     = _build_adj(nodes, edges)
    adj_w   = adj

    pq = [(heuristic[start], start, [start])]
    visited = set()
    visited_order = []

    while pq:
        h, node, path = heapq.heappop(pq)

        if node in visited:
            continue

        visited.add(node)

        if node not in visited_order:
            visited_order.append(node)

        if node == goal:
            cost = _path_cost(path, adj_w)
            return SearchResult(True, path, cost, visited_order, "Greedy",
                                f"Path found! Cost = {cost:.2f}")

        for neighbor, _ in adj[node]:
            if neighbor not in visited:
                heapq.heappush(pq, (heuristic[neighbor], neighbor, path + [neighbor]))

    return SearchResult(False, [], 0, visited_order, "Greedy",
                        f"Node '{goal}' was NOT found from '{start}'.")

# ── A* ────────────────────────────────────────────────────────────────────────
def astar(nodes, edges, start, goal, heuristic):
    adj = _build_adj(nodes, edges)

    pq = [(heuristic[start], start, [start], 0)]
    visited = set()
    visited_order = []
    g_values = {start: 0}

    while pq:
        f, node, path, g = heapq.heappop(pq)

        if node in visited:
            continue

        visited.add(node)

        if node not in visited_order:
            visited_order.append(node)

        if node == goal:
            return SearchResult(True, path, g, visited_order, "A*",
                                f"Path found! Cost = {g:.2f}")

        for neighbor, weight in adj[node]:
            if neighbor in visited:
                continue

            new_g = g + weight

            if neighbor not in g_values or new_g < g_values[neighbor]:
                g_values[neighbor] = new_g
                new_f = new_g + heuristic[neighbor]

                heapq.heappush(pq, (new_f, neighbor, path + [neighbor], new_g))

    return SearchResult(False, [], 0, visited_order, "A*",
                        f"Node '{goal}' was NOT found from '{start}'.")
# ── Dispatcher ────────────────────────────────────────────────────────────────
def run_algorithm(algo, nodes, edges, start, goal, heuristics=None):
    h = heuristics or {}
    if algo == "BFS":    return bfs(nodes, edges, start, goal)
    if algo == "DFS":    return dfs(nodes, edges, start, goal)
    if algo == "IDS":    return ids(nodes, edges, start, goal)
    if algo == "UCS":    return ucs(nodes, edges, start, goal)
    if algo == "Greedy": return greedy(nodes, edges, start, goal, h)
    if algo == "A*":     return astar(nodes, edges, start, goal, h)
    raise ValueError(f"Unknown algorithm: {algo}")
