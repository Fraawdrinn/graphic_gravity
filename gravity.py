import pymunk
import pygame
from pygame.locals import QUIT
import math

# Initialize pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
dt = 1/60.0

# Create a pymunk space (world)
space = pymunk.Space()
space.gravity = (0, 900)  # Gravity acting downwards

def create_ball(space, position, radius=20, mass=1):
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.9
    shape.friction = 0.1
    space.add(body, shape)
    return shape

def create_circular_ground(space, body, radius, num_segments=32, bouncy=15, opening_size=4):
    segment_angle = 2 * math.pi / num_segments
    ground_shapes = []

    for i in range(num_segments - opening_size):
        angle1 = i * segment_angle
        angle2 = (i + 1) * segment_angle
        p1 = (radius * math.cos(angle1), radius * math.sin(angle1))
        p2 = (radius * math.cos(angle2), radius * math.sin(angle2))
        segment = pymunk.Segment(body, p1, p2, 5)
        segment.elasticity = bouncy/10
        segment.friction = 0.1
        space.add(segment)
        ground_shapes.append(segment)

    return ground_shapes


def draw_circle(screen, shape, color):
    pos = shape.body.position
    pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), int(shape.radius))

def draw_segment(screen, shape, color):
    body = shape.body
    p1 = body.local_to_world(shape.a)
    p2 = body.local_to_world(shape.b)
    pygame.draw.line(screen, color, (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), 5)

def is_object_outside_circle(object_position, circle):
    """
    Check if an object is outside a circular boundary.
    
    :param object_position: (x, y) tuple of the object's position
    :param circle_center: (x, y) tuple of the circle's center
    :param circle_radius: radius of the circle
    :param tolerance: additional distance beyond the radius to consider (default 0)
    :return: True if the object is outside the circle, False otherwise
    """
    circle_center = circle['center']
    circle_radius = circle['radius']
    dx = object_position[0] - circle_center[0]
    dy = object_position[1] - circle_center[1]
    distance = math.sqrt(dx**2 + dy**2)
    return distance > circle_radius


def main():
    # Create objects
    ball = create_ball(space, (300, 200))
    ground_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    ground_body.position = (300, 300)
    space.add(ground_body)
    ground_shapes = create_circular_ground(space, ground_body, 250)

    # Define elements outside the game loop
    elements = {
        'ball': {'type': 'circle', 'shape': ball, 'color': pygame.Color("white"), 'to_remove': False},
        'ground': {
            'type': 'segments', 
            'shapes': ground_shapes, 
            'color': pygame.Color("white"),
            'circle_info': {'center': (300, 300), 'radius': 250},
            'to_remove': False
        }
    }

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Update physics
        space.step(dt)
        
        rotation_speed = 0.5  # Degrees per frame
        ground_body.angle += math.radians(rotation_speed)

        # Update and check for removal
        elements_to_remove = []
        for key, element in elements.items():
            if not element['to_remove']:
                # Check if ball is outside the circle
                if element['type'] == 'circle':
                    ball_position = element['shape'].body.position
                    for other_key, other_element in elements.items():
                        if 'circle_info' in other_element:
                            if is_object_outside_circle(ball_position, other_element['circle_info']):
                                print(f"Ball has exited the circle: {other_element['circle_info']}")
                                element['to_remove'] = True
                                elements_to_remove.append(key)
                                break  # Exit the inner loop once we've found the circle

        # Remove flagged elements
        for key in elements_to_remove:
            element = elements[key]
            if element['type'] == 'circle':
                space.remove(element['shape'], element['shape'].body)
            elif element['type'] == 'segments':
                for shape in element['shapes']:
                    space.remove(shape)
            del elements[key]
            print(f"Removed element: {key}")

        # Draw elements
        screen.fill(pygame.Color("black"))
        for element in elements.values():
            if element['type'] == 'circle':
                draw_circle(screen, element['shape'], element['color'])
            elif element['type'] == 'segments':
                for shape in element['shapes']:
                    draw_segment(screen, shape, element['color'])

        pygame.display.flip()
        pygame.display.set_caption(f"fps: {clock.get_fps():.2f}") 
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
