"""
pathfinding_reel.py
===================

Visualizzazione "Live" di algoritmi di Pathfinding su labirinto 2x2.
Formato Instagram Reel (9:16 verticale).

Modifiche:
- Layout 2x2 (Matrice).
- Labirinto generato con Recursive Backtracker (corridoi veri).
- Sostituito Bidirectional BFS con Greedy Best-First Search.

"""

import matplotlib.pyplot as plt
from matplotlib import animation, colors
import numpy as np
import heapq
from itertools import zip_longest
import random
import sys

# --- CONFIGURAZIONE ---
# Dimensioni devono essere DISPARI per il generatore di labirinti
ROWS, COLS = 41, 25 
FPS = 20             
sys.setrecursionlimit(2000) # Necessario per generazione labirinto ricorsiva

# --- COLORI ---
# 0: Muro (Nero/Grigio Scuro)
# 1: Strada (Nero Profondo)
# 2: Visitato (Verde)
# 3: Frontiera (Bianco)
# 4: Percorso (Viola)
# 5: Start/End (Rosso)
CMAP = colors.ListedColormap(['#1a1a1a', '#000000', '#2E8B57', '#FFFFFF', '#9932CC', '#FF4500'])
BOUNDS = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
NORM = colors.BoundaryNorm(BOUNDS, CMAP.N)

# --- MAZE GENERATION (Recursive Backtracker) ---
def generate_maze_recursive():
    # Inizializza tutto a MURO (0)
    grid = np.zeros((ROWS, COLS), dtype=int)
    
    # Funzione per scavare
    def carve_passages_from(cx, cy):
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            
            if 0 <= nx < ROWS and 0 <= ny < COLS and grid[nx, ny] == 0:
                # Scava il passaggio (muro intermedio + cella target)
                grid[cx + dx//2, cy + dy//2] = 1
                grid[nx, ny] = 1
                carve_passages_from(nx, ny)

    # Inizia a scavare dal punto (1,1)
    grid[1, 1] = 1
    carve_passages_from(1, 1)
    
    # Aggiungi qualche "loop" casuale per rendere il pathfinding meno banale
    # (altrimenti DFS sarebbe troppo fortunato o sfortunato)
    for _ in range(30):
        rx, ry = random.randint(1, ROWS-2), random.randint(1, COLS-2)
        if grid[rx, ry] == 0:
            grid[rx, ry] = 1
            
    start = (1, 1)
    end = (ROWS-2, COLS-2)
    
    # Assicura start/end liberi
    grid[start] = 1
    grid[end] = 1
    
    return grid, start, end

# --- ALGORITMI ---

def get_neighbors(node, grid):
    r, c = node
    neighs = []
    # Ordine shuffle per rendere DFS interessante e non deterministico
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    random.shuffle(dirs)
    
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        # Nota: grid[nr, nc] == 0 è muro qui. 1 è strada.
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr, nc] != 0:
            neighs.append((nr, nc))
    return neighs

def reconstruct_path(came_from, current, grid_visual):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
        if current is None: break
    for r, c in path:
        if grid_visual[r, c] not in [5]: 
            grid_visual[r, c] = 4 

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# 1. DFS
def dfs_gen(grid, start, end):
    grid_vis = grid.copy()
    stack = [start]
    came_from = {start: None}
    visited = {start}
    grid_vis[start] = 5
    grid_vis[end] = 5

    while stack:
        current = stack.pop()
        if current == end:
            reconstruct_path(came_from, end, grid_vis)
            yield grid_vis
            return

        if current != start and current != end:
            grid_vis[current] = 2 
        
        neighbors = get_neighbors(current, grid)
        active_nodes = []
        for next_node in neighbors:
            if next_node not in visited:
                visited.add(next_node)
                came_from[next_node] = current
                stack.append(next_node)
                active_nodes.append(next_node)
                if next_node != end: grid_vis[next_node] = 3 
        yield grid_vis
        for node in active_nodes:
            if node != end: grid_vis[node] = 2 

