#!/home/bernardc/dev/ActiveLabs/kanban-tui/.venv/bin/python
import json
import os
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Label, Input, TextArea
from textual.screen import ModalScreen
from textual.binding import Binding

#DATA_FILE = "kanban.json"
DEFAULT_DATA = {"next_id": 1, "TODO": {}, "DOING": {}, "DONE": {}}

def get_data_path():
    # 1. Intentar buscar en el directorio donde el usuario ejecuta el comando
    cwd_path = os.path.join(os.getcwd(), "kanban.json")
    if os.path.exists(cwd_path):
        return cwd_path
    
    # 2. Si no existe, usar el directorio donde vive el script (comportamiento actual)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "kanban.json")

def cargar_datos():
    path = get_data_path()
    if not os.path.exists(path):
        # Crear archivo vacío si no existe
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, indent=4)
        return DEFAULT_DATA
    
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # En caso de corrupción, retornar el default
            return DEFAULT_DATA

def guardar_datos(data):
    with open(get_data_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class TareaItem(Static):
    can_focus = True
    def __init__(self, tid, info, col):
        super().__init__()
        self.tid = tid
        self.info = info
        self.columna = col
    
    def compose(self) -> ComposeResult:
        # Extraemos la fecha con un valor por defecto si no existe
        fecha = self.info.get('creado', 'sin fecha')
        yield Label(f"[b][{self.tid}][/b] {self.info['texto'][:20]}")
        yield Label(f"[dim]{fecha}[/]", classes="fecha-label")

class ConfirmacionModal(ModalScreen):
    BINDINGS = [Binding("s", "confirmar", "Sí"), Binding("n", "cancelar", "No")]
    def __init__(self, mensaje):
        super().__init__()
        self.mensaje = mensaje
    def compose(self) -> ComposeResult:
        yield Vertical(Label(self.mensaje), Label("[b]S[/]: Sí | [b]N[/]: No"), id="modal-box")
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

class AyudaModal(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss", "Cerrar"), Binding("q", "dismiss", "Cerrar")]

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label("[b]PANEL DE AYUDA[/b]", id="modal-title")
            yield Static("--- NAVEGACIÓN ---\n"
                         "h/j/k/l: Mover selección\n"
                         "H/L: Mover tarea entre columnas\n"
                         "J/K: Reordenar tarea arriba/abajo\n\n"
                         "--- ACCIONES ---\n"
                         "Enter: Editar tarea\n"
                         "a: Añadir tarea\n"
                         "d: Borrar tarea\n"
                         "t: Alternar tema (ansi-light/flexoki)\n"
                         "q: Salir de la app\n\n"
                         "--- EN MODO EDICIÓN ---\n"
                         "i: Insertar | Esc: Normal\n"
                         ":: Comandos (:w, :wq, :q)")
            yield Label("\nPresiona [b]Esc[/] o [b]q[/] para cerrar.")

class NuevaTareaModal(ModalScreen):
    BINDINGS = [
        Binding("i", "insertar", "Insertar"),
        Binding("escape", "modo_normal", "Normal"),
        Binding("colon", "activar_comandos", ":"),
        Binding("enter", "guardar_y_salir", "Guardar"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label("Nueva Tarea", id="modal-title")
            self.text_area = TextArea(text="", id="edit-input")
            self.text_area.read_only = True
            yield self.text_area
            
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
        self.cmd_input.value = "" # Limpiamos el input
        self.info_label.update("-- NORMAL -- | i: Insertar | : Comandos")
        self.text_area.focus()

    def action_activar_comandos(self):
        self.cmd_input.display = True
        self.cmd_input.focus()
        self.cmd_input.value = ""

    def action_guardar_y_salir(self):
        # Esta acción ahora es el núcleo del guardado
        texto = self.text_area.text.strip()
        if texto:
            self.dismiss(texto) # Retorna el texto a la App principal
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "cmd-line":
            cmd = event.value.strip()
            if cmd == "q":
                self.dismiss(None)
            elif cmd in ["w", "wq"]:
                # :w y :wq funcionan igual aquí (guardan y cierran)
                self.action_guardar_y_salir()
            else:
                self.action_modo_normal()

class RepoCheckModal(ModalScreen):
    # Definimos los bindings para que Textual los gestione automáticamente
    BINDINGS = [
        Binding("s", "confirmar", "Sí"), 
        Binding("n", "cancelar", "No")
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label("No es un repositorio Git.\n¿Generar lista de tareas aquí?", id="modal-title")
            yield Label("[b]S[/]: Sí | [b]N[/]: No")

    def action_confirmar(self):
        self.dismiss(True)

    def action_cancelar(self):
        self.dismiss(False)

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
    #modal-box Static {
        padding: 1;
        width: 100%;
        text-align: left;
    }
    Footer {
        height: 1;
        background: $surface-darken-1;
        /* Eliminamos font-size: 80%; que causa el error */
    }

    /* Opcional: reducir el espacio entre elementos del footer */
    Footer > .footer--key {
        padding: 0 1; 
    }
    .fecha-label {
        text-align: right;
        padding-right: 1;
        width: 100%;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("t", "toggle_theme", "Cambiar Tema"),
        Binding("q", "quit", "Salir"),
        Binding("?", "mostrar_ayuda", "Ayuda"),
        Binding("enter", "entrar_tarjeta", "Editar"),
        # Navegación base visible en el footer
        Binding("h", "move_left", "←"),
        Binding("l", "move_right", "→"),
        Binding("j", "move_down", "↓"),
        Binding("k", "move_up", "↑"),
        
        # Acciones ocultas del footer para limpiar la interfaz
        Binding("J", "move_task_down", "Mover ↓", show=False),
        Binding("K", "move_task_up", "Mover ↑", show=False),
        Binding("H", "move_task_left", "Mover ←", show=False),
        Binding("L", "move_task_right", "Mover →", show=False),

        Binding("a", "añadir_tarea", "Añadir"),
        Binding("d", "delete_task", "Borrar", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.columnas = ["TODO", "DOING", "DONE"]
        self.col_idx = 0

    def action_toggle_theme(self):
        """Alterna entre ansi-light y flexoki"""
        # Cambiamos directamente self.theme (que es la propiedad oficial de Textual)
        self.theme = "flexoki" if self.theme == "ansi-light" else "ansi-light"
        self.notify(f"Tema cambiado a: {self.theme}")
    
    def action_delete_task(self):
        focused = self.screen.focused
        if not isinstance(focused, TareaItem):
            return

        def confirmar_borrado(confirmado):
            if confirmado:
                data = cargar_datos()
                col = focused.columna
                tid = int(focused.tid) # Convertimos a int para comparar
                
                # Eliminamos la tarea
                if str(tid) in data[col]:
                    del data[col][str(tid)]
                    
                    # Lógica para ajustar next_id
                    # Solo restamos si el ID eliminado era el último creado (next_id - 1)
                    if tid == data["next_id"] - 1:
                        data["next_id"] -= 1
                    
                    guardar_datos(data)
                    self.actualizar_tablero()
                    self.notify(f"Tarea {tid} eliminada y next_id actualizado")

        self.push_screen(ConfirmacionModal(f"¿Borrar tarea #{focused.tid}?"), confirmar_borrado)
    
    def action_añadir_tarea(self):
        def procesar_nueva_tarea(texto):
            if texto:
                data = cargar_datos()
                tid = str(data["next_id"])
                data["next_id"] += 1
                col_actual = self.columnas[self.col_idx]
                
                # Obtenemos fecha actual
                fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
                # Guardar en JSON incluyendo la clave "creado"
                data[col_actual][tid] = {
                    "texto": texto,
                    "creado": fecha_actual
                }
                guardar_datos(data)
                self.actualizar_tablero()
                self.notify(f"Tarea {tid} añadida en {col_actual}")

        self.push_screen(NuevaTareaModal(), procesar_nueva_tarea)
    
    def action_mostrar_paleta(self):
        # Puedes crear un modal simple que contenga un Input
        # y una lista de opciones ejecutables.
        self.notify("Funcionalidad de Palette en desarrollo")
    
    def on_mount(self) -> None:
        # Verificamos si estamos en un repo Git
        if not os.path.isdir(".git"):
            self.push_screen(RepoCheckModal(), self._handle_repo_check)
        else:
            self.theme = "ansi-light"
            self.actualizar_tablero()

    def _handle_repo_check(self, result: bool):
        if result:
            # Si dice que sí, inicializamos el archivo
            if not os.path.exists(get_data_path()):
                guardar_datos(DEFAULT_DATA)
            self.theme = "ansi-light"
            self.actualizar_tablero()
        else:
            # Si dice que no, salimos de la app
            self.exit()

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
    def action_mostrar_ayuda(self):
        self.push_screen(AyudaModal())

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

    def action_move_task_left(self):
        self._mover_entre_columnas(-1)

    def action_move_task_right(self):
        self._mover_entre_columnas(1)

    def _mover_entre_columnas(self, delta):
        focused = self.screen.focused
        if not isinstance(focused, TareaItem):
            return

        col_actual = focused.columna
        col_actual_idx = self.columnas.index(col_actual)
        col_destino_idx = col_actual_idx + delta

        # Verificar si el movimiento es posible
        if 0 <= col_destino_idx < len(self.columnas):
            col_destino = self.columnas[col_destino_idx]
            data = cargar_datos()
            
            # Extraer tarea
            tarea_id = str(focused.tid)
            tarea_info = data[col_actual].pop(tarea_id)
            
            # Insertar en nueva columna
            data[col_destino][tarea_id] = tarea_info
            guardar_datos(data)
            
            # Actualizar estado y UI
            self.col_idx = col_destino_idx
            self.actualizar_tablero()
            
            # Enfocar la tarea en la nueva ubicación
            def enfocar_en_nueva_col():
                tareas = self.query(f"#tasks-{col_destino} TareaItem")
                # Buscamos la tarea por ID en la nueva columna
                tarea_nueva = next((t for t in tareas if str(t.tid) == tarea_id), None)
                if tarea_nueva:
                    tarea_nueva.focus()
                    tarea_nueva.scroll_visible()
            
            self.call_after_refresh(enfocar_en_nueva_col)
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
