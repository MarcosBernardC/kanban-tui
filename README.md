# 🛰️ Kanban TUI

Un tablero Kanban minimalista, ultra-rápido y elegante desarrollado nativamente para la terminal. Construido en Python utilizando el framework **Textual**, pensado para desarrolladores y entusiastas de la eficiencia que viven en la línea de comandos.

Para un repositorio impecable, recuerda colocar tu captura en `assets/kanban-screenshot.png`.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/UIFramework-Textual-005F73?style=for-the-badge&logo=terminal&logoColor=white" alt="Textual" />
  <img src="https://img.shields.io/badge/License-MIT-FFB703?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Environment-Linux%20%2F%20Fedora-E94560?style=for-the-badge&logo=fedora&logoColor=white" alt="OS" />
</p>

---

![Kanban TUI Screenshot](assets/kanban-screenshot.png)

## ✨ Características

- **Diseño Modular de Tres Columnas:** Visualiza tus flujos de trabajo de manera limpia en columnas `TODO`, `DOING` y `DONE`.
- **Numeración Cronológica Inteligente:** Olvídate de los complejos IDs globales. La TUI ordena automáticamente las tareas por fecha de creación y muestra un índice local dinámico (`[1]`, `[2]`, `[3]`).
- **Vista de Detalle e Inspección:** Presiona `Enter` para abrir un modal elegante con metadatos completos de la tarea (fecha, hora y columna actual).
- **Edición en Caliente:** Modifica el texto de tus tareas directamente desde el diálogo de inspección sin interrumpir tu flujo de trabajo.
- **Salida Segura:** Evita cierres accidentales mediante un diálogo clásico de confirmación de salida.
- **Persistencia Local Robusta:** Los datos se guardan automáticamente en un archivo `kanban.json` estructurado, incluyendo migración transparente desde formatos antiguos.

## 🚀 Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone [https://github.com/tu-usuario/kanban-tui.git](https://github.com/tu-usuario/kanban-tui.git)
cd kanban-tui
```

### 2. Configurar el entorno virtual (Recomendado)

Bash

```
python3 -m venv .venv
source .venv/bin/activate  # En Linux/Fedora
```

### 3. Instalar dependencias

Bash

```
pip install -r requirements.txt
```

### 4. Lanzar la aplicación

Bash

```
./kanban.py
```

## ⌨️ Atajos de Teclado (Keybindings)

### Tablero Principal

| **Tecla**     | **Acción**                                                   |
| ------------- | ------------------------------------------------------------ |
| `q`           | Abrir diálogo de salida                                      |
| `a`           | Añadir una nueva tarea                                       |
| `Enter` / `e` | Ver detalle e inspeccionar tarea activa                      |
| `d` / `x`     | Eliminar tarea activa                                        |
| `m`           | Mover tarea a la siguiente columna (`TODO` ➔ `DOING` ➔ `DONE`) |
| `🠔` / `h`     | Navegar a la columna izquierda                               |
| `🠖` / `l`     | Navegar a la columna derecha                                 |
| `🠗` / `j`     | Desplazar foco hacia abajo                                   |
| `🠕` / `k`     | Desplazar foco hacia arriba                                  |

### Ventanas Modales (Detalle / Salida)

| **Tecla**   | **Acción**                                                   |
| ----------- | ------------------------------------------------------------ |
| `q` / `Esc` | Cerrar el modal / Cancelar acción                            |
| `e`         | Activar edición de texto (Solo en el detalle de la tarea)    |
| `Enter`     | Confirmar guardado de texto / Confirmar salida de la aplicación |

## 🛠️ Tecnologías Utilizadas

- **Python 3.14+**
- **Textual** (Framework para interfaces de terminal enriquecidas)
- **JSON** (Almacenamiento e intercambio de datos)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. ¡Siéntete libre de clonarlo, modificarlo y adaptarlo a tus flujos de trabajo diarios!
