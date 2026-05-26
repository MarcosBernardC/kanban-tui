#!/usr/bin/env python3
import json
import os
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Label, Input
from textual.binding import Binding

DATA_FILE = "kanban.json"
DEFAULT_DATA = {"next_id": 1, "TODO": {}, "DOING": {}, "DONE": {}}

# --- Funciones de Datos (se mantienen igual) ---
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

# --- Clases de UI ---
class TareaItem(Static):
    can_focus = True
    def __init__(self, tid, idx, texto, col, creado):
        super().__init__()
        self.tid = tid
        self.indice_visual = idx
        self.texto = texto
        self.columna = col
        self.creado = creado

    def compose(self) -> ComposeResult:
        yield Label(f"[b][accent][{self.indice_visual}][/][/b] {self.texto[:20]}...")

class KanbanApp(App):
    CSS = """
    .columna-contenedor { width: 1fr; height: 100%; border: solid $primary; margin: 0 1; }
    /* Estilo para la columna activa */
    .columna-contenedor.activa { border: thick $accent; background: $surface-darken-1; }
    
    .col-title { text-align: center; text-style: bold; background: $primary; color: $text; padding: 1; }
    TareaItem { background: $surface; margin: 1; padding: 1; border: solid $secondary; }
    TareaItem:focus { border: double $accent; background: $surface-darken-2; }
    Input { dock: bottom; border: tall $accent; }
    """

    BINDINGS = [
        Binding("q", "quit", "Salir"),
        Binding("a", "add_task", "Añadir"),
        Binding("d", "delete_task", "Eliminar"),
        Binding("m", "move_task", "Mover Col."),
        Binding("h", "move_left", "Izquierda"),
        Binding("l", "move_right", "Derecha"),
        Binding("j", "move_down", "Abajo"),
        Binding("k", "move_up", "Arriba"),
    ]

    def __init__(self):
        super().__init__()
        self.columnas_lista = ["todo", "doing", "done"]
        self.col_activa_idx = 0

    def on_mount(self) -> None:
        self.query_one("#input-nueva-tarea", Input).visible = False
        self.actualizar_tablero()
        self._actualizar_estilo_columnas()

    def _actualizar_estilo_columnas(self):
        """Añade o quita la clase 'activa' según el índice actual."""
        for i, col in enumerate(self.columnas_lista):
            contenedor = self.query_one(f"#{col}-col", Vertical)
            if i == self.col_activa_idx:
                contenedor.add_class("activa")
            else:
                contenedor.remove_class("activa")

    def actualizar_tablero(self):
        data = cargar_datos()
        for col in self.columnas_lista:
            container = self.query_one(f"#tasks-{col}", VerticalScroll)
            container.remove_children()
            for idx, (tid, info) in enumerate(data[col.upper()].items(), 1):
                container.mount(TareaItem(tid, idx, info["texto"], col.upper(), info["creado"]))
        self.call_after_refresh(self._enfocar_tarea)

    def _enfocar_tarea(self):
        col = self.columnas_lista[self.col_activa_idx]
        self._actualizar_estilo_columnas()
        tareas = self.query(f"#tasks-{col} TareaItem")
        if tareas:
            tareas[0].focus()

    def action_move_left(self):
        if self.col_activa_idx > 0:
            self.col_activa_idx -= 1
            self._enfocar_tarea()

    def action_move_right(self):
        if self.col_activa_idx < len(self.columnas_lista) - 1:
            self.col_activa_idx += 1
            self._enfocar_tarea()

    # ... resto de métodos igual ...
    def action_move_down(self): self.screen.focus_next()
    def action_move_up(self): self.screen.focus_previous()
    def action_add_task(self):
        inp = self.query_one("#input-nueva-tarea", Input)
        inp.visible = True
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted):
        data = cargar_datos()
        nid = str(data["next_id"])
        data["TODO"][nid] = {"texto": event.value, "creado": datetime.now().strftime("%d/%m/%Y %H:%M")}
        data["next_id"] += 1
        guardar_datos(data)
        event.input.visible = False
        self.actualizar_tablero()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            for col in self.columnas_lista:
                with Vertical(id=f"{col}-col", classes="columna-contenedor"):
                    yield Static(f"❯ {col.upper()}", classes="col-title")
                    yield VerticalScroll(id=f"tasks-{col}")
        yield Input(id="input-nueva-tarea")
        yield Footer()

if __name__ == "__main__":
    KanbanApp().run()
