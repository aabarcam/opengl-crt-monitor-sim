import math
import random as rd
import numpy as np

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

def toVerticesAndIndexes(mesh, r, g, b):
    faces = mesh.faces()

    vertices = []
    v = 0

    mesh.request_face_normals()
    mesh.request_vertex_normals()
    mesh.release_face_normals()
    mesh.update_vertex_normals()

    nor_list = mesh.vertex_normals()

    for vertex in mesh.points():
        vertices += vertex.tolist() # Pos
        vertices += [r, g, b] # Color
        vertices += [nor_list[v][0],nor_list[v][1],nor_list[v][2]] # Normales
            
        v += 1

    indexes = []

    for face in faces:
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            indexes += [vertex.idx()]

    return vertices, indexes

def toTexCylinderVerticesAndIndexes(mesh):
    faces = mesh.faces()

    vertices = []
    v = 0

    mesh.request_face_normals()
    mesh.request_vertex_normals()
    mesh.release_face_normals()
    mesh.update_vertex_normals()

    nor_list = mesh.vertex_normals()

    for vertex in mesh.points():
        vert = vertex.tolist()
        vertices += vert # Pos
        vertices += [vert[0], vert[1]] # Tex        
        vertices += [nor_list[v][0],nor_list[v][1],nor_list[v][2]] # Normales
            
        v += 1

    indexes = []

    for face in faces:
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            indexes += [vertex.idx()]

    return vertices, indexes

def createColorNormalsQuad(r, g, b):

    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #   positions        colors     normals
        -0.5, -0.5, 0.0,  r, g, b,  0, 0, 1,
         0.5, -0.5, 0.0,  r, g, b,  0, 0, 1,
         0.5,  0.5, 0.0,  r, g, b,  0, 0, 1,
        -0.5,  0.5, 0.0,  r, g, b,  0, 0, 1]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return Shape(vertices, indices)

def createTextureNormalsQuad(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions        texture
        -0.5, -0.5, 0.0,  0, ny,    0, 0, 1,
         0.5, -0.5, 0.0, nx, ny,    0, 0, 1,
         0.5,  0.5, 0.0, nx, 0,     0, 0, 1,
        -0.5,  0.5, 0.0,  0, 0,     0, 0, 1]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return Shape(vertices, indices)

def createGridStruct(cell_size, width, height):
    coordinates = []
    for i in range(height):
        y = i * cell_size
        for j in range(width):
            x = j * cell_size
            coordinates += [[x, y, 0]]
    return coordinates


def createGridCells(cell_size, centers):
    BLACK = [0, 0, 0] # RGB
    WHITE = [1,1,1]
    NORMALS = [0, 0, -1]
    vertices = []
    indices = []
    step = cell_size * 0.49
    for i in range(len(centers)):
        rand_color = rd.randint(0,100)/100
        color = [rand_color, rand_color, rand_color]
        vertices = vertices + [centers[i][0] - step, centers[i][1] - step, 0] + BLACK + NORMALS
        vertices = vertices + [centers[i][0] + step, centers[i][1] - step, 0] + BLACK + NORMALS
        vertices = vertices + [centers[i][0] + step, centers[i][1] + step, 0] + BLACK + NORMALS
        vertices = vertices + [centers[i][0] - step, centers[i][1] + step, 0] + BLACK + NORMALS

        index_step = 4*i
        indices += [
            index_step    , index_step + 1, index_step + 2,
            index_step + 2, index_step + 3, index_step
        ]
    return Shape(vertices, indices)

