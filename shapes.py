from os import pipe
import numpy as np
import math
import random as rd
from OpenGL.GL import *
import grafica.shapes3d as sh3
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.scene_graph as sg
import sys, os.path

import custom_modules.custom_shapes as csh
import custom_modules.custom_scenegraph as csg
import models as md

from grafica.assets_path import getAssetPath

def createGPUShape(shape, pipeline):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

def createHalfCylinder(pipeline, circle_n, cylinder_n, rad, r, g, b):
    mesh = csh.createHalfCylinder(circle_n, cylinder_n, rad)
    cylinder_vertices, cylinder_indices = csh.toVerticesAndIndexes(mesh, r, g, b)
    cylinderGpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(cylinderGpu)
    cylinderGpu.fillBuffers(cylinder_vertices, cylinder_indices, GL_STATIC_DRAW)
    return cylinderGpu

def createTexHalfCylinder(pipeline, circle_n, cylinder_n, rad):
    mesh = csh.createHalfCylinder(circle_n, cylinder_n, rad)
    cylinder_vertices, cylinder_indices = csh.toTexCylinderVerticesAndIndexes(mesh)
    cylinderGpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(cylinderGpu)
    cylinderGpu.fillBuffers(cylinder_vertices, cylinder_indices, GL_STATIC_DRAW)
    cylinderGpu.texture = es.textureSimpleSetup("assets/stone.png", GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    return cylinderGpu
 
def createGridModel(pipeline):
    blackQuad = csh.createColorNormalsQuad(0, 0, 0)
    gpuQuad = createGPUShape(blackQuad, pipeline)
    pipeline.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(blackQuad.vertices, blackQuad.indices, GL_STATIC_DRAW)
    return gpuQuad

def createGridQuads(pipeline, cell_size, grid_struct):
    gridShape = csh.createGridCells(cell_size, grid_struct)
    gpuGrid = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuGrid)
    gpuGrid.fillBuffers(gridShape.vertices, gridShape.indices, GL_STREAM_DRAW)
    return gpuGrid, gridShape.vertices

def createNStructs(cell_size, width, height, n):
    struct_list = []
    for i in range(n):
        struct = csh.createGridStruct(cell_size, width, height)
        struct_list.append(struct)
    return struct_list

def createPyramid(pipeline):
    pyramidShape = csh.createPyramidShape(0.5, 0.5, 0.5)
    gpuPyramid = createGPUShape(pyramidShape, pipeline)
    pyramidNode = sg.SceneGraphNode("piramide")
    pyramidNode.childs = [gpuPyramid]
    return pyramidNode

def createQuarterPyramid(pipeline):
    pyramidQShape = csh.createQuarterPyramidShape(0.5, 0.5, 0.5)
    gpuQPyramid = createGPUShape(pyramidQShape, pipeline)
    pyramidQNode = sg.SceneGraphNode("cuarto_piramide")
    pyramidQNode.childs = [gpuQPyramid]
    return pyramidQNode

def createColorQuadCylinder(pipeline):
    cyilinderShape = csh.createColorNormalsQuadCylinder(0.5, 0.5, 0.5)
    gpuCylinder = createGPUShape(cyilinderShape, pipeline)
    cylinderNode = sg.SceneGraphNode("cilindro_cuadrado")
    cylinderNode.childs = [gpuCylinder]
    return cylinderNode

def electronModel(pipeline, circle_n):
    sphereShape = sh3.createColorNormalSphere(circle_n, 1, 0, 0)
    gpuSphere = createGPUShape(sphereShape, pipeline)
    sphereNode = sg.SceneGraphNode("esfera")
    sphereNode.childs = [gpuSphere]
    return sphereNode

def createFieldModel(pipeline, field_size, plate_size, r, g, b):
    cubeShape = bs.createColorNormalsCube(r, g, b)
    gpuCube = createGPUShape(cubeShape, pipeline)
    plateNode = sg.SceneGraphNode("placa")
    plateNode.childs = [gpuCube]
    plateNode.transform = tr.scale(plate_size[0], plate_size[1], plate_size[2])
    
    plateTrNode1 = sg.SceneGraphNode("placa_trasladada_1")
    plateTrNode1.childs = [plateNode]
    plateTrNode1.transform = tr.translate(0, 0, field_size[2]/2)
    
    plateTrNode2 = sg.SceneGraphNode("placa_trasladada_2")
    plateTrNode2.childs = [plateNode]
    plateTrNode2.transform = tr.matmul([tr.translate(0, field_size[1]/2, 0), tr.rotationX(np.pi/2)])

    plateTrNode3 = sg.SceneGraphNode("placa_trasladada_3")
    plateTrNode3.childs = [plateNode]
    plateTrNode3.transform = tr.translate(0, 0, -field_size[2]/2)

    plateTrNode4 = sg.SceneGraphNode("placa_trasladada_4")
    plateTrNode4.childs = [plateNode]
    plateTrNode4.transform = tr.matmul([tr.translate(0, -field_size[1]/2, 0), tr.rotationX(np.pi/2)])

    plateGroupNode = sg.SceneGraphNode("grupo_placas")
    plateGroupNode.childs = [plateTrNode1, plateTrNode2, plateTrNode3, plateTrNode4]
    return plateGroupNode

def createGPUCube(pipeline, left, right, top, bottom, near, far):
    cubeShape = csh.createBoundaryBoxTest(left, right, top, bottom, near, far)
    gpuCube = createGPUShape(cubeShape, pipeline)
    cubeNode = sg.SceneGraphNode("cubo")
    cubeNode.childs = [gpuCube]
    return cubeNode

def createTexQuads(pipeline, n, img_file):
    finalNode = sg.SceneGraphNode("quads")
    finalNode.childs = []
    quadShape = csh.createTextureNormalsQuad(1, 1)
    gpuQuad = createTextureGPUShape(quadShape, pipeline, img_file)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                quadNode = sg.SceneGraphNode("quad_"+str(i)+str(j)+str(k))
                quadNode.childs = [gpuQuad]

                quadRotatedNode = sg.SceneGraphNode("quad_r"+str(i)+str(j)+str(k))
                quadRotatedNode.childs = [quadNode]
                quadRotatedNode.transform = tr.matmul([tr.translate(0.2*i, 0.2*j, 0.2*k), tr.rotationY(np.pi/2), tr.uniformScale(0.2)])
                finalNode.childs += [quadRotatedNode]
    return finalNode