# 2. BFS
def bfs_gen(grid, start, end):
    grid_vis = grid.copy()
    queue = [start]
    came_from = {start: None}
    visited = {start}
    grid_vis[start] = 5
    grid_vis[end] = 5

    while queue:
        current = queue.pop(0)
        if current == end:
            reconstruct_path(came_from, end, grid_vis)
            yield grid_vis
            return
        if current != start: grid_vis[current] = 2 

        for next_node in get_neighbors(current, grid):
            if next_node not in visited:
                visited.add(next_node)
                came_from[next_node] = current
                queue.append(next_node)
                if next_node != end: grid_vis[next_node] = 3 
        yield grid_vis

# 3. A* (A-Star)
def astar_gen(grid, start, end):
    grid_vis = grid.copy()
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    grid_vis[start] = 5
    grid_vis[end] = 5

    while priority_queue:
        _, current = heapq.heappop(priority_queue)
        if current == end:
            reconstruct_path(came_from, end, grid_vis)
            yield grid_vis
            return
        if current != start: grid_vis[current] = 2 

        for next_node in get_neighbors(current, grid):
            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(end, next_node)
                heapq.heappush(priority_queue, (priority, next_node))
                came_from[next_node] = current
                if next_node != end: grid_vis[next_node] = 3 
        yield grid_vis

# 4. Greedy Best-First Search
def greedy_bfs_gen(grid, start, end):
    grid_vis = grid.copy()
    priority_queue = []
    # Greedy usa SOLO l'euristica per la priorità, ignora il costo accumulato
    heapq.heappush(priority_queue, (0, start))
    came_from = {start: None}
    visited = {start} # Serve visited set per greedy per evitare loop
    grid_vis[start] = 5
    grid_vis[end] = 5

    while priority_queue:
        _, current = heapq.heappop(priority_queue)
        if current == end:
            reconstruct_path(came_from, end, grid_vis)
            yield grid_vis
            return
        if current != start: grid_vis[current] = 2 

        for next_node in get_neighbors(current, grid):
            if next_node not in visited:
                visited.add(next_node)
                priority = heuristic(end, next_node) # Solo euristica
                heapq.heappush(priority_queue, (priority, next_node))
                came_from[next_node] = current
                if next_node != end: grid_vis[next_node] = 3 
        yield grid_vis

# --- ANIMAZIONE MAIN ---

def create_pathfinding_reel():
    # Genera labirinto
    grid_base, start, end = generate_maze_recursive()
    
    algos = [
        ("A* Search", astar_gen(grid_base, start, end)),
        ("Greedy Best-First", greedy_bfs_gen(grid_base, start, end)),
        ("BFS (Optimal)", bfs_gen(grid_base, start, end)),
        ("DFS (Chaos)", dfs_gen(grid_base, start, end)),
    ]
    
    # SETUP GRAFICO 2x2
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 19.2), dpi=80)
    fig.patch.set_facecolor('#000000')
    # Titolo leggermente più in alto
    fig.suptitle("PATHFINDING\nALGORITHMS", fontsize=60, color='white', weight='bold', y=0.95)

    # Appiattiamo axes array per iterare facilmente
    axes_flat = axes.flatten()
    images = []
    
    for ax, (name, _) in zip(axes_flat, algos):
        ax.set_facecolor('#000000')
        ax.set_title(name, color='#C0EDD8', fontsize=25, pad=10)
        ax.axis('off')
        img = ax.imshow(grid_base, cmap=CMAP, norm=NORM, interpolation='nearest')
        images.append(img)

    # Layout stretto ma con spazio per titoli
    plt.tight_layout(rect=[0, 0.0, 1, 0.90])

    def master_generator():
        gens = [a[1] for a in algos]
        for states in zip_longest(*gens):
            yield states

    def update(states):
        if states is None: return []
        artists = []
        for i, state in enumerate(states):
            if state is not None:
                images[i].set_data(state)
                artists.append(images[i])
        return artists

    print("Rendering Pathfinding 2x2 GIF...")
    
    anim = animation.FuncAnimation(
        fig, update, frames=master_generator, 
        interval=40, blit=True, save_count=500
    )
    
    output_path = "pathfinding_race_2x2.gif"
    try:
        anim.save(output_path, writer='pillow', fps=FPS)
        print(f"GIF salvata correttamente: {output_path}")
    except Exception as e:
        print(f"Errore salvataggio: {e}")

if __name__ == '__main__':
    create_pathfinding_reel()