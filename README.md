# SwordArt: Procedural Dungeon Crawler

> A 2D Python-based engine demonstrating procedural content generation (PCG) using recursive division algorithms and spatial hashing for physics optimization.

## 🗺️ Project Overview
**SwordArt** is a technical implementation of a roguelike dungeon explorer. Unlike static game maps, this engine generates a unique level layout upon every execution. It features a custom **Kinematic Character Controller** utilizing vector-based movement and a directional hitbox combat system.

The project emphasizes algorithmic efficiency in map generation and entity management within the **Arcade** framework.

## 🚀 Key Features

* **Procedural Map Generation:** Implements a **Recursive Split Algorithm** to divide the game space into varying sectors and carve out non-overlapping rooms.
* **Graph Connectivity:** Automatically connects isolated rooms by calculating the Minimal Spanning Tree (logic variant) based on **Euclidean distance** between room centroids.
* **Spatial Hashing:** Utilizes `arcade.SpriteList(use_spatial_hash=True)` to reduce collision detection complexity from $O(n^2)$ to near $O(1)$ average case.
* **Directional Combat:** Dynamic hitbox calculation based on player facing direction (`RIGHT_FACING` / `LEFT_FACING`) with cooldown management.

## 🧠 Algorithmic & Mathematical Concepts

### 1. Map Generation (Recursive Division)
The dungeon is created by recursively splitting the grid $(W, H)$ into smaller sub-rectangles (leaves).
If a section is larger than the threshold (`MAX = 15`), it splits either horizontally or vertically:

$$\text{Split}(S) = \begin{cases} \text{Horizontal Cut} & \text{if } H > W \\ \text{Vertical Cut} & \text{if } W > H \\ \text{Random} & \text{otherwise} \end{cases}$$

### 2. Room Connectivity
To connect rooms $R_1$ and $R_2$, the engine calculates the Euclidean distance between their centers $(x_1, y_1)$ and $(x_2, y_2)$ to find the closest neighbors:

$$d(R_1, R_2) = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$

### 3. Hitbox Logic (AABB)
The combat system generates a temporary Axis-Aligned Bounding Box (AABB) offset by the player's position. For a generic attack range $r$:
* **Right Attack:** $[x, x+r]$
* **Left Attack:** $[x-r, x]$

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Core Library:** [Python Arcade](https://api.arcade.academy/) (Modern OpenGL context).
* **Concepts:** Recursion, Matrix Manipulation, Collision Physics.

## 💻 Installation & Usage

1.  **Install Dependencies:**
    ```bash
    pip install arcade
    ```

2.  **Run the Engine:**
    ```bash
    python main.py
    ```
---
**Author:** [Johan Caro]
*Applied Mathematics & Computer Science Student*
