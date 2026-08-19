//main script

using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.Common;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

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

    public static void DrawRectangle(float x, float y, float width, float height) 
    {
        float left   = (x / 800f) * 2f - 1f;
        float right  = ((x + width) / 800f) * 2f - 1f;
        float top    = 1f - (y / 600f) * 2f;
        float bottom = 1f - ((y + height) / 600f) * 2f;

        float[] vertices =
        {
            left,  top,
            left,  bottom,
            right, bottom,

            left,  top,
            right, bottom,
            right, top
        };

        int vao = GL.GenVertexArray();
        int vbo = GL.GenBuffer();

        GL.BindVertexArray(vao);
        GL.BindBuffer(BufferTarget.ArrayBuffer, vbo);

        GL.BufferData(
            BufferTarget.ArrayBuffer,
            vertices.Length * sizeof(float),
            vertices,
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
            6
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

    public Program(): base(GameWindowSettings.Default, new NativeWindowSettings{ClientSize = new Vector2i(800, 600), Title = "Fast Conways Game of Life"}) 
    {
        grid = new Grid(80, 60, 10);
        grid.grid[5, 2] = true;
    }

    protected override void OnUpdateFrame(FrameEventArgs args) 
    {
        grid.Update();
    }

    protected override void OnRenderFrame(FrameEventArgs args) 
    {
        GL.Clear(ClearBufferMask.ColorBufferBit);

        grid.Draw();

        SwapBuffers();
    }
}