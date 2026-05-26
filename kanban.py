#!/usr/bin/env python3
import json
import os
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Label, Input
from textual.binding import Binding

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

class TareaItem(Static):
    """Widget de tarea interactivo simplificado."""
    can_focus = True  

    def __init__(self, tid: str, texto: str, columna: str, **kwargs):
        super().__init__(**kwargs)
        self.tid = tid
        self.texto = texto
        self.columna = columna

    def compose(self) -> ComposeResult:
        yield Label(f"[b][#7cfc00][{self.tid}][/][/b] {self.texto}")

class KanbanApp(App):
    TITLE = "🛰️ KANBAN TUI"
    
    CSS = """
    Screen {
        background: transparent;
    }
    Horizontal {
        height: 1fr;
        margin: 0;
    }
    .columna-contenedor {
        width: 1fr;
        height: 1fr;
        border: solid $primary-darken-1;
        margin: 0 1;
        padding: 0 1;
        background: transparent;
    }
    .col-title {
        text-align: center;
        text-style: bold;
        background: $primary-darken-3;
        color: $text;
        margin: 1 0;
        height: 3;
        content-align: center middle;
    }
    #todo-col { border: solid #6c71c4; }
    #doing-col { border: solid #268bd2; }
    #done-col { border: solid #859900; }
    
    .lista-tareas {
        height: 1fr;
        overflow-y: scroll;
    }
    
    TareaItem {
        background: $surface;
        margin: 0 0 1 0;
        padding: 0 1;
        border: solid $primary-darken-2;
        height: auto;
    }
    TareaItem:focus {
        border: double #268bd2;
        background: $primary-darken-2;
    }
    
    Input {
        margin: 1 1 0 1;
        border: tall #6c71c4;
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Salir", show=True),
        Binding("a", "add_task", "Añadir", show=True),
        Binding("e", "edit_task", "Editar", show=True),
        Binding("d,x", "delete_task", "Eliminar", show=True),
        Binding("m", "move_task", "Mover Col.", show=True),
        Binding("left,h", "move_left", "Col. Izquierda", show=False),
        Binding("right,l", "move_right", "Col. Derecha", show=False),
        Binding("down,j", "move_down", "Bajar Tarea", show=False),
        Binding("up,k", "move_up", "Subir Tarea", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="todo-col", classes="columna-contenedor"):
                yield Static("❯ TODO (0)", classes="col-title", id="title-todo")
                with VerticalScroll(id="tasks-todo", classes="lista-tareas"):
                    pass
            with Vertical(id="doing-col", classes="columna-contenedor"):
                yield Static("❯ DOING (0)", classes="col-title", id="title-doing")
                with VerticalScroll(id="tasks-doing", classes="lista-tareas"):
                    pass
            with Vertical(id="done-col", classes="columna-contenedor"):
                yield Static("❯ DONE (0)", classes="col-title", id="title-done")
                with VerticalScroll(id="tasks-done", classes="lista-tareas"):
                    pass
        yield Input(placeholder="Escribe la tarea...", id="input-nueva-tarea")
        yield Footer()

    def on_mount(self) -> None:
        self.columnas_lista = ["todo", "doing", "done"]
        self.col_activa_idx = 0
        self.tarea_activa_idx = 0 
        self.tarea_en_edicion = None  
        
        self.actualizar_interfaz()
        self.query_one("#input-nueva-tarea", Input).visible = False

    def actualizar_interfaz(self, select_tid: str = None) -> None:
        data = cargar_datos()
        
        self.query_one("#title-todo", Static).update(f"❯ TODO ({len(data['TODO'])})")
        self.query_one("#title-doing", Static).update(f"❯ DOING ({len(data['DOING'])})")
        self.query_one("#title-done", Static).update(f"❯ DONE ({len(data['DONE'])})")

        target_widget = None

        for col_name in self.columnas_lista:
            container = self.query_one(f"#tasks-{col_name}", VerticalScroll)
            container.query(TareaItem).remove()
            
            for tid, txt in data[col_name.upper()].items():
                item = TareaItem(tid, txt, col_name.upper())
                container.mount(item)
                
                # Si es la tarea que queremos seleccionar explícitamente, guardamos la referencia
                if select_tid and select_tid == tid:
                    target_widget = item
                    # Sincronizamos las coordenadas internas de la App
                    self.col_activa_idx = self.columnas_lista.index(col_name)
                    tareas_en_col = list(data[col_name.upper()].keys())
                    self.tarea_activa_idx = tareas_en_col.index(tid)

        # Usamos call_after_refresh para asegurar que Textual renderizó los nuevos elementos antes de enfocar
        if target_widget:
            self.call_after_refresh(target_widget.focus)
        else:
            self.call_after_refresh(self._refrescar_foco)

    def _refrescar_foco(self) -> None:
        """Enfoca la tarea correspondiente según las coordenadas actuales de forma segura."""
        col_name = self.columnas_lista[self.col_activa_idx]
        container = self.query_one(f"#tasks-{col_name}", VerticalScroll)
        tareas = list(container.query(TareaItem))
        
        if tareas:
            self.tarea_activa_idx = min(self.tarea_activa_idx, len(tareas) - 1)
            if self.tarea_activa_idx < 0:
                self.tarea_activa_idx = 0
            tareas[self.tarea_activa_idx].focus()
        else:
            self.tarea_activa_idx = 0
            # Si la columna está vacía, mantenemos el foco en un lugar seguro para no perder el teclado
            container.focus()

    # --- NAVEGACIÓN ---

    def action_move_left(self) -> None:
        if self.col_activa_idx > 0:
            self.col_activa_idx -= 1
            self._refrescar_foco()

    def action_move_right(self) -> None:
        if self.col_activa_idx < len(self.columnas_lista) - 1:
            self.col_activa_idx += 1
            self._refrescar_foco()

    def action_move_down(self) -> None:
        col_name = self.columnas_lista[self.col_activa_idx]
        container = self.query_one(f"#tasks-{col_name}", VerticalScroll)
        tareas = list(container.query(TareaItem))
        if tareas and self.tarea_activa_idx < len(tareas) - 1:
            self.tarea_activa_idx += 1
            tareas[self.tarea_activa_idx].focus()

    def action_move_up(self) -> None:
        col_name = self.columnas_lista[self.col_activa_idx]
        container = self.query_one(f"#tasks-{col_name}", VerticalScroll)
        tareas = list(container.query(TareaItem))
        if tareas and self.tarea_activa_idx > 0:
            self.tarea_activa_idx -= 1
            tareas[self.tarea_activa_idx].focus()

    # --- ACCIONES INTERACTIVAS ---

    def action_add_task(self) -> None:
        self.tarea_en_edicion = None
        input_widget = self.query_one("#input-nueva-tarea", Input)
        input_widget.placeholder = "📝 Nueva tarea: Escribe y presiona Enter..."
        input_widget.value = ""
        input_widget.visible = True
        input_widget.focus()

    def action_edit_task(self) -> None:
        focused_widget = self.focused
        if isinstance(focused_widget, TareaItem):
            self.tarea_en_edicion = focused_widget  
            input_widget = self.query_one("#input-nueva-tarea", Input)
            input_widget.placeholder = f"✏️ Editar tarea [{focused_widget.tid}]:"
            input_widget.value = focused_widget.texto
            input_widget.visible = True
            input_widget.focus()

    def action_delete_task(self) -> None:
        focused_widget = self.focused
        if isinstance(focused_widget, TareaItem):
            data = cargar_datos()
            data[focused_widget.columna].pop(focused_widget.tid)
            guardar_datos(data)
            
            # Ajustamos el índice por si borramos el último elemento de la lista
            if self.tarea_activa_idx > 0:
                self.tarea_activa_idx -= 1
                
            self.actualizar_interfaz()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        texto = event.value.strip()
        if texto:
            data = cargar_datos()
            if self.tarea_en_edicion:
                tid = self.tarea_en_edicion.tid
                col = self.tarea_en_edicion.columna
                data[col][tid] = texto
                target_id = tid
            else:
                nuevo_id = str(data["next_id"])
                data["TODO"][nuevo_id] = texto
                data["next_id"] += 1
                target_id = nuevo_id

            guardar_datos(data)
            event.input.value = ""
            event.input.visible = False
            self.tarea_en_edicion = None
            self.actualizar_interfaz(select_tid=target_id)
        else:
            event.input.visible = False
            self.tarea_en_edicion = None
            self.actualizar_interfaz()

    def action_move_task(self) -> None:
        focused_widget = self.focused
        if isinstance(focused_widget, TareaItem):
            tid = focused_widget.tid
            col_actual = focused_widget.columna
            
            mapeo_siguiente = {"TODO": "DOING", "DOING": "DONE", "DONE": "TODO"}
            col_destino = mapeo_siguiente[col_actual]
            
            data = cargar_datos()
            texto_tarea = data[col_actual].pop(tid)
            data[col_destino][tid] = texto_tarea
            guardar_datos(data)
            
            self.actualizar_interfaz(select_tid=tid)

if __name__ == "__main__":
    KanbanApp().run()
