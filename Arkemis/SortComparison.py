"""
sorting_visualizer_reel.py
==========================

Visualizzazione "Live" degli algoritmi di ordinamento per Instagram Reels.
Invece di un grafico statico dei tempi, questo script mostra gli array
mentre vengono ordinati passo dopo passo simultaneamente.

Caratteristiche:
- Formato 9:16 (Verticale).
- 4 Subplot (uno per algoritmo).
- I generatori (yield) permettono di aggiornare il grafico ad ogni operazione significativa.
- Evidenziazione in BIANCO degli elementi attivi (confronto/scambio).

Usage
-----
Eseguire lo script per generare 'sorting_race_reel.mp4'.
"""

import random
import matplotlib.pyplot as plt
from matplotlib import animation
from itertools import zip_longest
import copy

# --- CONFIGURAZIONE ---
N_ELEMENTS = 60  # Numero di barre (ridotto per renderle visibili su mobile)
FPS = 60         # Frame rate alto per fluidità
INTERVAL = 1     # ms tra frame (il più veloce possibile)

# --- COLORI ARKEMIS ---
COLOR_BG = '#000000'
COLOR_BAR = '#C0EDD8' # Verde pastello
COLOR_ACTIVE = '#FFFFFF' # Bianco per evidenziare l'azione

# --- GENERATORI DI ORDINAMENTO ---
# Questi algoritmi usano 'yield' per restituire lo stato dell'array
# e gli indici attivi ad ogni passo.

def bubble_sort_gen(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            # Yield stato corrente e indici sotto esame
            yield arr, [j, j + 1]
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                yield arr, [j, j + 1]
        if not swapped:
            break
    # Yield finale stato ordinato
    yield arr, []

def insertion_sort_gen(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            yield arr, [j, j + 1] # Visualizza confronto
            arr[j + 1] = arr[j]
            j -= 1
            yield arr, [j + 1] # Visualizza spostamento
        arr[j + 1] = key
        yield arr, [j + 1]
    yield arr, []

def selection_sort_gen(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield arr, [min_idx, j] # Visualizza ricerca minimo
            if arr[j] < arr[min_idx]:
                min_idx = j
        
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            yield arr, [i, min_idx] # Visualizza scambio
    yield arr, []

def heap_sort_gen(arr):
    n = len(arr)
    
    # Helper iterativo interno per poter fare yield
    def heapify_gen(n, i):
        largest = i
        while True:
            l = 2 * i + 1
            r = 2 * i + 2
            
            # Yield confronto
            indices_to_check = [largest]
            if l < n: indices_to_check.append(l)
            if r < n: indices_to_check.append(r)
            yield arr, indices_to_check

            if l < n and arr[l] > arr[largest]:
                largest = l
            if r < n and arr[r] > arr[largest]:
                largest = r
            
            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                yield arr, [i, largest] # Yield scambio
                i = largest
            else:
                break

    # Build maxheap
    for i in range(n // 2 - 1, -1, -1):
        yield from heapify_gen(n, i)

    # Extract elements
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        yield arr, [i, 0] # Yield swap root with end
        yield from heapify_gen(i, 0)
    
    yield arr, []

# --- SETUP VISUALIZZAZIONE ---

def create_race_animation():
    # Dati iniziali identici per tutti
    base_arr = random.sample(range(1, N_ELEMENTS + 1), N_ELEMENTS)
    
    # Setup algoritmi
    algos = [
        ("Heap Sort", heap_sort_gen(copy.deepcopy(base_arr))),
        ("Insertion Sort", insertion_sort_gen(copy.deepcopy(base_arr))),
        ("Selection Sort", selection_sort_gen(copy.deepcopy(base_arr))),
        ("Bubble Sort", bubble_sort_gen(copy.deepcopy(base_arr))),
    ]
    
    # Configurazione figura 9:16
    fig, axes = plt.subplots(4, 1, figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(COLOR_BG)
    
    # Titolo generale
    fig.suptitle("SORTING ALGORITHM\nLIVE RACE", fontsize=50, color='#FFFFFF', weight='bold', y=0.96)

    bars_collections = []
    
    # Inizializzazione Subplots
    for ax, (name, _) in zip(axes, algos):
        ax.set_facecolor(COLOR_BG)
        ax.set_title(name, color=COLOR_BAR, fontsize=30, loc='left', pad=10)
        
        # Rimuovi assi e bordi per pulizia visiva
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Crea le barre iniziali
        bars = ax.bar(range(N_ELEMENTS), base_arr, color=COLOR_BAR, width=0.8)
        bars_collections.append(bars)
        ax.set_xlim(-1, N_ELEMENTS)
        ax.set_ylim(0, N_ELEMENTS + 5)

    plt.tight_layout(rect=[0, 0.02, 1, 0.92]) # Lascia spazio per il titolo

    # Generatore combinato che avanza tutti gli algoritmi di uno step alla volta
    def master_generator():
        # zip_longest permette agli algoritmi veloci di finire mentre gli altri continuano
        generators = [algo[1] for algo in algos]
        for states in zip_longest(*generators):
            yield states

    def update(states):
        if states is None: return []
        
        artists = []
        # states è una tupla di 4 elementi (uno per algo). 
        # Ogni elemento è (arr, active_indices) oppure None se finito.
        
        for i, state in enumerate(states):
            bars = bars_collections[i]
            
            if state is None:
                # Algoritmo finito: colora tutto di verde "successo" (o lascia standard)
                # Assicuriamoci che sia tutto color standard
                for bar in bars:
                    bar.set_color(COLOR_BAR)
                continue
                
            arr, active_indices = state
            
            # Aggiorna altezza barre e colori
            for idx, (bar, height) in enumerate(zip(bars, arr)):
                bar.set_height(height)
                
                # Logica colori
                if idx in active_indices:
                    bar.set_color(COLOR_ACTIVE) # Bianco per azione
                else:
                    bar.set_color(COLOR_BAR) # Verde standard
            
            artists.extend(bars)
            
        return artists

    print("Generazione animazione in corso... (potrebbe richiedere un minuto)")
    
    # Nota: save_count è un limite di sicurezza frame, aumentalo se il video taglia la fine del bubble sort
    anim = animation.FuncAnimation(
        fig, update, frames=master_generator, 
        interval=INTERVAL, blit=True, save_count=2000
    )
    
    output_path = "sorting_race_reel.mp4"
    try:
        anim.save(output_path, writer='ffmpeg', fps=FPS, dpi=100)
        print(f"Salvato: {output_path}")
    except Exception as e:
        print(f"Errore FFMPEG: {e}. Fallback su GIF.")
        anim.save("sorting_race_reel.gif", writer='pillow', fps=30)

if __name__ == '__main__':
    create_race_animation()