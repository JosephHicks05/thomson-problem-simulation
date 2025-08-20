from vpython import *
import time
from random import uniform as rand
from math import pi


SIM_SPEED = 1
MAX_N_SELECTION = 30
electron_number = 12
deltat = 1/960
PRINT_FREQUENCY = .0004

# screen setup
SCREEN_SCALE = 500
ASPECT_RATIO = 1
scene.width = SCREEN_SCALE
scene.height = SCREEN_SCALE * (ASPECT_RATIO ** -1)
scene.background = color.white
# screen setup

PI = 3.14159265
GOLDEN_RATIO = (1 + (5**.5))/2

def get_random_point_on_sphere():
    y = (random() * 2) - 1
    angle = random() * 2 * PI

    x = cos(angle) * ((1 - y**2) ** .5)
    z = sin(angle) * ((1 - y**2) ** .5)

    return vector(x, y, z)


sphere_of_interest = sphere(pos=vector(0, 0, 0), radius=1, color=color.red)

ELECTRON_COLOR = vector(.4, .4, 1)
ELECTRON_RADIUS = .25
electrons = []

simulation_running = False

IDEAL_SOLUTIONS = [
    [],
    [vector(0, 1, 0)],
    [vector(0, 1, 0), vector(0, -1, 0)],
    [vector(0, 1, 0), vector(-(3**.5)/2, -.5, 0), vector((3**.5)/2, -.5, 0)],
    [vector(0, 1, 0), vector(2*(2**.5)/3, -1/3, 0), vector(-(2**.5)/3, -1/3, (6**.5)/3), vector(-(2**.5)/3, -1/3, -(6**.5)/3)],
    [vector(0, 1, 0), vector(0, -1, 0), vector(1, 0, 0), vector(-.5, 0, -(3**.5)/2), vector(-.5, 0, (3**.5)/2)],
    [vector(0, 1, 0), vector(0, -1, 0), vector(1, 0, 0), vector(-1, 0, 0), vector(0, 0, 1), vector(0, 0, -1)],
    
    [norm(vector(0, 1, GOLDEN_RATIO)), norm(vector(0, -1, GOLDEN_RATIO)), norm(vector(0, 1, -GOLDEN_RATIO)), norm(vector(0, -1, -GOLDEN_RATIO)), 
    norm(vector(1, GOLDEN_RATIO, 0)), norm(vector(-1, GOLDEN_RATIO, 0)), norm(vector(1, -GOLDEN_RATIO, 0)), norm(vector(-1, -GOLDEN_RATIO, 0)),
    norm(vector(GOLDEN_RATIO, 0, 1)), norm(vector(-GOLDEN_RATIO, 0, 1)), norm(vector(GOLDEN_RATIO, 0, -1)), norm(vector(-GOLDEN_RATIO, 0, -1))]
]

BEST_GUESSES = [
    (7, 14.4530), (8, 19.6753), (9, 25.7600), (10, 32.7169), (11, 40.5964), (13, 58.8532),
    (14, 69.3064), (15, 80.6702), (16, 92.9117), (17, 106.05), (18, 120.084), (19, 135.089),
    (20, 150.882), (21, 167.642), (22, 185.288), (23, 203.93), (24, 223.347), (25, 243.813),
    (26, 265.133), (27, 287.303), (28, 310.492), (29, 334.634), (30, 359.604), (31, 385.531),
    (32, 412.261), (33, 440.204), (34, 468.905), (35, 498.57), (36, 529.122), (37, 560.619),
    (38, 593.039), (39, 626.389), (40, 660.675), (41, 695.917), (42, 732.078), (43, 769.191),
    (44, 807.174), (45, 846.188), (46, 886.167), (47, 927.059), (48, 968.713), (49, 1011.56),
    (50, 1055.18), 
]

def generate_electrons(electron_number):
    global electrons
    
    for electron in electrons:
        electron.visible = False
        del electron
        
    electrons = []
    
    for i in range(electron_number):
        electrons.append(sphere(pos=get_random_point_on_sphere(), radius=ELECTRON_RADIUS, color=ELECTRON_COLOR))


def update_electrons(electron1, electron2, deltat):
    relative_position_1_2 = electron2.pos - electron1.pos

    force_1_2 = (1 / (mag(relative_position_1_2) ** 2)) * norm(relative_position_1_2)
    # we make the simplifying assumption that the charges are 1.
    # also epsilon_0, pi, and 4 are all 1. theoretical physics, baby.
    force_2_1 = -force_1_2

    electron1.pos = norm(electron1.pos + (force_2_1 * deltat))
    electron2.pos = norm(electron2.pos + (force_1_2 * deltat))


def get_electric_potential_energy(electron1, electron2):
    distance = mag(electron2.pos - electron1.pos)
    # again all constants are 1.
    return (1 / distance)


def get_total_electric_potential_energy(electrons):
    total_energy = 0
    for electron_1_index, electron1 in enumerate(electrons):
        for electron2 in electrons[electron_1_index + 1:]:
            total_energy += get_electric_potential_energy(electron1, electron2)
    
    return total_energy


def disable_button(to_disable):
    to_disable.disabled = True
    to_disable.color = color.black
    to_disable.background = color.black
    

def enable_button(to_enable):
    to_enable.disabled = False
    to_enable.color = color.black
    to_enable.background = color.white


def disable_N_selection():
    for n_button in n_selection_buttons:
        disable_button(n_button)


def enable_N_selection():
    for n_button in n_selection_buttons:
        enable_button(n_button)


def set_electron_number(evt):
    global electron_number
    electron_number = int(evt.text)
    disable_N_selection()
    
    
def move_electrons(locations):
    for new_location, electron in zip(locations, electrons):
        electron.pos = new_location


def show_ideal_solution():
    for solution in IDEAL_SOLUTIONS:
        if len(solution) == electron_number:
            move_electrons(solution)
            return

    for best_guess in BEST_GUESSES:
        if best_guess[0] == electron_number:
            print(f"there is no confirmed ideal solution for N = {electron_number}, but the conjectured lowest potential energy is {best_guess[1]}")
            return
    
 
def toggle_sphere():
    global sphere_of_interest
    sphere_of_interest.visible = not sphere_of_interest.visible
    

def toggle_simulation():
    global toggle_simulation_button
    global simulation_running
    
    simulation_running = not simulation_running
    
    if simulation_running:
        toggle_simulation_button.text = "stop simulation"
    else:
        toggle_simulation_button.text = "run simulation"
    

toggle_simulation_button = button(text="run simulation", bind=toggle_simulation)

enable_N_selection_button = button(text="Select number of electrons", bind=enable_N_selection)

n_selection_buttons = [button(text=str(N), bind=set_electron_number) for N in range(MAX_N_SELECTION + 1)]
disable_N_selection()

show_ideal_solution_button = button(text="Show ideal solution", bind=show_ideal_solution)
toggle_sphere_button = button(text="Toggle sphere visibility", bind=toggle_sphere)

sim_steps = 0
current_displayed_electrons = 0

while True:
    sim_steps += 1
    rate(SIM_SPEED/deltat)
    
    if current_displayed_electrons != electron_number:
        generate_electrons(electron_number)
        current_displayed_electrons = electron_number

    electric_potential_energy = 0
    
    if simulation_running:
        for electron_1_index, electron1 in enumerate(electrons):
            for electron2 in electrons[electron_1_index + 1:]:
                update_electrons(electron1, electron2, deltat)

    

    if sim_steps % int(1/PRINT_FREQUENCY) == 1:
        print(f"N = {electron_number}  |  Electric Potential Energy: {get_total_electric_potential_energy(electrons):.7}")
