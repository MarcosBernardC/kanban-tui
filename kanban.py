#!/usr/bin/env python3
import curses
import json
import os

DATA_FILE = "kanban.json"
DEFAULT_DATA = {"next_id": 1, "TODO": {}, "DOING": {}, "DONE": {}}

def cargar_datos():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, indent=4)
        return DEFAULT_DATA
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def dibujar_interfaz(stdscr):
    # Configuración inicial de curses
    curses.curs_set(0)  # Ocultar cursor físico
    stdscr.keypad(True) # Habilitar flechas de dirección y teclas especiales
    
    # Sincronizar con el fondo nativo claro/transparente de tu terminal
    curses.use_default_colors()
    
    # Inicialización de pares usando tus índices seleccionados de la paleta
    curses.init_pair(1, 104, -1) # TODO  -> Morado/Rosa Pastel
    curses.init_pair(2, 12, -1)  # DOING -> Celeste Claro / Foco
    curses.init_pair(3, 107, -1) # DONE  -> Verde Menta / Apagado

    columnas = ["TODO", "DOING", "DONE"]
    col_activa = 0
    idx_tarea_activa = 0

    while True:
        stdscr.clear()
        data = cargar_datos()
        
        # Mapear tareas de la columna actual a una lista indexable
        tareas_col_actual = list(data[columnas[col_activa]].items())
        
        # Ajustar el índice activo si la lista cambia de tamaño dinámicamente
        if idx_tarea_activa >= len(tareas_col_actual):
            idx_tarea_activa = max(0, len(tareas_col_actual) - 1)

        # 1. Dibujar Encabezado principal
        stdscr.addstr(0, 2, "🛰️  KANBAN TUI", curses.A_BOLD)
        stdscr.addstr(1, 2, "─" * 50)

        # 2. Dibujar las Columnas laterales
        for idx_col, col in enumerate(columnas):
            x_pos = 2 + (idx_col * 24)
            
            # Aplicar color base con brillo (A_BOLD) para ganar consistencia visual
            attr = curses.color_pair(idx_col + 1) | curses.A_BOLD
            
            # Subrayar el título si estamos parados en esa columna
            if idx_col == col_activa:
                attr |= curses.A_UNDERLINE
            
            stdscr.addstr(3, x_pos, f"❯ {col} ({len(data[col])})", attr)

            # Dibujar cada una de las tareas de la columna
            for idx_t, (tid, txt) in enumerate(data[col].items()):
                y_pos = 5 + idx_t
                display_str = f"[{tid}] {txt[:18]}"
                
                # Elemento seleccionado bajo el cursor interactivo
                if idx_col == col_activa and idx_t == idx_tarea_activa:
                    attr_seleccionado = curses.color_pair(idx_col + 1) | curses.A_REVERSE | curses.A_BOLD
                    stdscr.addstr(y_pos, x_pos, f" {display_str} ", attr_seleccionado)
                else:
                    # Texto normal en reposo
                    attr_normal = curses.color_pair(idx_col + 1) | curses.A_BOLD
                    stdscr.addstr(y_pos, x_pos, f"  {display_str}", attr_normal)

        # 3. Dibujar Barra de Guía inferior
        stdscr.addstr(18, 2, "─" * 70)
        stdscr.addstr(19, 2, "[h/l/⇄] Columnas  |  [j/k/⇅] Tareas  |  [a] Añadir  |  [e] Editar  |  [m] Mover  |  [q] Salir", curses.A_DIM)

        stdscr.refresh()

        # 4. Captura del teclado de un solo toque
        key = stdscr.getch()

        if key in [ord('q'), 27]: # 'q' o ESC para salir con gracia
            break
        
        elif key in [ord('l'), curses.KEY_RIGHT]: # Navegar a la Derecha
            col_activa = (col_activa + 1) % 3
            idx_tarea_activa = 0
            
        elif key in [ord('h'), curses.KEY_LEFT]: # Navegar a la Izquierda
            col_activa = (col_activa - 1) % 3
            idx_tarea_activa = 0
            
        elif key in [ord('j'), curses.KEY_DOWN] and tareas_col_actual: # Bajar cursor
            idx_tarea_activa = (idx_tarea_activa + 1) % len(tareas_col_actual)
            
        elif key in [ord('k'), curses.KEY_UP] and tareas_col_actual: # Subir cursor
            idx_tarea_activa = (idx_tarea_activa - 1) % len(tareas_col_actual)

        elif key == ord('a'): # [a] Añadir Tarea
            curses.echo()
            curses.curs_set(1)
            stdscr.addstr(21, 2, "📝 Nueva tarea:                                       ")
            stdscr.move(21, 16)
            texto = stdscr.getstr().decode('utf-8')
            if texto.strip():
                nuevo_id = str(data["next_id"])
                data["TODO"][nuevo_id] = texto
                data["next_id"] += 1
                guardar_datos(data)
            curses.noecho()
            curses.curs_set(0)

        elif key == ord('e') and tareas_col_actual: # [e] Editar Texto de Tarea
            tid, antiguo_texto = tareas_col_actual[idx_tarea_activa]
            curses.echo()
            curses.curs_set(1)
            stdscr.addstr(21, 2, f"✏️ Editar: {antiguo_texto[:30]}... -> ")
            stdscr.move(21, len(antiguo_texto[:30]) + 15)
            nuevo_texto = stdscr.getstr().decode('utf-8')
            if nuevo_texto.strip():
                data[columnas[col_activa]][tid] = nuevo_texto
                guardar_datos(data)
            curses.noecho()
            curses.curs_set(0)

        elif key == ord('m') and tareas_col_actual: # [m] Ciclar Tarea a la Siguiente Columna
            tid, txt = tareas_col_actual[idx_tarea_activa]
            col_origen = columnas[col_activa]
            col_destino = columnas[(col_activa + 1) % 3]
            
            data[col_origen].pop(tid)
            data[col_destino][tid] = txt
            guardar_datos(data)

if __name__ == "__main__":
    curses.wrapper(dibujar_interfaz)
