# 🛰️ KANBAN TUI

Un tablero Kanban interactivo para la terminal, minimalista, ultra ligero y de alto rendimiento. Construido nativamente en Python usando `curses`, sincronizado automáticamente con el fondo nativo de tu terminal y optimizado con una paleta de colores extendida de 256 tonos.

## ✨ Características

- **Diseño Nativo Eficiente:** Funciona directamente sobre el buffer de tu terminal sin dependencias externas pesadas ni entornos complejos.
- **Paleta de Colores Curada:** Sintonizado específicamente para terminales con un flujo de maduración visual armónico (`104` Morado/Rosa Pastel para TODO, `12` Celeste Foco para DOING, y `107` Verde Menta para DONE).
- **Persistencia de Datos Atómica:** Estado guardado en un archivo local plano `kanban.json` que se actualiza en tiempo real con cada interacción.
- **Navegación Fluida:** Atajos de teclado intuitivos inspirados en los movimientos nativos de Vim (`h`, `j`, `k`, `l`).

## 🛠️ Requisitos e Instalación

### Requisitos
- Python 3.x
- Módulo nativo `curses` (incluido por defecto en sistemas Unix como Fedora, CachyOS, Ubuntu, macOS).

### Instalación
1. Clona este repositorio o copia el archivo ejecutable en tu directorio de herramientas locales:
   ```bash
   git clone git@github.com:MarcosBernardC/kanban-tui.git
   cd kanban-tui

2. Asegúrate de que el script tenga permisos de ejecución:
	Bash
    ```
    chmod +x kanban.py
    ```

## 🎮 Modo de Uso

Lanza la interfaz ejecutando directamente el script:
    ```bash
    ./kanban.py
    ```

### Atajos de Teclado (Navegación e Interacción)

| **Tecla**   | **Acción**                                                   |
| ----------- | ------------------------------------------------------------ |
| `h` / `←`   | Moverse a la columna de la izquierda.                        |
| `l` / `→`   | Moverse a la columna de la derecha.                          |
| `j` / `↓`   | Desplazar el cursor hacia abajo en la lista de tareas.       |
| `k` / `↑`   | Desplazar el cursor hacia arriba en la lista de tareas.      |
| `a`         | **Añadir** una nueva tarea en la columna `TODO`.             |
| `e`         | **Editar** el texto de la tarea actualmente seleccionada.    |
| `m`         | **Mover** (ciclar) la tarea seleccionada a la siguiente columna (`TODO` ➔ `DOING` ➔ `DONE`). |
| `q` / `ESC` | **Salir** de la aplicación con gracia conservando el estado del terminal. |

## 🗄️ Estructura de Almacenamiento

El programa autogenera un archivo plano `kanban.json` en el mismo directorio con una estructura limpia estructurada por índices indexables:

JSON

```json
{
    "next_id": 2,
    "TODO": {},
    "DOING": {
        "1": "hola"
    },
    "DONE": {}
}
```

## 🎨 Personalización Visual

Si deseas experimentar con otros tonos de la terminal, puedes modificar las líneas de inicialización de color dentro de `kanban.py` usando cualquier código de escape de la paleta de 256 colores:

Python

```python
curses.init_pair(1, 104, -1) # Columna TODO
curses.init_pair(2, 12, -1)  # Columna DOING
curses.init_pair(3, 107, -1) # Columna DONE
```

## 📝 Licencia

Este proyecto es de uso personal bajo la filosofía de software libre "Haz lo que quieras con él" (MIT/WTFPL). Creado para potenciar el estado de flujo diario desde la línea de comandos.