def createPyramidShape(r, g, b):
    SQ2 = 1/math.sqrt(2)
    vertices = [
        # positions         # colors    # normals
        -0.5, -0.5, 0.0,    r, g, b,    0, 0, -1,
        0.5, -0.5, 0.0,     r, g, b,    0, 0, -1,
         0.5,  0.5, 0.0,    r, g, b,    0, 0, -1,
        -0.5,  0.5, 0.0,    r, g, b,    0, 0, -1,

        -0.5, -0.5, 0.0,    r, g, b,    -SQ2, 0, SQ2,
        -0.5,  0.5, 0.0,    r, g, b,    -SQ2, 0, SQ2,
        0.0, 0.0, 0.5,      r, g, b,    -SQ2, 0, SQ2,

        0.5, 0.5, 0.0,      r, g, b,    SQ2, 0, SQ2,
        0.5, -0.5, 0.0,     r, g, b,    SQ2, 0, SQ2,
        0.0, 0.0, 0.5,      r, g, b,    SQ2, 0, SQ2,

        0.5, 0.5, 0.0,      r, g, b,    0, SQ2, SQ2,
        -0.5, 0.5, 0.0,     r, g, b,    0, SQ2, SQ2,
        0.0, 0.0, 0.5,      r, g, b,    0, SQ2, SQ2,

        0.5, -0.5, 0.0,     r, g, b,    0, -SQ2, SQ2,
        -0.5, -0.5, 0.0,    r, g, b,    0, -SQ2, SQ2,
        0.0, 0.0, 0.5,      r, g, b,    0, -SQ2, SQ2
    ]
    indices = [
        0, 1, 2,
        2, 3, 0,
        4, 5, 6,
        7, 8, 9,
        10, 11, 12,
        13, 14, 15
    ]
    return Shape(vertices, indices)

def createQuarterPyramidShape(r, g, b):
    SQ2 = 1/math.sqrt(2)
    vertices = [
        -0.25, 0.25, 0.25,  r, g, b,    SQ2, 0, -SQ2,
        -0.5, 0.5, 0.0,     r, g, b,    SQ2, 0, -SQ2,
        -0.5, -0.5, 0.0,     r, g, b,    SQ2, 0, -SQ2,
        -0.25, -0.25, 0.25,   r, g, b,    SQ2, 0, -SQ2,

        0.5, 0.5, 0.0,      r, g, b,    -SQ2, 0, -SQ2,
        0.5, -0.5, 0.0,      r, g, b,    -SQ2, 0, -SQ2,
        0.25, -0.25, 0.25,    r, g, b,    -SQ2, 0, -SQ2,
        0.25, 0.25, 0.25,   r, g, b,    -SQ2, 0, -SQ2,

        0.5, 0.5, 0.0,      r, g, b,    0, -SQ2, -SQ2,
        -0.5, 0.5, 0.0,     r, g, b,    0, -SQ2, -SQ2,
        -0.25, 0.25, 0.25,  r, g, b,    0, -SQ2, -SQ2,
        0.25, 0.25, 0.25,   r, g, b,    0, -SQ2, -SQ2
    ]
    indices = [
        0, 1, 2,
        2, 3, 0,
        4, 5, 6,
        6, 7, 4,
        8, 9, 10,
        10, 11, 8,
    ]
    return Shape(vertices, indices)

def createTextureNormalsQuadCylinder(image_filename):

    # Defining locations,texture coordinates and normals for each vertex of the shape  
    vertices = [
    #   positions            tex coords   normals
    # Z+
        -0.5, -0.5,  0.5,    0, 1,        0,0,-1,
         0.5, -0.5,  0.5,    1, 1,        0,0,-1,
         0.5,  0.5,  0.5,    1, 0,        0,0,-1,
        -0.5,  0.5,  0.5,    0, 0,        0,0,-1,   
    # Z-          
        -0.5, -0.5, -0.5,    0, 1,        0,0,1,
         0.5, -0.5, -0.5,    1, 1,        0,0,1,
         0.5,  0.5, -0.5,    1, 0,        0,0,1,
        -0.5,  0.5, -0.5,    0, 0,        0,0,1,
    # X+          
         0.5, -0.5, -0.5,    0, 1,        -1,0,0,
         0.5,  0.5, -0.5,    1, 1,        -1,0,0,
         0.5,  0.5,  0.5,    1, 0,        -1,0,0,
         0.5, -0.5,  0.5,    0, 0,        -1,0,0,  
    # Y-          
        -0.5, -0.5, -0.5,    0, 1,        0,1,0,
         0.5, -0.5, -0.5,    1, 1,        0,1,0,
         0.5, -0.5,  0.5,    1, 0,        0,1,0,
        -0.5, -0.5,  0.5,    0, 0,        0,1,0
        ]   

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15  # Y-
        ]

    return Shape(vertices, indices, image_filename)

