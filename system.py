# system.py
import pygame
import math
from utils import get_edge_point, draw_arrow

class System:
    def __init__(self, name, size=(140, 50), position=(0, 0), mass=1.0,
                 outer_boundary_radius=None, inner_boundary_radius=None):
        self.name = name
        self.size = size            # fixed rectangle size
        self.position = position    # center position (absolute)
        self.subsystems = []        # list of child System objects
        self.interactions = []      # interactions as tuples: (source, dest, verb, data)
        self.rect = None            # pygame.Rect, computed when drawn
        
        # Physics properties.
        self.mass = mass
        self.velocity = [0.0, 0.0]    # [vx, vy]
        self.acceleration = [0.0, 0.0]  # [ax, ay]
        self.net_force = [0.0, 0.0]   # net force vector
        
        # Optional boundary circles (applies for systems that contain subsystems)
        self.outer_boundary_radius = outer_boundary_radius  # external circle radius
        self.inner_boundary_radius = inner_boundary_radius  # central circle radius

    def add_subsystem(self, subsystem):
        self.subsystems.append(subsystem)

    def add_interaction(self, source_name, dest_name, verb, data):
        self.interactions.append((source_name, dest_name, verb, data))

    def layout_subsystems_circle(self, radius):
        """
        Arrange direct subsystems evenly around a circle of given radius 
        (centered at self.rect.center).
        """
        if not self.subsystems:
            return
        cx, cy = self.rect.center
        n = len(self.subsystems)
        for i, subsystem in enumerate(self.subsystems):
            angle = 2 * math.pi * i / n
            new_x = cx + radius * math.cos(angle)
            new_y = cy + radius * math.sin(angle)
            subsystem.position = (new_x, new_y)
            # Optionally, layout children of the subsystem in a smaller circle.
            subsystem.layout_subsystems_circle(radius * 0.5)

    def get_bounding_box(self):
        """Recursively compute the bounding box of self and all child subsystems.
           Returns (min_x, min_y, max_x, max_y)
        """
        if self.rect is None:
            self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
            self.rect.center = self.position
        min_x, min_y = self.rect.left, self.rect.top
        max_x, max_y = self.rect.right, self.rect.bottom
        for subsystem in self.subsystems:
            sub_min_x, sub_min_y, sub_max_x, sub_max_y = subsystem.get_bounding_box()
            min_x = min(min_x, sub_min_x)
            min_y = min(min_y, sub_min_y)
            max_x = max(max_x, sub_max_x)
            max_y = max(max_y, sub_max_y)
        return (min_x, min_y, max_x, max_y)

    def shift(self, dx, dy):
        """Shift self and all subsystems by (dx, dy)."""
        x, y = self.position
        self.position = (x + dx, y + dy)
        if self.rect:
            self.rect.move_ip(dx, dy)
        for subsystem in self.subsystems:
            subsystem.shift(dx, dy)

    def find_system(self, name):
        """Recursively find a system by name."""
        if self.name == name:
            return self
        for subsystem in self.subsystems:
            found = subsystem.find_system(name)
            if found:
                return found
        return None

    def update_physics(self, dt=1.0):
        """
        Update the physics for direct subsystems based on:
          - A force that attracts a subsystem toward the parent's center proportional to
            the number of incoming interactions.
          - A force that repels a subsystem from the parent's center proportional to
            the number of outgoing interactions.
          - Boundary collision forces.
          - Repulsive force between every pair of subsystems.
          - Attractive (spring-like) force between connected subsystems.
        """
        if not self.subsystems:
            return

        # Calculate Incoming and Outgoing Interaction Forces
        incoming_counts = {sub.name: 0 for sub in self.subsystems}
        outgoing_counts = {sub.name: 0 for sub in self.subsystems}
        for src, dest, verb, data in self.interactions:
            if dest in incoming_counts:
                incoming_counts[dest] += 1
            if src in outgoing_counts:
                outgoing_counts[src] += 1

        parent_center = self.position
        attraction_coefficient = 500.0  # coefficient for attraction (incoming)
        repulsion_coefficient = 500.0   # coefficient for repulsion (outgoing)

        for sub in self.subsystems:
            # Compute vector from subsystem to parent's center.
            vec_x = parent_center[0] - sub.position[0]
            vec_y = parent_center[1] - sub.position[1]
            d = math.hypot(vec_x, vec_y)
            if d != 0:
                ux = vec_x / d
                uy = vec_y / d
            else:
                ux, uy = 0, 0

            # Force pulling inward due to incoming interactions.
            force_incoming = attraction_coefficient * incoming_counts[sub.name]
            # Force pushing outward due to outgoing interactions.
            force_outgoing = repulsion_coefficient * outgoing_counts[sub.name]
            # Net force from parent's center.
            net_force_center = force_incoming - force_outgoing

            sub.net_force = [ux * net_force_center, uy * net_force_center]

        # Boundary Forces
        for sub in self.subsystems:
            vec_x = sub.position[0] - parent_center[0]
            vec_y = sub.position[1] - parent_center[1]
            r = math.hypot(vec_x, vec_y)
            boundary_k = 1000.0
            if self.outer_boundary_radius is not None and r > self.outer_boundary_radius:
                penetration = r - self.outer_boundary_radius
                if r != 0:
                    sub.net_force[0] -= (vec_x / r) * boundary_k * penetration
                    sub.net_force[1] -= (vec_y / r) * boundary_k * penetration
            if self.inner_boundary_radius is not None and r < self.inner_boundary_radius:
                penetration = self.inner_boundary_radius - r
                if r != 0:
                    sub.net_force[0] += (vec_x / r) * boundary_k * penetration
                    sub.net_force[1] += (vec_y / r) * boundary_k * penetration

        # Repulsive Force Between Every Pair of Direct Subsystems
        repulsion_coefficient_value = 20000000.0
        cutoff = 10000  # only apply repulsion if systems are within this distance
        n_sub = len(self.subsystems)
        for i in range(n_sub):
            for j in range(i+1, n_sub):
                sub_i = self.subsystems[i]
                sub_j = self.subsystems[j]
                dx = sub_j.position[0] - sub_i.position[0]
                dy = sub_j.position[1] - sub_i.position[1]
                d = math.hypot(dx, dy)
                if d < 1:
                    d = 1
                if d < cutoff:
                    force_magnitude = repulsion_coefficient_value / (d * d)
                    ux = dx / d
                    uy = dy / d
                    sub_i.net_force[0] -= ux * force_magnitude
                    sub_i.net_force[1] -= uy * force_magnitude
                    sub_j.net_force[0] += ux * force_magnitude
                    sub_j.net_force[1] += uy * force_magnitude

        # Attractive Force Between Connected Subsystems
        attraction_coefficient_connected = 10.0
        target_distance = 150.0
        for src, dest, verb, data in self.interactions:
            src_system = None
            dest_system = None
            for sub in self.subsystems:
                if sub.name == src:
                    src_system = sub
                if sub.name == dest:
                    dest_system = sub
            if src_system is not None and dest_system is not None:
                dx = dest_system.position[0] - src_system.position[0]
                dy = dest_system.position[1] - src_system.position[1]
                d = math.hypot(dx, dy)
                if d == 0:
                    continue
                force_magnitude = -attraction_coefficient_connected * (d - target_distance)
                ux = dx / d
                uy = dy / d
                src_system.net_force[0] -= ux * force_magnitude
                src_system.net_force[1] -= uy * force_magnitude
                dest_system.net_force[0] += ux * force_magnitude
                dest_system.net_force[1] += uy * force_magnitude

        # Integrate Physics for Each Direct Subsystem
        for sub in self.subsystems:
            sub.acceleration[0] = sub.net_force[0] / sub.mass
            sub.acceleration[1] = sub.net_force[1] / sub.mass
            sub.velocity[0] += sub.acceleration[0] * dt
            sub.velocity[1] += sub.acceleration[1] * dt
            damping = 0.9
            sub.velocity[0] *= damping
            sub.velocity[1] *= damping
            sub.position = (sub.position[0] + sub.velocity[0] * dt,
                            sub.position[1] + sub.velocity[1] * dt)

        # Recursively update physics for each subsystem.
        for sub in self.subsystems:
            sub.update_physics(dt)

    def draw(self, screen, font):
        """
        Draw self (rectangle and name), boundary circles (if defined), 
        then draw subsystems and interactions.
        """
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.rect.center = self.position

        fill_color = (180, 180, 250) if self.name == "Game" else (200, 200, 200)
        pygame.draw.rect(screen, fill_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        text_surface = font.render(self.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        # Draw boundary circles if defined.
        if self.outer_boundary_radius is not None:
            pygame.draw.circle(screen, (0, 0, 255), self.position, int(self.outer_boundary_radius), 2)
        if self.inner_boundary_radius is not None:
            pygame.draw.circle(screen, (255, 0, 0), self.position, int(self.inner_boundary_radius), 2)

        for subsystem in self.subsystems:
            subsystem.draw(screen, font)

        for src_name, dest_name, verb, data in self.interactions:
            src_system = self.find_system(src_name)
            dest_system = self.find_system(dest_name)
            if src_system and dest_system:
                vx = dest_system.position[0] - src_system.position[0]
                vy = dest_system.position[1] - src_system.position[1]
                start_edge = get_edge_point(src_system.rect, src_system.position, (vx, vy))
                end_edge = get_edge_point(dest_system.rect, dest_system.position, (-vx, -vy))
                label = f"{verb} ({data})"
                draw_arrow(screen, start_edge, end_edge, label, font)

def load_system_from_dict(data):
    """
    Recursively create a System from a dictionary.
    Expected keys:
      - name (string)
      - size (list of two numbers) [optional, default (140,50)]
      - position (list of two numbers) [optional, default (0,0)]
      - mass (number) [optional, default 1.0]
      - outer_boundary_radius (number) [optional]
      - inner_boundary_radius (number) [optional]
      - subsystems (list of system dictionaries) [optional]
      - interactions (list of [source, dest, verb, data]) [optional]
    """
    name = data.get("name")
    size = tuple(data.get("size", [140, 50]))
    position = tuple(data.get("position", [0, 0]))
    mass = data.get("mass", 1.0)
    outer_boundary_radius = data.get("outer_boundary_radius")
    inner_boundary_radius = data.get("inner_boundary_radius")
    system_obj = System(name, size=size, position=position, mass=mass,
                        outer_boundary_radius=outer_boundary_radius,
                        inner_boundary_radius=inner_boundary_radius)
    subsystems = data.get("subsystems", [])
    for sub_data in subsystems:
        sub_system = load_system_from_dict(sub_data)
        system_obj.add_subsystem(sub_system)
    interactions = data.get("interactions", [])
    for interaction in interactions:
        if len(interaction) >= 4:
            system_obj.add_interaction(interaction[0], interaction[1], interaction[2], interaction[3])
    return system_obj
