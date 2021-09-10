import glfw
from OpenGL.GL import *
import numpy as np
import random as rd
import math
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.lighting_shaders as ls
import grafica.performance_monitor as pm
from grafica.assets_path import getAssetPath

import imgui
from imgui.integrations.glfw import GlfwRenderer

# Custom imports

import custom_modules.custom_shapes as csh
import custom_modules.custom_scenegraph as csg
import custom_modules.custom_light_shaders as cls

import models as md
import shapes as sh

class Camera:
    def __init__(self):
        self.center = np.array([0.0, 0.0, 0.0])
        self.offset = np.array([0.0, 0.0, 0.0])
        self.rho = 5
        self.eye = np.array([0.0, 0.0, 0.0])
        self.height = 0.5
        self.up = np.array([0, 0, 1])
        self.viewMatrix = None

    def set_rho(self, delta):
        if ((self.rho + delta) > 1.5):
            self.rho += delta

    def reset_position(self):
        self.offset = np.array([0.0, 0.0, 0.0])

    def get_viewMatrix(self):
        return self.viewMatrix

class SideCamera(Camera):
    # Actualizar la matriz de vista
    def update_view(self):
        # Se calcula la posición de la camara con coordenadas poleras relativas al centro
        self.center[0] = -self.offset[0]
        self.center[1] = -self.offset[1]
        self.center[2] = self.offset[2]
        self.eye[0] = self.center[0]
        self.eye[1] = self.center[1] + self.rho
        self.eye[2] = self.height + self.center[2]

        # Se genera la matriz de vista
        self.viewMatrix = tr.lookAt(
            self.eye,
            self.center,
            self.up
        )

class FrontCamera(Camera):
    def update_view(self):
        # Se calcula la posición de la camara con coordenadas poleras relativas al centro
        self.center[0] = self.offset[1]
        self.center[1] = -self.offset[0]
        self.center[2] = self.offset[2]
        self.eye[0] = self.center[0] - self.rho
        self.eye[1] = self.center[1]
        self.eye[2] = self.height + self.center[2]

        # Se genera la matriz de vista
        self.viewMatrix = tr.lookAt(
            self.eye,
            self.center,
            self.up
        )
        
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True

        # Variables para controlar la camara
        self.is_up_pressed = False
        self.is_down_pressed = False

        # Se crea instancia de la camara
        self.side_camera = SideCamera()
        self.front_camera = FrontCamera()
        
        self.active_camera = self.side_camera

    # Entregar la referencia a la camara
    def get_camera(self):
        return self.active_camera

    def shift_camera(self, num):
        if num == 0:
            self.active_camera = self.side_camera
        else:
            self.active_camera = self.front_camera

    # Metodo para ller el input del teclado
    def on_key(self, window, key, scancode, action, mods):
        # Caso de detectar la barra espaciadora, se cambia el metodo de dibujo
        if key == glfw.KEY_SPACE:
            if action == glfw.PRESS:
                self.fillPolygon = not self.fillPolygon

        # Caso en que se cierra la ventana
        if key == glfw.KEY_ESCAPE:
            if action == glfw.PRESS:
                glfw.set_window_should_close(window, True)
    
    def update_camera(self, delta):        
        # Camara se acerca al centro
        if self.is_up_pressed:
            self.active_camera.set_rho(-5 * delta)

        # Camara se aleja del centro
        if self.is_down_pressed:
            self.active_camera.set_rho(5 * delta)

