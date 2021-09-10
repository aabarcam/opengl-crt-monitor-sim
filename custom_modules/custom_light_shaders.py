from OpenGL.GL import *
import OpenGL.GL.shaders
from grafica.gpu_shape import GPUShape


class SimpleStatePhongShaderProgram:

    def __init__(self):
        vertex_shader = """
            #version 330 core

            layout (location = 0) in vec3 position;
            layout (location = 1) in vec3 color;
            layout (location = 2) in vec3 normal;

            out vec3 fragPosition;
            out vec3 fragOriginalColor;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragOriginalColor = color;
                fragNormal = mat3(transpose(inverse(model))) * normal;  
                
                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = """
            #version 330 core

            out vec4 fragColor;

            in vec3 fragNormal;
            in vec3 fragPosition;
            in vec3 fragOriginalColor;
            
            uniform vec3 lightPosition; 
            uniform vec3 viewPosition;
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;


            void main()
            {
                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse
                // fragment normal has been interpolated, so it does not necessarily have norm equal to 1
                vec3 normalizedNormal = normalize(fragNormal);
                vec3 toLight = lightPosition - fragPosition;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(normalizedNormal, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - fragPosition);
                vec3 reflectDir = reflect(-lightDir, normalizedNormal);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                    
                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * fragOriginalColor;
                fragColor = vec4(result, 1.0);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

def default_light_settings(pipeline, settings):
    camera = settings[0]
    ka = settings[1]
    kd = settings[2]
    ks = settings[3]
    projection = settings[4]
    viewMatrix = settings[5]
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 0.25, 0.25, 0.25)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.0005)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.005)
    
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), ka[0], ka[1], ka[2])
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), kd[0], kd[1], kd[2])
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), ks[0], ks[1], ks[2])

    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)


class MultiplePhongShaderProgram:
    # Pipeline para multiples fuentes de luz, sin texturas

    def __init__(self):
        vertex_shader = """
            #version 330 core

            layout (location = 0) in vec3 position;
            layout (location = 1) in vec3 color;
            layout (location = 2) in vec3 normal;

            out vec3 fragPosition;
            out vec3 fragOriginalColor;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragOriginalColor = color;
                fragNormal = mat3(transpose(inverse(model))) * normal;  
                
                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = """
            #version 330 core

            out vec4 fragColor;

            in vec3 fragNormal;
            in vec3 fragPosition;
            in vec3 fragOriginalColor;
            
            // Posiciones de las fuentes de luz 

            uniform vec3 lightPos[17];
            uniform int lights;

            uniform vec3 viewPosition;
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;

            void main()
            {
                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse
                // fragment normal has been interpolated, so it does not necessarily have norm equal to 1
                vec3 normalizedNormal = normalize(fragNormal);

                // Vector para sumar la contribucion de cada fuente de luz
                vec3 result = vec3(0.0f, 0.0f, 0.0f);

                // Se itera por cada fuente de luz para calcular su contribucion
                for (int i = 0; i < lights; i++)
                {   
                    // direccion a la fuente de luz de la iteacion actual
                    vec3 toLight = lightPos[i] - fragPosition;

                    // Lo demas es exactamente igual
                    vec3 lightDir = normalize(toLight);
                    float diff = max(dot(normalizedNormal, lightDir), 0.0);
                    vec3 diffuse = Kd * Ld * diff;
                    
                    // specular
                    vec3 viewDir = normalize(viewPosition - fragPosition);
                    vec3 reflectDir = reflect(-lightDir, normalizedNormal);  
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                    vec3 specular = Ks * Ls * spec;

                    // attenuation
                    float distToLight = length(toLight);
                    float attenuation = constantAttenuation
                        + linearAttenuation * distToLight
                        + quadraticAttenuation * distToLight * distToLight;
                        
                    // Se suma la contribucion calculada en la iteracion actual
                    result += ((diffuse + specular) / attenuation) ;
                }

                // El calculo final es con la suma final
                result = (ambient + result ) * fragOriginalColor;
                fragColor = vec4(result, 1.0);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

class SimpleTextureShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    def setupVAO(self, gpuShape):
        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)
        
        # Unbind the current VAO
        glBindVertexArray(0)