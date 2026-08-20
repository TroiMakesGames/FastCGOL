//main script

using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.Common;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

using System.Collections.Generic;

class Program : GameWindow
{
    /* SETUP + simple draw function - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

    static int shaderProgram;

    protected override void OnLoad() 
    {
        GL.ClearColor(0.1f, 0.1f, 0.1f, 1);

        shaderProgram = CreateShaderProgram(
            "Shaders/rectangle.vert",
            "Shaders/rectangle.frag"
        );
    }

    public static void DrawGrid(bool[] grid, int worldWidth, int worldHeight, int cellSize)
    {
        List<float> vertices = new List<float>();

        for (int i = 0; i < worldWidth; i++)
        {
            for (int j = 0; j < worldHeight; j++)
            {
                int index = i + j * worldWidth;

                if (!grid[index])
                    continue;

                float x = cellSize * i;
                float y = cellSize * j;

                float left   = (x / 750f) * 2f - 1f;
                float right  = ((x + cellSize) / 750f) * 2f - 1f;
                float top    = 1f - (y / 450f) * 2f;
                float bottom = 1f - ((y + cellSize) / 450f) * 2f;

                // Triangle 1
                vertices.Add(left);
                vertices.Add(top);

                vertices.Add(left);
                vertices.Add(bottom);

                vertices.Add(right);
                vertices.Add(bottom);

                // Triangle 2
                vertices.Add(left);
                vertices.Add(top);

                vertices.Add(right);
                vertices.Add(bottom);

                vertices.Add(right);
                vertices.Add(top);
            }
        }

        int vao = GL.GenVertexArray();
        int vbo = GL.GenBuffer();

        GL.BindVertexArray(vao);
        GL.BindBuffer(BufferTarget.ArrayBuffer, vbo);

        GL.BufferData(
            BufferTarget.ArrayBuffer,
            vertices.Count * sizeof(float),
            vertices.ToArray(),
            BufferUsageHint.StreamDraw
        );

        GL.VertexAttribPointer(
            0,
            2,
            VertexAttribPointerType.Float,
            false,
            2 * sizeof(float),
            0
        );

        GL.EnableVertexAttribArray(0);

        GL.UseProgram(shaderProgram);

        GL.DrawArrays(
            PrimitiveType.Triangles,
            0,
            vertices.Count / 2
        );

        GL.DeleteBuffer(vbo);
        GL.DeleteVertexArray(vao);
    }

    int CreateShaderProgram(string vertexPath, string fragmentPath) 
    {
        int vertexShader = CreateShader(
            ShaderType.VertexShader,
            vertexPath
        );

        int fragmentShader = CreateShader(
            ShaderType.FragmentShader,
            fragmentPath
        );

        int program = GL.CreateProgram();

        GL.AttachShader(program, vertexShader);
        GL.AttachShader(program, fragmentShader);

        GL.LinkProgram(program);

        GL.DeleteShader(vertexShader);
        GL.DeleteShader(fragmentShader);

        return program;
    }

    int CreateShader(ShaderType type, string path) 
    {
        int shader = GL.CreateShader(type);

        GL.ShaderSource(shader, File.ReadAllText(path));
        GL.CompileShader(shader);

        return shader;
    }

    static void Main() 
    {
        using var window = new Program();
        window.Run();
    }

    /* INSTANTIATION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

    Grid grid;

    int frameCount = 0;
    double fpsTimer = 0;

    public Program(): base(GameWindowSettings.Default, new NativeWindowSettings{ClientSize = new Vector2i(750, 450), Title = "Fast Conways Game of Life"}) 
    {
        grid = new Grid(250, 150, 3);
    }

    protected override void OnUpdateFrame(FrameEventArgs args) 
    {
        grid.Update();
    }

    protected override void OnRenderFrame(FrameEventArgs args) 
    {
        GL.Clear(ClearBufferMask.ColorBufferBit);

        DrawGrid(
            grid.grid,
            250,
            150,
            3
        );

        SwapBuffers();

        frameCount++;
        fpsTimer += args.Time;

        if (fpsTimer >= 1.0f)
        {
            Title = $"Fast Conways Game of Life - FPS: {frameCount}";

            frameCount = 0;
            fpsTimer = 0;
        }
    }
}