def transformGuiOverlay(offset, precision, time, field, el_vel, method, vect, grid):
    global controller
    # Funcion para actualizar el menu
    # start new frame context
    imgui.new_frame()

    # open new window context
    imgui.begin("Control de escena", False, imgui.WINDOW_ALWAYS_AUTO_RESIZE)

    # draw text label inside of current window
    imgui.text("Posicion de la camara")

    edited, offset[0] = imgui.slider_float("Horizontal", offset[0], -5.0, 5.0)
    edited, offset[2] = imgui.slider_float("Vertical", offset[2], -5.0, 5.0)
    edited, offset[1] = imgui.slider_float("Profundidad", offset[1], -5.0, 5.0)

    if imgui.button("Camara lateral"):
        controller.shift_camera(0)
        controller.active_camera.reset_position()
    imgui.same_line(spacing=5)
    if imgui.button("Camara frontal"):
        controller.shift_camera(1)
        controller.active_camera.reset_position()
        
    imgui.text("Control de electrones")

    edited, el_vel = imgui.slider_float("Velocidad", el_vel, 0.5, 4.0)
    edited, precision = imgui.slider_float("Precision", precision, 1, 100)
    edited, time = imgui.slider_float("Periodo de disparo", time, 0.05, 2)

    imgui.text("Metodo numerico")
    if imgui.button("Euler"):
        method = "euler"
    imgui.same_line(spacing=5)
    if imgui.button("Euler modificado"):
        method = "euler_modificado"
    if imgui.button("Euler mejorado"):
        method = "euler_mejorado"
    imgui.same_line(spacing=5)
    if imgui.button("RK4"):
        method = "rk4"

    imgui.text("Control de campo de fuerza")
    edited, field[1] = imgui.slider_float("Fuerza horizontal", field[1], -1.1, 1.1)
    edited, field[2] = imgui.slider_float("Fuerza vertical", field[2], -1.1, 1.1)
    if imgui.button("Campo vectorial"):
        vect = not vect
    if imgui.button("Grilla"):
        grid = not grid

    imgui.end()
    # pass all drawing comands to the rendering pipeline
    # and close frame context
    imgui.render()
    imgui.end_frame()

    return offset, precision, time, field, el_vel, method, vect, grid

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "Simulador de CRT"

    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Se instancia un controller
    controller = Controller()
    # Se conecta el metodo on_key del controller para manejar el input del teclado
    glfw.set_key_callback(window, controller.on_key)

     # Different shader programs for different lighting strategies
    phongTexPipeline = ls.SimpleTexturePhongShaderProgram() # Pipeline para dibujar texturas

    phongMultipleLightsPipeline = cls.MultiplePhongShaderProgram()

    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Create shapes
    circle_n = 20

    cell_size = 0.05
    grid_width = 25
    grid_height = 25
    total = grid_width * grid_height
    grids = 16
    
    grid_list = []
    vert_list = []

    grid_structures = sh.createNStructs(cell_size, grid_width, grid_height, grids)
    cells_list = []
    grid_offset = tr.matmul([tr.translate(-2, 0, 0), tr.rotationY(-np.pi * 0.5)])
    for i in range(grids):
        hor = i%4
        ver = i//4
        for j in range(total):
            grid_structures[i][j][0] += hor*grid_width*cell_size + cell_size/2 - cell_size*grid_width*2
            grid_structures[i][j][1] += ver*grid_height*cell_size + cell_size/2 - cell_size*grid_height*2
            cell = md.Cell(grid_structures[i][j], cell_size)
            cell.state = rd.randint(0, 100)/100
            cell.grid = i
            cell.num  = j
            cells_list.append(cell)
        
        gpuGrid, grid_vertices = sh.createGridQuads(phongMultipleLightsPipeline, cell_size, grid_structures[i])
        grid_list.append(gpuGrid)
        vert_list.append(grid_vertices)
    
    vert_list = np.array(vert_list, dtype=np.float32)
    active_cells = cells_list.copy()
    length = len(vert_list[0])

    grid_bg = sh.createGridModel(phongMultipleLightsPipeline)

    quarterPyramidNode = sh.createQuarterPyramid(phongMultipleLightsPipeline)
    quarterPyramidNode.transform = tr.matmul([tr.translate(-2, 0, 0), tr.rotationZ(-np.pi), tr.rotationY(-np.pi * 0.5), tr.scale(4*cell_size*grid_height, 4*cell_size*grid_width, 10)])
   
    vectorialNode = sh.createTexQuads(phongTexPipeline, 5, "assets/arrow.png")
    vectorialNode.transform = tr.translate(0.5, -0.4, -0.4)

    # Create scenes

    halfTubeNode = sh.createColorQuadCylinder(phongMultipleLightsPipeline)
    halfTubeNode.transform = tr.matmul([tr.translate(1.75, 0, 0), tr.uniformScale(2.5)])

    finalScene = sg.SceneGraphNode("escena")
    finalScene.childs = [halfTubeNode]

    # Create models
    field_pos = np.array([1.0, 0.0, 0.0])
    field_size = np.array([0.75, 1.0, 1.0])
    plate_size = np.array([field_size[0], 0.25, 0.1])
    field = md.ForceField(field_pos, field_size)
    fieldModel = sh.createFieldModel(phongMultipleLightsPipeline, field_size, plate_size, 0.8, 0.8, 0.8)
    field.set_model(fieldModel)

    testCube = sh.createGPUCube(phongMultipleLightsPipeline, field.pos[0] - field.size[0]/2, field.pos[0] + field.size[0]/2, field.pos[1] - field.size[1]/2, field.pos[1] + field.size[1]/2, field.pos[2] - field.size[2]/2, field.pos[2] + field.size[2]/2)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    glfw.swap_interval(0)
    t0 = glfw.get_time()

    imgui.create_context()
    impl = GlfwRenderer(window)
    
    controller = Controller()
    
    glfw.set_key_callback(window, controller.on_key)

    time = 0
    electron_list = []
    electron_size = 0.05
    electron_vel = 1.0
    field_force = np.array([0.0, 0.0, 0.0])
    calc_method = "euler"

    ka = [0.6, 0.6, 0.6] 
    kd = [0.8, 0.8, 0.8]
    ks = [1.0, 1.0, 1.0]

    lights =   [-15.0, 0.0, 0.0]

    light_cnt = len(lights)/3
    litGrids = []
    lit_amount = []

    vect_angle = 0

    precision = 1
    T = 1

    vect_field = False

    grid_v2 = False
    while not glfw.window_should_close(window):
        
        perfMonitor.update(t0)
        glfw.set_window_title(window, title + str(perfMonitor))
        # Variables del tiempo
        t1 = glfw.get_time()
        delta = t1 -t0
        t0 = t1
        
        impl.process_inputs()
        # Using GLFW to check for input events
        glfw.poll_events()

        controller.update_camera(delta)
        camera = controller.get_camera()
        camera.update_view()
        viewMatrix = camera.get_viewMatrix()

        projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

        if field.force[1] != 0:
            vect_angle = math.atan(field.force[2]/field.force[1])
        if field.force[1] < 0:
            vect_angle += np.pi

        to_remove = []
        new_vertices = vert_list
        
        time += delta

        # Esto ocurre cada T segundos
        if time > T:
            field.set_force(field_force)
            time = 0
            if precision < 100:
                electron = md.Electron([3, rd.randint(-50,50)/(precision * 100), rd.randint(-50,50)/(precision * 100) + cell_size/2], electron_size)
            else:
                electron = md.Electron([3, 0.0, 0.0], electron_size)
            electron_model = sh.electronModel(phongMultipleLightsPipeline, circle_n)
            electron.set_model(electron_model)
            electron_list.append(electron)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # imgui function
        camera.offset, precision, T, field_force, electron_vel, calc_method, vect_field, grid_v2 = transformGuiOverlay(camera.offset, precision, T, field_force, electron_vel, calc_method, vect_field, grid_v2)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        
        # Updating entities
        field.electronCollision(electron_list)
        field.update()
        for i in range(len(electron_list) - 1, -1, -1):
            electron = electron_list[i]
            electron.update(delta, calc_method)
            electron.set_vel(electron_vel)
            if electron.collisionWithY(-2):
                for cell in cells_list:
                    if electron.pos[2] > cell.pos[0] - cell_size/2 and electron.pos[2] < cell.pos[0] + cell_size/2 \
                    and electron.pos[1] > cell.pos[1] - cell_size/2 and electron.pos[1] < cell.pos[1] + cell_size/2:
                        x = cell.grid
                        prev_state = cell.state
                        cell.state = 1
                        cell.total += 0.05
                        if cell not in active_cells:
                            active_cells.append(cell)
                        if x not in litGrids:
                            litGrids.append(x)
                            lit_amount.append(1)
                            light_cnt += 1
                            lights = lights + [grid_structures[x][total//2][2] - 6.0] + [grid_structures[x][total//2][1] * 2] + [grid_structures[x][total//2][0] * 2]
                        elif prev_state == 0:
                            p = litGrids.index(x)
                            lit_amount[p] += 1
                        break
                electron_list.pop(i)

        # Determinando settings del frame
        light_settings = [camera, ka, kd, ks, projection, viewMatrix]
        # Dibujando colores normales
        lightingPipeline = phongMultipleLightsPipeline
        glUseProgram(lightingPipeline.shaderProgram)
        glUniform3fv(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPos"), len(lights)//3, lights)
        glUniform1i(glGetUniformLocation(lightingPipeline.shaderProgram, "lights"), len(lights)//3)
        cls.default_light_settings(lightingPipeline, light_settings)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, grid_offset)
        for i in range(len(active_cells)):
            cell = active_cells[i]
            color = cell.state
            if grid_v2:
                color = cell.total
            j = cell.grid
            if color != 0:
                k = cell.num
                first_vert = 36*k
                cell.update(delta)
                for v in range(4):
                    each_vert = v*9
                    vert_list[j][first_vert + each_vert + 3] = color
                    vert_list[j][first_vert + each_vert + 4] = color
                    vert_list[j][first_vert + each_vert + 5] = color
            else:
                to_remove.append(i)
                if cell.grid in litGrids:
                    x = litGrids.index(cell.grid)
                    lit_amount[x] -= 1
                    if lit_amount[x] == 0:
                        lit_amount.pop(x)
                        litGrids.pop(x)
                        lights.pop(3*(x+1)+2)
                        lights.pop(3*(x+1)+1)
                        lights.pop(3*(x+1))

        for i in range(len(to_remove) - 1, -1, -1):
            active_cells.pop(to_remove[i])
        
        
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)

        for i in range(len(grid_list)):
            glBindBuffer(GL_ARRAY_BUFFER, grid_list[i].vbo)
            glBufferData(GL_ARRAY_BUFFER, length * 4, vert_list[i], GL_STREAM_DRAW)
            lightingPipeline.drawCall(grid_list[i])

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(0.01, 0, 0), grid_offset, tr.uniformScale(grid_width*cell_size*4)]))
        
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), ka[0], ka[1], ka[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.7, 0.7, 0.7)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 0.05, 0.05, 0.05)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.05)
        lightingPipeline.drawCall(grid_bg)
        for electron in electron_list:
            sg.drawSceneGraphNode(electron.model, lightingPipeline, "model")

        sg.drawSceneGraphNode(fieldModel, lightingPipeline, "model")
        sg.drawSceneGraphNode(quarterPyramidNode, lightingPipeline, "model")
        sg.drawSceneGraphNode(finalScene, lightingPipeline, "model")

        # Dibujando texturas
        lightingPipeline = phongTexPipeline
        glUseProgram(lightingPipeline.shaderProgram)

        cls.default_light_settings(lightingPipeline, light_settings)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), lights[0], lights[1], lights[2])
        for quad in vectorialNode.childs:
            quad.childs[0].transform = tr.rotationZ(vect_angle)
        if vect_field and vect_angle:
            sg.drawSceneGraphNode(vectorialNode, lightingPipeline, "model")
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        impl.render(imgui.get_draw_data())

            
        glfw.swap_buffers(window)

    finalScene.clear()
    glfw.terminate()
