//main script

using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.Common;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

using System.Collections.Generic;
using System.Diagnostics;   //measuring and logging performance data

class Program : GameWindow
{
    /* SETUP + simple draw function - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

    static int shaderProgram;

    //sim logic vars
    static int computeProgram;

    static int gridBufferA;
    static int gridBufferB;

    static int currentBuffer;
    static int nextBuffer;

    //gpu rendering single texture global vao
    static int fullscreenVao;

    //removing hardcoded world resolution
    const int WorldWidth = 250;
    const int WorldHeight = 150;

    //since GPU included or not differs so much, use a flag to determine
    const bool benchmarkMode = true;

    protected override void OnLoad() 
    {
        GL.ClearColor(0.1f, 0.1f, 0.1f, 1);

        shaderProgram = CreateShaderProgram(
            "Shaders/rectangle.vert",
            "Shaders/rectangle.frag"
        );

        //load comp shader
        computeProgram = CreateComputeProgram(
            "Shaders/gameoflife.comp"
        );

        CreateGridBuffers();

        fullscreenVao = GL.GenVertexArray();
    }

    int CreateComputeProgram(string path)
    {
        int shader = GL.CreateShader(ShaderType.ComputeShader);

        GL.ShaderSource(shader, File.ReadAllText(path));
        GL.CompileShader(shader);

        string infoLog = GL.GetShaderInfoLog(shader);

        if (!string.IsNullOrWhiteSpace(infoLog))
            Console.WriteLine(infoLog);

        int program = GL.CreateProgram();

        GL.AttachShader(program, shader);
        GL.LinkProgram(program);

        GL.DeleteShader(shader);

        return program;
    }

    public static void DrawGrid(int shaderProgram)
    {
        GL.UseProgram(shaderProgram);
        GL.BindVertexArray(fullscreenVao);

        int widthLocation = GL.GetUniformLocation(
            shaderProgram,
            "width"
        );

        int heightLocation = GL.GetUniformLocation(
            shaderProgram,
            "height"
        );

        GL.Uniform1(widthLocation, WorldWidth);
        GL.Uniform1(heightLocation, WorldHeight);

        GL.DrawArrays(
            PrimitiveType.Triangles,
            0,
            6
        );
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

    //measuring performance data
    //benchmark data collection is done in  groups instead of per-iteration to minimize GPU desync problems
    const int benchmarkGroupSize = 100;
    int generationCount = 0;
    int maxGenerationCount = 10000;
    long[] times = new long[10000 / benchmarkGroupSize];
    Stopwatch stopwatch = new Stopwatch();

    public Program(): base(GameWindowSettings.Default, new NativeWindowSettings{ClientSize = new Vector2i(750, 450), Title = "Fast Conways Game of Life"}) 
    {
        grid = new Grid(250, 150, 3);
    }

    protected override void OnUpdateFrame(FrameEventArgs args) 
    {
        //end case return
        if (generationCount >= maxGenerationCount)
        {
            GL.Finish();

            Close();
            return;
        }

        if (generationCount % benchmarkGroupSize == 0)
        {
            GL.Finish();        //wait for prev GPU comp call to finish to prevent split data
            stopwatch.Restart();
        }

        //grid.Update();
        UpdateGPU();        //run comp shader simulation logic
        //ReadGPUGrid();      //read computed state
        //  not required with no GPU comp shader - CPU grid.grid translation (GPU is rendered directly)

        generationCount++;

        if (generationCount % benchmarkGroupSize == 0)
        {
            GL.Finish();
            stopwatch.Stop();
            times[(generationCount / benchmarkGroupSize) - 1] = stopwatch.ElapsedTicks;
        }
    }

    protected override void OnRenderFrame(FrameEventArgs args)
    {
        //remove rendering from full build
        if (benchmarkMode) {return;}

        GL.Clear(ClearBufferMask.ColorBufferBit);

        GL.BindBufferBase(
            BufferRangeTarget.ShaderStorageBuffer,
            0,
            currentBuffer
        );

        DrawGrid(shaderProgram);

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

    //writting performance data after finishing
    protected override void OnUnload()
    {
        using (StreamWriter writer = new StreamWriter("data_cs_cgol_shader.txt"))
        {
            int groupCount = generationCount / benchmarkGroupSize;

            for (int i = 0; i < groupCount; i++)
            {
                //since gpu desync solution generates groups ... each group must get split into the avarage
                double groupMilliseconds = (double)times[i] / Stopwatch.Frequency * 1000.0;
                double averageMilliseconds = groupMilliseconds / benchmarkGroupSize;

                //write the avarage multiple times
                for (int j = 0; j < benchmarkGroupSize; j++)
                {writer.WriteLine(averageMilliseconds);}
            }
        }

        base.OnUnload();
    }

    //instantiate comp shader grid buffers
    void CreateGridBuffers()
    {
        uint[] initialGrid = new uint[WorldWidth * WorldHeight];

        for (int i = 0; i < initialGrid.Length; i++)
        {
            initialGrid[i] = grid.grid[i] ? 1u : 0u;
        }

        gridBufferA = GL.GenBuffer();

        GL.BindBuffer(
            BufferTarget.ShaderStorageBuffer,
            gridBufferA
        );

        GL.BufferData(
            BufferTarget.ShaderStorageBuffer,
            initialGrid.Length * sizeof(uint),
            initialGrid,
            BufferUsageHint.DynamicDraw
        );


        gridBufferB = GL.GenBuffer();

        GL.BindBuffer(
            BufferTarget.ShaderStorageBuffer,
            gridBufferB
        );

        GL.BufferData(
            BufferTarget.ShaderStorageBuffer,
            initialGrid.Length * sizeof(uint),
            IntPtr.Zero,
            BufferUsageHint.DynamicDraw
        );


        currentBuffer = gridBufferA;
        nextBuffer = gridBufferB;
    }

    void UpdateGPU()
    {
        GL.UseProgram(computeProgram);

        int widthLocation = GL.GetUniformLocation(
            computeProgram,
            "width"
        );

        int heightLocation = GL.GetUniformLocation(
            computeProgram,
            "height"
        );

        GL.Uniform1(widthLocation, WorldWidth);
        GL.Uniform1(heightLocation, WorldHeight);


        GL.BindBufferBase(
            BufferRangeTarget.ShaderStorageBuffer,
            0,
            currentBuffer
        );

        GL.BindBufferBase(
            BufferRangeTarget.ShaderStorageBuffer,
            1,
            nextBuffer
        );

        int groupsX = (WorldWidth + 15) / 16;
        int groupsY = (WorldHeight + 15) / 16;

        GL.DispatchCompute(
            groupsX,
            groupsY,
            1
        );

        GL.MemoryBarrier(
            MemoryBarrierFlags.ShaderStorageBarrierBit
        );

        //swap bufers
        int temp = currentBuffer;
        currentBuffer = nextBuffer;
        nextBuffer = temp;
    }

    //get gpu computed grid into renderable vars
    void ReadGPUGrid()
    {
        uint[] gpuGrid = new uint[WorldWidth * WorldHeight];

        GL.BindBuffer(
            BufferTarget.ShaderStorageBuffer,
            currentBuffer
        );

        GL.GetBufferSubData(
            BufferTarget.ShaderStorageBuffer,
            IntPtr.Zero,
            gpuGrid.Length * sizeof(uint),
            gpuGrid
        );

        for (int i = 0; i < gpuGrid.Length; i++)
        {
            grid.grid[i] = gpuGrid[i] != 0;
        }
    }
}