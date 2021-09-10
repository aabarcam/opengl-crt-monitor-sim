from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import grafica.transformations as tr
import grafica.gpu_shape as gs

import custom_modules.custom_light_shaders as cls

class CustomSceneGraphNode:
    # Se modifica para tener un atributo extra curr_pipeline de pipeline actual para admitir distintos pipelines en un solo grafo
    """
    A simple class to handle a scene graph
    Each node represents a group of objects
    Each leaf represents a basic figure (GPUShape)
    To identify each node properly, it MUST have a unique name
    """
    def __init__(self, name):
        self.name = name
        self.transform = tr.identity()
        self.childs = []
        self.curr_pipeline = None
        self.attributes = None
        self.attr_names = None

    def clear(self):
        """Freeing GPU memory"""

        for child in self.childs:
            child.clear()
    


def findNode(node, name):

    # The name was not found in this path
    if isinstance(node, gs.GPUShape):
        return None

    # This is the requested node
    if node.name == name:
        return node
    
    # All childs are checked for the requested name
    for child in node.childs:
        foundNode = findNode(child, name)
        if foundNode != None:
            return foundNode

    # No child of this node had the requested name
    return None


def findTransform(node, name, parentTransform=tr.identity()):

    # The name was not found in this path
    if isinstance(node, gs.GPUShape):
        return None

    newTransform = np.matmul(parentTransform, node.transform)

    # This is the requested node
    if node.name == name:
        return newTransform
    
    # All childs are checked for the requested name
    for child in node.childs:
        foundTransform = findTransform(child, name, newTransform)
        if isinstance(foundTransform, (np.ndarray, np.generic) ):
            return foundTransform

    # No child of this node had the requested name
    return None


def findPosition(node, name, parentTransform=tr.identity()):
    foundTransform = findTransform(node, name, parentTransform)

    if isinstance(foundTransform, (np.ndarray, np.generic) ):
        zero = np.array([[0,0,0,1]], dtype=np.float32).T
        foundPosition = np.matmul(foundTransform, zero)
        return foundPosition

    return None


def drawCustomSceneGraphNode(node, pipeline, transformName, light_settings, parentTransform=tr.identity()):
    # Dibujara los nodos con el pipeline que se encuentre en el atributo curr_pipeline para usar distintos shaders en un solo grafo
    assert(isinstance(node, CustomSceneGraphNode))

    # Composing the transformations through this path
    newTransform = np.matmul(parentTransform, node.transform)
    
    if node.curr_pipeline != None: # cambia el pipeline a usar por el resto del sub grafo
        print(node.name)
        pipeline = node.curr_pipeline
        glUseProgram(pipeline.shaderProgram)
        cls.default_light_settings(pipeline, light_settings)
    # If the child node is a leaf, it should be a GPUShape.
    # Hence, it can be drawn with drawCall
    if len(node.childs) == 1 and isinstance(node.childs[0], gs.GPUShape):
        leaf = node.childs[0]
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, transformName), 1, GL_TRUE, newTransform)
        if node.attributes != None:
            for i in range(len(node.attributes)):
                # print(pipeline, node.curr_pipeline, node.name, node.attributes, node.attr_names)
                glUniform1f(glGetUniformLocation(pipeline.shaderProgram, node.attr_names[i]), node.attributes[i])
        # glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "green"), node.green)
        pipeline.drawCall(leaf)
    # If the child node is not a leaf, it MUST be a SceneGraphNode,
    # so this draw function is called recursively
    else:
        for child in node.childs:
            drawCustomSceneGraphNode(child, pipeline, transformName, light_settings, newTransform)