def createColorNormalsQuadCylinder(r, g, b):

    # Defining locations,texture coordinates and normals for each vertex of the shape  
    vertices = [
    #   positions            tex coords   normals
    # Z+
        -0.5, -0.5,  0.5,    r, g, b,     0,0,-1,
         0.5, -0.5,  0.5,    r, g, b,     0,0,-1,
         0.5,  0.5,  0.5,    r, g, b,     0,0,-1,
        -0.5,  0.5,  0.5,    r, g, b,     0,0,-1,   
    # Z-          
        -0.5, -0.5, -0.5,    r, g, b,     0,0,1,
         0.5, -0.5, -0.5,    r, g, b,     0,0,1,
         0.5,  0.5, -0.5,    r, g, b,     0,0,1,
        -0.5,  0.5, -0.5,    r, g, b,     0,0,1,
    # X+          
         0.5, -0.5, -0.5,    r, g, b,     -1,0,0,
         0.5,  0.5, -0.5,    r, g, b,     -1,0,0,
         0.5,  0.5,  0.5,    r, g, b,     -1,0,0,
         0.5, -0.5,  0.5,    r, g, b,     -1,0,0,  
    # Y-          
        -0.5, -0.5, -0.5,    r, g, b,     0,1,0,
         0.5, -0.5, -0.5,    r, g, b,     0,1,0,
         0.5, -0.5,  0.5,    r, g, b,     0,1,0,
        -0.5, -0.5,  0.5,    r, g, b,     0,1,0
        ]   

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15  # Y-
        ]

    return Shape(vertices, indices)

def createBoundaryBoxTest(left, right, top, bottom, near, far):
    r = 1
    g = 0
    b = 0
    vertices = [
    #   positions         colors   normals
    # Z+
        left, near,  top, r, g, b, 0,0,1,
        right, near,  top, r, g, b, 0,0,1,
        right,  far,  top, r, g, b, 0,0,1,
        left,  far,  top, r, g, b, 0,0,1,

    # Z-
        left, near, bottom, r, g, b, 0,0,-1,
        right, near, bottom, r, g, b, 0,0,-1,
        right,  far, bottom, r, g, b, 0,0,-1,
        left,  far, bottom, r, g, b, 0,0,-1,
        
    # X+
        right, near, bottom, r, g, b, 1,0,0,
        right,  far, bottom, r, g, b, 1,0,0,
        right,  far,  top, r, g, b, 1,0,0,
        right, near,  top, r, g, b, 1,0,0,
 
    # X-
        left, near, bottom, r, g, b, -1,0,0,
        left,  far, bottom, r, g, b, -1,0,0,
        left,  far,  top, r, g, b, -1,0,0,
        left, near,  top, r, g, b, -1,0,0,

    # Y+
        left, far, bottom, r, g, b, 0,1,0,
        right, far, bottom, r, g, b, 0,1,0,
        right, far,  top, r, g, b, 0,1,0,
        left, far,  top, r, g, b, 0,1,0,

    # Y-
        left, near, bottom, r, g, b, 0,-1,0,
        right, near, bottom, r, g, b, 0,-1,0,
        right, near,  top, r, g, b, 0,-1,0,
        left, near,  top, r, g, b, 0,-1,0
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return Shape(vertices, indices)