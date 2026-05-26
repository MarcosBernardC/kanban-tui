#!/usr/bin/env python3 import json
import os
import json
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Label, Input
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import TextArea # Importa esto al principio

DATA_FILE = "kanban.json"
DEFAULT_DATA = {"next_id": 1, "TODO": {}, "DOING": {}, "DONE": {}}

# --- Funciones de Datos ---
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

class TareaItem(Static):
    can_focus = True
    def __init__(self, tid, info, col):
        super().__init__()
        self.tid = tid
        self.info = info
        self.columna = col
    def compose(self) -> ComposeResult:
        yield Label(f"[b][{self.tid}][/b] {self.info['texto'][:20]}")

class ConfirmacionModal(ModalScreen):
    BINDINGS = [Binding("s", "confirmar", "Sí"), Binding("n", "cancelar", "No")]
    def __init__(self, mensaje):
        super().__init__()
        self.mensaje = mensaje
    def compose(self) -> ComposeResult:
        yield Vertical(Label(self.mensaje), Label("[b]S[/]: Guardar | [b]N[/]: Volver a editar"), id="modal-box")
    def action_confirmar(self): self.dismiss(True)
    def action_cancelar(self): self.dismiss(False)

class EditarTareaModal(ModalScreen):
    BINDINGS = [
        Binding("i", "insertar", "Insertar"),
        Binding("escape", "modo_normal", "Normal"),
        Binding("colon", "activar_comandos", ":"),
        # Navegación estilo Vim
        Binding("h", "cursor_left", "Izquierda", show=False),
        Binding("j", "cursor_down", "Abajo", show=False),
        Binding("k", "cursor_up", "Arriba", show=False),
        Binding("l", "cursor_right", "Derecha", show=False),
    ]

    def __init__(self, item: TareaItem): # <--- Aquí recibes el item
        super().__init__()
        self.item = item                 # <--- FALTABA ESTA LÍNEA CRÍTICA
   
    def action_cursor_left(self): 
        self.text_area.action_cursor_left()

    def action_cursor_right(self): 
        self.text_area.action_cursor_right()

    def action_cursor_up(self): 
        self.text_area.action_cursor_up()

    def action_cursor_down(self): 
        self.text_area.action_cursor_down()
        
    def compose(self) -> ComposeResult:
        # Ahora self.item ya existe y puede ser usado aquí
        with Vertical(id="modal-box"):
            yield Label(f"Tarea #{self.item.tid}", id="modal-title")
            self.text_area = TextArea(text=self.item.info['texto'], id="edit-input")
            self.text_area.read_only = True
            yield self.text_area
            
            # Línea de comandos oculta inicialmente
            self.cmd_input = Input(placeholder=":", id="cmd-line")
            self.cmd_input.display = False 
            yield self.cmd_input
            
            self.info_label = Label("-- NORMAL -- | i: Insertar | : Comandos")
            yield self.info_label

    def action_insertar(self):
        self.text_area.read_only = False
        self.text_area.focus()
        self.info_label.update("-- INSERT -- | Esc: Normal")

    def action_modo_normal(self):
        self.text_area.read_only = True
        self.cmd_input.display = False
        self.info_label.update("-- NORMAL -- | i: Insertar | : Comandos")

    def action_activar_comandos(self):
        self.cmd_input.display = True
        self.cmd_input.focus()
        self.cmd_input.value = ""

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "cmd-line":
            cmd = event.value.strip()
            
            # Lógica centralizada de guardado
            def guardar():
                data = cargar_datos()
                data[self.item.columna][str(self.item.tid)]["texto"] = self.text_area.text
                guardar_datos(data)

            if cmd == "w":
                # :w - Guardar y volver a modo normal
                guardar()
                self.action_modo_normal()
            
            elif cmd == "wq":
                # :wq - Guardar y salir
                guardar()
                self.dismiss(True)
            
            elif cmd == "q":
                # :q - Salir sin guardar
                self.dismiss(False)
            
            elif cmd == "q!":
                # :q! - Salir forzado (equivalente a q aquí)
                self.dismiss(False)
                
            else:
                # Comando no reconocido, volvemos a modo normal
                self.action_modo_normal()

