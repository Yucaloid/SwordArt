# ⚔️ SwordArt: Procedural Dungeon Crawler

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Arcade](https://img.shields.io/badge/Library-Arcade-red?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Refactored-success?style=for-the-badge)

Bienvenido a **SwordArt**, un juego de exploración de mazmorras (Dungeon Crawler) generado procedimentalmente y desarrollado en Python utilizando la librería `arcade`.

Este repositorio es un híbrido entre un archivo histórico y un proyecto moderno: contiene tanto la versión original (**Legacy**) con la que aprendí a programar, como una versión modernizada (**Refactored**) adaptada a los estándares actuales.

---

## 📜 Nota del Autor

> *"Este fue mi primer proyecto de desarrollo de videojuegos. He decidido mantener el código original (`SwordArt.py`) en el repositorio por el cariño que le tengo y para recordar mis inicios, aunque utilice una versión de la librería que ya no es el estándar. Si eres nuevo probando el juego, te sugiero usar la versión `arcade3`. Mis otros 2 compañeros aunque estuvieron en el inicio del proyecto no siguieron en el pero sus nombres se conservan en la imagen de menu"*

---

## 📂 Versiones del Proyecto

Debido a los cambios estructurales mayores ("breaking changes") en la librería `arcade` (entre v2.6 y v3.0), no es posible ejecutar ambos scripts en el mismo entorno sin ajustar las dependencias.

| Archivo | Versión Arcade | Estado | Descripción |
| :--- | :---: | :---: | :--- |
| **`SwordArt_arcade3.py`** | **v3.0+** | ✅ Recomendado | **Versión Refactorizada.** Incluye cámaras modernas, renderizado optimizado y un sistema de generación de mapas mejorado con túneles conectados. |
| `SwordArt.py` | v2.5.x / v2.6 | 🏛️ Legacy | **Versión Original.** Se conserva el código intacto por valor histórico y sentimental. Requiere una versión antigua de la librería. |

---

## 🛠️ Tecnologías y Algoritmos

El núcleo del proyecto se basa en la generación procedural para garantizar que ninguna partida sea igual a la anterior.

* **Lenguaje:** Python 3
* **Motor Gráfico:** Python Arcade Library
* **Algoritmo Principal:** [Binary Space Partitioning (BSP)](https://es.wikipedia.org/wiki/Partici%C3%B3n_binaria_del_espacio).
    * El mapa utiliza una estructura de árbol para dividir el espacio recursivamente.
    * Se generan habitaciones en las hojas del árbol y se conectan mediante pasillos para crear la mazmorra jugable.

---

## 🚀 Instalación y Ejecución

⚠️ **Advertencia:** Se recomienda encarecidamente usar **Entornos Virtuales** (`venv`) si deseas alternar entre versiones, para evitar conflictos de dependencias.

### 🟢 Opción A: Versión Moderna (Recomendada)
Utiliza las características más recientes de Python y Arcade.

1. **Instalar dependencias:**
   ```bash
   pip install arcade
   ```
2. **Ejecutar el juego:**
   ```bash
   python SwordArt_arcade3.py
   ```

### 🟠 Opción B: Versión Legacy (Histórica)
Para experimentar el proyecto tal como fue concebido originalmente, es necesario hacer un "downgrade" de la librería a la serie 2.x.

1. **Instalar versión compatible:**
   ```bash
   pip install "arcade==2.6.17"
   ```
   *(Nota: También compatible con versiones 2.5.x)*

2. **Ejecutar el juego:**
   ```bash
   python SwordArt.py
   ```

---

## 🎮 Controles

El esquema de control es clásico y sencillo:

| Tecla | Acción |
| :---: | :--- |
| **Flechas / WASD** | Mover al personaje por la mazmorra |
| **Z / X** | Atacar (Stab / Golpe) |
| **ESC** | Pausar / Salir |

---

Made with ❤️ & Python.
