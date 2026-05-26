# 🛰️ Kanban TUI

Un tablero Kanban minimalista, de alta velocidad y rendimiento, diseñado para ejecutarse nativamente en la terminal. Construido en Python bajo el framework **Textual**, esta TUI está optimizada para desarrolladores que priorizan la eficiencia y el control mediante el teclado.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/UIFramework-Textual-005F73?style=for-the-badge&logo=terminal&logoColor=white" alt="Textual" />
  <img src="https://img.shields.io/badge/License-MIT-FFB703?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Environment-Linux%20%2F%20Fedora-E94560?style=for-the-badge&logo=fedora&logoColor=white" alt="OS" />
</p>

## ✨ Características Principales

- **Interfaz Basada en Modos:** Navegación fluida inspirada en Vim para gestionar tareas sin tocar el mouse.
- **Gestión de Flujo (Vim-Style):**
  - **Reordenamiento:** Usa `J` y `K` para ajustar la prioridad de tareas en tiempo real.
  - **Transferencia:** Usa `H` y `L` para migrar tareas entre estados (`TODO` ➔ `DOING` ➔ `DONE`) instantáneamente.
- **Persistencia Atómica:** Datos gestionados mediante `kanban.json` con auto-guardado seguro a través de comandos internos (`:w`, `:wq`).
- **Inspección Profunda:** Modal de edición con modo *Insertar* y *Normal*, brindando un control preciso sobre el contenido de tus tareas.

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio

Bash

```
git clone https://github.com/MarcosBernardC/kanban-tui
cd kanban-tui
```

### 2. Configurar entorno

Bash

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Lanzar la aplicación

Puedes ejecutarla directamente o darle permisos de ejecución:

Bash

```
chmod +x kanban.py
./kanban.py
```

## ⌨️ Atajos de Teclado (Keybindings)

### Tablero Principal

| **Tecla** | **Acción**                      |
| --------- | ------------------------------- |
| `q`       | Salir de la aplicación          |
| `a`       | Añadir nueva tarea              |
| `d`       | Eliminar tarea activa           |
| `Enter`   | Entrar en modo edición de tarea |
| `h` / `l` | Mover foco entre columnas       |
| `j` / `k` | Desplazar foco verticalmente    |
| `H` / `L` | Mover tarea entre columnas      |
| `J` / `K` | Reordenar tarea (arriba/abajo)  |

### Modo Edición (Modales)

| **Tecla** | **Acción**                |
| --------- | ------------------------- |
| `i`       | Entrar en modo insertar   |
| `Esc`     | Volver a modo normal      |
| `:`       | Activar línea de comandos |
| `:w`      | Guardar cambios           |
| `:wq`     | Guardar y cerrar modal    |
| `:q`      | Cerrar sin guardar        |

## 🛠️ Tecnologías

- **Python 3.14+**
- **Textual:** Framework para TUI enriquecida.
- **JSON:** Capa de persistencia local.

## 📄 Licencia

MIT. Adaptado para flujos de trabajo de ingeniería de software.
