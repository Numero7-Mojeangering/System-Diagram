# Summary

This project renders a system functional architecture defined in a json file.

We are using a **time-step simulation** to move the subsystems.

---

- **Example:**  
  A "Game" system with its subsystems (e.g., "Physics Engine", "Rendering Engine", etc.). These systems interact through defined relationships (e.g., "provides", "modifies", "synchronizes").

---

## File Breakdown

### `utils.py`

- **Utility Functions:**
  - **`get_edge_point(rect, center, direction)`**  
    Computes the intersection point on the edge of a rectangle in a specified direction from its center.
    
  - **`draw_arrow(screen, start, end, text, font, color)`**  
    Draws an arrow between two points with a label placed at the midpoint. The arrowhead is created using a small polygon based on the line's angle.

---

### `system.py`

- **`System` Class:**  
  Represents a system or subsystem in the architecture. Each instance stores its:
  - **Attributes:**
    - **Name, Size, and Position:**  
      Define the visual appearance and location of the system.
    - **Physics Properties:**  
      Includes mass, velocity, acceleration, and net force for simulating movement.
    - **Hierarchy:**  
      Contains lists of child subsystems and interaction definitions.
    - **Boundaries:**  
      Outer and inner boundary circles.
  
- **Key Methods:**
  - **`add_subsystem()` / `add_interaction()`:**  
    Build the hierarchical structure and define relationships between systems.
  
  - **`layout_subsystems_circle(radius)`:**  
    Positions direct subsystems evenly around a circle (centered at the parent system’s center) with a specified radius. This method also recursively applies a smaller circle layout to any child subsystems.
  
  - **`get_bounding_box()`:**  
    Recursively calculates the overall bounding box of a system and its descendants. This is used to adjust the canvas size so all content is visible.
  
  - **`shift(dx, dy)`:**  
    Shifts the system (and all its child systems) by a given offset. This is used after computing the bounding box to ensure a margin around the displayed content.
  
  - **`find_system(name)`:**  
    Recursively searches the system hierarchy for a system with a given name.
  
  - **`update_physics(dt)`:**  
    Simulates forces and updates movement by:
    - Calculating **incoming** and **outgoing** interaction counts for each direct subsystem.
    - Applying a force that **attracts** a subsystem toward the parent’s center (based on incoming interactions) and a force that **repels** it (based on outgoing interactions).
    - Incorporating **boundary forces** that push subsystems inward if they exceed the outer boundary and push them outward if they are too close to the central boundary.
    - Computing **repulsive forces** between every pair of direct subsystems to prevent overlap.
    - Applying **spring-like attractive forces** between connected subsystems to maintain a target separation.
    - Integrating the net force over time (with damping) to update each subsystem’s velocity and position.
  
  - **`draw(screen, font)`:**  
    Draws the system as a rectangle with its name centered. If boundary circles are defined, they are drawn as well. It then recursively calls `draw()` on its subsystems and uses utility functions to render arrows for each defined interaction.

- **Helper Function:**  
  - **`load_system_from_dict(data)`**  
    Recursively creates a `System` object (and its hierarchy) from a dictionary loaded from JSON.

---

### `main.py`

- **Main Functionality:**  
  This file is the entry point of the application:
  - Initializes Pygame and creates a font.
  - Loads the architecture from the `architecture.json` file using the helper function from `system.py`.
  - Prepares the top-level "Game" system for display by setting up its rectangle, and then calls `layout_subsystems_circle(150)` to arrange its direct subsystems.
  - Computes the bounding box of the entire hierarchy to determine the required canvas size and applies a shift so that all content is visible with a margin.
  - Sets up the main Pygame window and enters the simulation loop, where:
    - **Physics are updated** each frame (using the defined forces and integration).
    - **Systems are drawn** on the screen, including visual representations of interactions via arrows.
    - The display is refreshed, and the loop continues until the user quits.

---

### `architecture.json`

- **Structure:**  
  This file defines the hierarchy of systems. For example:
  - The top-level system is named "Game" and contains properties such as size and position.
  - It includes an array of subsystems (like "Physics Engine", "Rendering Engine", etc.) with their own sizes.
  - An interactions array defines relationships between systems. Each interaction is a list that includes the source system, destination system, a verb describing the interaction, and additional data (e.g., "movement & collision data").

---

## Simulation Flow

1. **Loading and Initialization:**
   - The program starts by loading the architecture from a JSON file.
   - The hierarchy is built using `load_system_from_dict()`, which creates a nested structure of `System` objects.
   - The top-level system is prepared for display (positioned, its rectangle is defined, and its direct subsystems are laid out in a circle).

2. **Dynamic Adjustment:**
   - The bounding box of the entire hierarchy is computed to determine how large the Pygame canvas needs to be.
   - The system is shifted so that everything is visible within the window with an appropriate margin.

3. **Main Loop (Simulation):**
   - **Physics Update:**  
     Forces based on interactions, boundaries, and subsystem relationships are computed and integrated.
   - **Drawing:**  
     The updated positions are rendered on the screen, showing the systems, their boundaries, and interaction arrows.
   - The simulation continues until the user quits.


