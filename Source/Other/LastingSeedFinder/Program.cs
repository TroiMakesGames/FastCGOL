//main script

using OpenTK.Windowing.Desktop;
using OpenTK.Windowing.Common;
using OpenTK.Graphics.OpenGL4;
using OpenTK.Mathematics;

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
    const int WorldWidth = 1600;
    const int WorldHeight = 1600;

    int generationCount = 0;
    int simCount = 1;

    Grid grid;
    int longestGeneration = 0;
    bool[] longestGrid = null;

    int logTime = 100;

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

    public Program(): base(GameWindowSettings.Default, new NativeWindowSettings
        {
            ClientSize = new Vector2i(WorldWidth, WorldHeight),
            Title = "CGOL - Long Lasting Seed Finder"
        }) 
    {
        grid = new Grid(WorldWidth, WorldHeight, 1);
        grid.CheckForLoop(0);
    }

    protected override void OnUpdateFrame(FrameEventArgs args) 
    {
        //manual stop
        if (KeyboardState.IsKeyDown(OpenTK.Windowing.GraphicsLibraryFramework.Keys.Escape))
        {
            Console.WriteLine($"Longest simulation found: {longestGeneration} generations.");

            Close();
            return;
        }

        UpdateGPU();
        ReadGPUGrid();

        generationCount++;

        if (generationCount % logTime == 0)
        {Console.WriteLine($"Ran {generationCount}...");}

        if (grid.CheckForLoop(generationCount))
        {
            Console.WriteLine($"Seed finished after {generationCount} generations.");

            //check fi longest so far
            if (generationCount > longestGeneration)
            {
                longestGeneration = generationCount;

                //copy wolrd data of longest
                longestGrid = (bool[])grid.startSeedData.Clone();

                Console.WriteLine($"NEW LONGEST SEED: {longestGeneration} generations!");
            }

            //save longest
            SaveSeed(grid);

            Console.WriteLine($"Longest simulation so far: {longestGeneration} generations.");

            Console.WriteLine(" ");

            //start new random seed
            StartNewSimulation();

            Console.WriteLine("Starting new seed...");
        }
    }

    protected override void OnRenderFrame(FrameEventArgs args)
    {
        /*
        GL.Clear(ClearBufferMask.ColorBufferBit);

        GL.BindBufferBase(
            BufferRangeTarget.ShaderStorageBuffer,
            0,
            currentBuffer
        );

        DrawGrid(shaderProgram);

        SwapBuffers();
        */
    }

    //writting performance data after finishing
    protected override void OnUnload()
    {
        /*
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
        */

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

    //reset gpu after prev sim
    void StartNewSimulation()
    {
        grid.NewSeed();

        generationCount = 0;

        uint[] initialGrid = new uint[WorldWidth * WorldHeight];

        for (int i = 0; i < initialGrid.Length; i++)
        {
            initialGrid[i] = grid.grid[i] ? 1u : 0u;
        }

        //reset to buffer A
        currentBuffer = gridBufferA;
        nextBuffer = gridBufferB;

        //upload new seed
        GL.BindBuffer(
            BufferTarget.ShaderStorageBuffer,
            currentBuffer
        );

        GL.BufferSubData(
            BufferTarget.ShaderStorageBuffer,
            IntPtr.Zero,
            initialGrid.Length * sizeof(uint),
            initialGrid
        );
    }

    void SaveSeed(Grid grid)
    {
        using StreamWriter writer = new StreamWriter($"seed_{simCount}_{generationCount}.txt");

        for (int i = 0; i < grid.startSeedData.Length; i++)
        {writer.Write(grid.startSeedData[i] ? '1' : '0');}

        writer.WriteLine();

        simCount++;
    }
}