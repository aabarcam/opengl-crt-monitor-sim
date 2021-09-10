from PIL.Image import new
import glfw
from OpenGL.GL import *
import numpy as np
import grafica.transformations as tr
import math

import grafica.scene_graph as sg

class Cell:
    def __init__(self, pos, size):
        self.pos  = pos
        self.size = size
        self.grid = None
        self.num = None
        self.state = None
        self.total = 0

    def set_state(self, new_state):
        self.state = new_state

    def set_pos(self, transform):
        old_pos = [self.pos[0], self.pos[1], self.pos[2], 1]
        new_pos = tr.matmul([transform, old_pos])
        self.pos = [new_pos[0], new_pos[1], new_pos[2]]

    def update(self, delta):
        if self.state > 0:
            self.state -= delta
        elif self.state < 0:
            self.state = 0


class Grid:
    def __init__(self, pos, size, row_cells):
        self.pos = pos
        self.size = size
        self.model = None
        self.cells = row_cells
        self.cell_list = []
        self.states = []

    def set_model(self, new_model):
        self.model = new_model
    
    def set_cells(self):
        cell_size = self.size / self.cells
        start_pos = [self.pos[0] - (self.cells/2 - 0.5) * cell_size, self.pos[1] - (self.cells/2 - 0.5) * cell_size]
        for i in range(self.cells):
            for j in range(self.cells):
                x = i * cell_size + start_pos[0]
                y = j * cell_size + start_pos[1]
                self.cell_list.append([x, y])
                self.states.append(0)

    def update(self):
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], self.pos[2]), tr.rotationX(-np.pi/2), tr.uniformScale(self.size)])

class Electron:
    def __init__(self, pos, size):
        self.pos = np.array(pos)
        self.orig_pos = self.pos
        self.vel = np.array([-1.0, 0.0, 0.0])
        self.orig_vel = self.vel
        self.acc = np.array([0.0, 0.0, 0.0])
        self.vel_mult = 1.0
        self.size = size
        self.radius = self.size * 0.5
        self.model = None

    def set_model(self, new_model):
        self.model = new_model
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], self.pos[2]), tr.uniformScale(self.size)])

    def set_vel(self, new_vel):
        self.vel_mult = new_vel

    def set_acceleration(self, new_acc):
        self.acc = new_acc.copy()

    def collisionWithY(self, plane_pos):
        if self.pos[0] - self.radius <= plane_pos:
            return True
        return False

    def update(self, delta, method):
        # euler
        if method == "euler":
            acc = self.acc * self.vel_mult
            self.vel = self.vel + delta * acc
            vel = self.vel * self.vel_mult
            self.pos = self.pos + delta * vel
        # euler modificado
        elif method == "euler_modificado":
            # la funcion es una constante
            acc = self.acc * self.vel_mult
            self.vel = self.vel + delta * acc
            vel = self.vel * self.vel_mult
            self.pos = self.pos + delta * vel
        # euler mejorado
        elif method == "euler_mejorado":
            acc = self.acc * self.vel_mult
            self.vel = self.vel + (delta/2) * (acc + acc)
            vel = self.vel * self.vel_mult
            self.pos = self.pos + (delta/2) * (vel + vel)
        # runge kutta 4
        elif method == "rk4":
            acc = self.acc * self.vel_mult
            k1a = k2a = k3a = k4a = acc
            self.vel = self.vel + (delta/6) * (k1a + 2*k2a + 2*k3a + k4a)
            vel = self.vel * self.vel_mult
            k1v = k2v = k3v = k4v = vel
            self.pos = self.pos + (delta/6) * (k1v + 2*k2v + 2*k3v + k4v)
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], self.pos[2]), tr.uniformScale(self.size)])

class ForceField:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.x_plane = self.pos[0]
        self.force = np.array([0.0, 0.0, 0.0])
        self.model = None

    def set_force(self, new_force):
        self.force = new_force

    def set_model(self, new_model):
        self.model = new_model

    def update(self):
        self.model.transform = tr.translate(self.pos[0], self.pos[1], self.pos[2])

    def electronCollision(self, electron_list):
        for electron in electron_list:
            if  electron.pos[0] > self.pos[0] - self.size[0]/2 and electron.pos[0] < self.pos[0] + self.size[0]/2 \
            and electron.pos[1] > self.pos[1] - self.size[1]/2 and electron.pos[1] < self.pos[1] + self.size[1]/2 \
            and electron.pos[2] > self.pos[2] - self.size[2]/2 and electron.pos[2] < self.pos[2] + self.size[2]/2:
                electron.set_acceleration(self.force)
            else:
                electron.set_acceleration(np.array([0.0, 0.0, 0.0]))