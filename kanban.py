#!/usr/bin/env python3
import json
import os
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Label, Input, Button
from textual.binding import Binding
from textual.screen import ModalScreen

DATA_FILE = "kanban.json"
DEFAULT_DATA = {"next_id": 1, "TODO": {}, "DOING": {}, "DONE": {}}

def cargar_datos():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, indent=4)
        return DEFAULT_DATA
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    modificado = False
    for col in ["TODO", "DOING", "DONE"]:
        for tid, contenido in list(data[col].items()):
            if isinstance(contenido, str):
                data[col][tid] = {
                    "texto": contenido,
                    "creado": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                modificado = True
    if modificado:
        guardar_datos(data)
    
    return data

def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


class ConfirmarSalidaModal(ModalScreen):
    """Ventana emergente clásica para confirmar la salida de la aplicación."""
    
    DEFAULT_CSS = """
    ConfirmarSalidaModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #confirmar-contenedor {
        width: 45;
        height: auto;
        border: thick #e60000;
        background: $surface;
        padding: 1 2;
    }

    #confirmar-titulo {
        text-align: center;
        text-style: bold;
        color: #ff3333;
        margin-bottom: 1;
    }

    #confirmar-botones {
        margin-top: 1;
        height: auto;
        align: center middle;
    }

    .btn-confirmar {
        margin: 0 1;
        width: 14;
    }
    """

    BINDINGS = [
        Binding("escape,q", "cancelar", "Regresar", show=True)
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="confirmar-contenedor"):
            yield Label("⚠️ ¿Estás seguro de que deseas salir?", id="confirmar-titulo")
            with Horizontal(id="confirmar-botones"):
                yield Button("Salir (Enter)", variant="error", id="btn-salir", classes="btn-confirmar")
                yield Button("Cancelar", variant="primary", id="btn-cancelar", classes="btn-confirmar")

    def on_mount(self) -> None:
        # Enfocamos el botón de salir por defecto para agilizar con un Enter rápido
        self.query_one("#btn-salir", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-salir":
            self.dismiss(True)
        elif event.button.id == "btn-cancelar":
            self.dismiss(False)

    def action_cancelar(self) -> None:
        self.dismiss(False)


class DetalleTareaModal(ModalScreen):
    """Ventana emergente elegante para visualizar metadatos, fecha y editar."""
    
    DEFAULT_CSS = """
    DetalleTareaModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }

    #modal-contenedor {
        width: 65;
        height: auto;
        border: thick #268bd2;
        background: $surface;
        padding: 1 2;
    }

    #modal-titulo {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: #7cfc00;
    }

    .modal-meta-linea {
        margin-bottom: 0;
        height: auto;
    }

    .meta-etiqueta {
        color: $text-muted;
    }

    .meta-valor {
        text-style: bold;
        color: $text;
    }

    #modal-texto-lectura {
        margin: 1 0;
        height: auto;
        min-height: 3;
        max-height: 10;
        overflow-y: scroll;
        border: round $primary-darken-3;
        padding: 1;
        background: $background;
    }

    #modal-input-edicion {
        margin: 1 0;
        border: tall #268bd2;
        background: $background;
        width: 1fr;
    }

    #modal-botones {
        margin-top: 1;
        height: auto;
        align: center middle;
    }

    .btn-modal {
        margin: 0 1;
        width: 16;
    }
    """

    BINDINGS = [
        Binding("escape,q", "custom_close", "Cerrar", show=True),
        Binding("e", "activar_edicion", "Editar Texto", show=True),
    ]

    def __init__(self, tid: str, indice_visual: int, texto: str, columna: str, creado: str, app_callback):
        super().__init__()
        self.tid = tid
        self.indice_visual = indice_visual
        self.texto = texto
        self.columna = columna
        self.creado = creado
        self.app_callback = app_callback
        self.editando = False

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-contenedor"):
            yield Label(f"🛰️ DETALLE DE TAREA [{self.indice_visual}]", id="modal-titulo")
            
            with Horizontal(classes="modal-meta-linea"):
                yield Label("📍 Columna: ", classes="meta-etiqueta")
                yield Label(f"{self.columna}", classes="meta-valor")
            
            with Horizontal(classes="modal-meta-linea", id="meta-fecha"):
                yield Label("📅 Creado el: ", classes="meta-etiqueta")
                yield Label(f"{self.creado}", classes="meta-valor")
            
            yield Static(self.texto, id="modal-texto-lectura")
            
            with Horizontal(id="modal-botones"):
                yield Button("Cerrar (q)", variant="primary", id="btn-accion-principal", classes="btn-modal")

    def on_mount(self) -> None:
        self.focus()

    def action_activar_edicion(self) -> None:
        if self.editando:
            return

        self.editando = True
        
        lectura_widget = self.query_one("#modal-texto-lectura")
        lectura_widget.remove()

        nuevo_input = Input(value=self.texto, id="modal-input-edicion")
        self.query_one("#modal-contenedor").mount(nuevo_input, after="#meta-fecha")
        
        btn = self.query_one("#btn-accion-principal", Button)
        btn.label = "Guardar"
        btn.variant = "success"
        
        nuevo_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-accion-principal":
            if self.editando:
                self.procesar_guardado()
            else:
                self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "modal-input-edicion":
            self.procesar_guardado()

    def procesar_guardado(self) -> None:
        nuevo_texto = self.query_one("#modal-input-edicion", Input).value.strip()
        if nuevo_texto:
            self.app_callback(self.tid, self.columna, nuevo_texto)
        self.dismiss()

    def action_custom_close(self) -> None:
        self.dismiss()


class TareaItem(Static):
    """Widget de tarea interactivo con índice secuencial de interfaz."""
    can_focus = True  

    def __init__(self, tid: str, indice_visual: int, texto: str, columna: str, creado: str, **kwargs):
        super().__init__(**kwargs)
        self.tid = tid
        self.indice_visual = indice_visual
        self.texto = texto
        self.columna = columna
        self.creado = creado

    def compose(self) -> ComposeResult:
        texto_preview = self.texto if len(self.texto) <= 20 else f"{self.texto[:17]}..."
        yield Label(f"[b][#7cfc00][{self.indice_visual}][/][/b] {texto_preview}")


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

    # Cambiamos la acción directa de 'quit' por nuestra propia acción controlada 'confirmar_salida'
    BINDINGS = [
        Binding("q", "confirmar_salida", "Salir", show=True),
        Binding("a", "add_task", "Añadir", show=True),
        Binding("enter,e", "abrir_modal_tarea", "Ver Detalle", show=True),
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
            
            tareas_columna = list(data[col_name.upper()].items())
            
            try:
                tareas_columna.sort(key=lambda x: datetime.strptime(x[1]["creado"], "%d/%m/%Y %H:%M"))
            except Exception:
                pass 

            for idx, (tid, info) in enumerate(tareas_columna, start=1):
                item = TareaItem(tid, idx, info["texto"], col_name.upper(), info["creado"])
                container.mount(item)
                
                if select_tid and select_tid == tid:
                    target_widget = item
                    self.col_activa_idx = self.columnas_lista.index(col_name)
                    self.tarea_activa_idx = idx - 1

        if target_widget:
            self.call_after_refresh(target_widget.focus)
        else:
            self.call_after_refresh(self._refrescar_foco)

    def _refrescar_foco(self) -> None:
        col_name = self.columnas_lista[self.col_activa_idx]
        container = self.query_one(f"#tasks-{col_name}", VerticalScroll)
        text_tasks = list(container.query(TareaItem))
        
        if text_tasks:
            self.tarea_activa_idx = min(self.tarea_activa_idx, len(text_tasks) - 1)
            if self.tarea_activa_idx < 0:
                self.tarea_activa_idx = 0
            text_tasks[self.tarea_activa_idx].focus()
        else:
            self.tarea_activa_idx = 0
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

    # --- ACCIÓN DE SALIDA CONTROLADA ---

    def action_confirmar_salida(self) -> None:
        """Despliega el modal de confirmación y evalúa la respuesta."""
        def chequear_resultado(debe_salir: bool) -> None:
            if debe_salir:
                self.exit()

        self.push_screen(ConfirmarSalidaModal(), chequear_resultado)

    # --- FLUJO DEL MODAL DE DETALLE ---

    def action_abrir_modal_tarea(self) -> None:
        focused_widget = self.focused
        if isinstance(focused_widget, TareaItem):
            self.push_screen(DetalleTareaModal(
                tid=focused_widget.tid,
                indice_visual=focused_widget.indice_visual,
                texto=focused_widget.texto,
                columna=focused_widget.columna,
                creado=focused_widget.creado,
                app_callback=self.guardar_cambios_tarea
            ))

    def guardar_cambios_tarea(self, tid: str, columna: str, nuevo_texto: str) -> None:
        data = cargar_datos()
        data[columna][tid]["texto"] = nuevo_texto
        guardar_datos(data)
        self.actualizar_interfaz(select_tid=tid)

    # --- ACCIONES RÁPIDAS ---

    def action_add_task(self) -> None:
        input_widget = self.query_one("#input-nueva-tarea", Input)
        input_widget.placeholder = "📝 Nueva tarea: Escribe y presiona Enter..."
        input_widget.value = ""
        input_widget.visible = True
        input_widget.focus()

    def action_delete_task(self) -> None:
        focused_widget = self.focused
        if isinstance(focused_widget, TareaItem):
            data = cargar_datos()
            data[focused_widget.columna].pop(focused_widget.tid)
            guardar_datos(data)
            if self.tarea_activa_idx > 0:
                self.tarea_activa_idx -= 1
            self.actualizar_interfaz()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input-nueva-tarea":
            texto = event.value.strip()
            if texto:
                data = cargar_datos()
                nuevo_id = str(data["next_id"])
                
                data["TODO"][nuevo_id] = {
                    "texto": texto,
                    "creado": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                data["next_id"] += 1
                guardar_datos(data)
                
                event.input.value = ""
                event.input.visible = False
                self.actualizar_interfaz(select_tid=nuevo_id)
            else:
                event.input.visible = False
                self.actualizar_interfaz()

    def action_move_task(self) -> None:
        focused_widget = self.focused
        if isinstance(focused_widget, TareaItem):
            tid = focused_widget.tid
            col_actual = focused_widget.columna
            
            mapeo_siguiente = {"TODO": "DOING", "DOING": "DONE", "DONE": "TODO"}
            col_destino = mapeo_siguiente[col_actual]
            
            data = cargar_datos()
            objeto_tarea = data[col_actual].pop(tid)
            data[col_destino][tid] = objeto_tarea
            guardar_datos(data)
            
            self.actualizar_interfaz(select_tid=tid)

if __name__ == "__main__":
    KanbanApp().run()