class KanbanApp(App):
    CSS = """
    .columna-contenedor { width: 1fr; height: 100%; border: solid $primary; margin: 0 1; }
    .columna-contenedor.activa { border: thick $accent; background: $surface-darken-1; }
    .col-title { text-align: center; text-style: bold; background: $primary; padding: 1; }
    TareaItem { background: $surface; margin: 1; padding: 1; border: solid $secondary; }
    TareaItem:focus { border: double $accent; background: $surface-darken-2; }
    #modal-box { align: center middle; width: 50; height: auto; border: thick $accent; background: $surface; padding: 1; }
    TextArea { height: auto; min-height: 5; border: solid $secondary; }
    TextArea:focus { border: solid $accent; }
    #cmd-line {
        background: $surface;
        border: none;
        padding: 0;
        height: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Salir"),
        Binding("enter", "entrar_tarjeta", "Editar/Abrir"),
        Binding("h", "move_left", "←"),
        Binding("l", "move_right", "→"),
        Binding("j", "move_down", "↓"),
        Binding("k", "move_up", "↑"),
        Binding("J", "move_task_down", "Mover ↓"),
        Binding("K", "move_task_up", "Mover ↑"),
    ]

    def __init__(self):
        super().__init__()
        self.columnas = ["TODO", "DOING", "DONE"]
        self.col_idx = 0

    def on_mount(self) -> None:
        # Esto establece el tema de forma segura al arrancar la app
        self.theme = "ansi-light" 
        self.actualizar_tablero()

    def actualizar_tablero(self):
        data = cargar_datos()
        for col in self.columnas:
            container = self.query_one(f"#tasks-{col}", VerticalScroll)
            container.remove_children()
            for tid, info in data[col].items():
                container.mount(TareaItem(tid, info, col))
        self.call_after_refresh(self._actualizar_foco)

    def _actualizar_foco(self):
        for i, col in enumerate(self.columnas):
            self.query_one(f"#{col}-col").set_class(i == self.col_idx, "activa")
        
        # Obtenemos todas las tareas de la columna actual
        tareas = self.query(f"#tasks-{self.columnas[self.col_idx]} TareaItem")
        
        if tareas:
            # Si ya hay un elemento enfocado en la pantalla, no lo cambies
            # Si no hay nada enfocado, enfoca el primero
            if not self.screen.focused or not isinstance(self.screen.focused, TareaItem):
                tareas[0].focus()
                tareas[0].scroll_visible()

    def action_entrar_tarjeta(self):
        f = self.screen.focused
        if isinstance(f, TareaItem):
            self.push_screen(EditarTareaModal(f), lambda res: self.actualizar_tablero())

    def action_move_left(self):
        if self.col_idx > 0: self.col_idx -= 1; self._actualizar_foco()
    def action_move_right(self):
        if self.col_idx < len(self.columnas) - 1: self.col_idx += 1; self._actualizar_foco()
    def action_move_down(self):
        self._mover_foco_circular(1)

    def action_move_up(self):
        self._mover_foco_circular(-1)
    
    def _mover_foco_circular(self, delta):
        # Buscamos todas las tareas de la columna actual
        tareas = self.query(f"#tasks-{self.columnas[self.col_idx]} TareaItem")
        if not tareas:
            return

        # Determinamos cuál es el índice actual
        focused = self.screen.focused
        if isinstance(focused, TareaItem):
            curr_idx = next((i for i, t in enumerate(tareas) if t == focused), 0)
        else:
            curr_idx = 0

        # Calculamos el nuevo índice con lógica circular
        new_idx = (curr_idx + delta) % len(tareas)
        
        # Aplicamos el foco y scroll
        tarea_objetivo = tareas[new_idx]
        tarea_objetivo.focus()
        tarea_objetivo.scroll_visible()
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            for col in self.columnas:
                with Vertical(id=f"{col}-col", classes="columna-contenedor"):
                    yield Static(f"❯ {col}", classes="col-title")
                    yield VerticalScroll(id=f"tasks-{col}")
        yield Footer()

    def action_move_task_up(self):
        self._reordenar_tarea(-1)

    def action_move_task_down(self):
        self._reordenar_tarea(1)

    def _reordenar_tarea(self, delta):
        focused = self.screen.focused
        if not isinstance(focused, TareaItem):
            return

        col = focused.columna
        data = cargar_datos()
        
        # Convertir a lista de tuplas para poder mover elementos
        items = list(data[col].items())
        # Encontrar el índice de la tarea actual
        curr_idx = next(i for i, (tid, _) in enumerate(items) if tid == str(focused.tid))
        new_idx = curr_idx + delta
        
        if 0 <= new_idx < len(items):
            items[curr_idx], items[new_idx] = items[new_idx], items[curr_idx]
            data[col] = dict(items)
            guardar_datos(data)
            self.actualizar_tablero()
            
            # Recuperar el foco y asegurar que sea visible
            def asegurar_foco_y_scroll():
                tarea = self.query(f"#tasks-{col} TareaItem")[new_idx]
                tarea.focus()
                tarea.scroll_visible() # <--- Crucial aquí
            
            self.call_after_refresh(asegurar_foco_y_scroll)

if __name__ == "__main__":
    KanbanApp().run()
