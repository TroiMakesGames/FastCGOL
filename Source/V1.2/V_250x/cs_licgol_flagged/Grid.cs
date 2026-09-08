// grid class that manages pretty much everything along the lines of the CGOL implementation

using System;
using System.IO;    //file reading

class Grid
{
    int worldWidth;
    int worldHeight;
    int cellSize;

    public bool[] grid;
    private bool[] newGrid;                     //double buffer for less allocation
    private int[] checkedGeneration;
    private int generation;
    private int[] activeCoords;
    private int[] newActiveCoords;              //    -||-
    private int activeCount;

    private (int X, int Y)[] neighbors;

    public Grid(int wrldWidth, int wrldHeight, int cllSize)
    {
        worldWidth = wrldWidth;
        worldHeight = wrldHeight;
        cellSize = cllSize;

        grid = new bool[worldWidth * worldHeight];
        newGrid = new bool[worldWidth * worldHeight];
        activeCoords = new int[worldWidth * worldHeight * 9];
        newActiveCoords = new int[worldWidth * worldHeight * 9];
        activeCount = 0;
        //this implementation of the flagged licgol differs from cr because in cr appending to an array is cheaper
        //instead of expensively appending using Linq, here we preinitialise extra space and track how much of the array has been used using activeCount 
        
        //flaggedArray has been replaced with a generation count to replace having to clear the flag array each iteration
        //  we keep track of the last generation that a cell at i j has been checked and only compute when the number is lagging behind (on global gen 18 if a cell has been proccesed at gen 17 last it means it hasnt yet been proccessed on gen 18)
        checkedGeneration = new int[worldWidth * worldHeight];
        generation = 1;

        neighbors = new (int X, int Y)[] {
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
        };

        //add every cell to active coords
        for (int i = 0; i < worldWidth; i++)
        {
            for (int j = 0; j < worldHeight; j++)
            {activeCoords[activeCount++] = i + j * worldWidth;}
        }
        

        //read from common seed data
        string seedData = File.ReadAllText("Assets/seed.txt");

        for (int i = 0; i < worldWidth * worldHeight; i++)
        {
            if (seedData[i] == '1')
            {grid[i] = true;}
        }
    }

    public void Update()
    {
        //create copy grid and new active coords array, (REPLACED with generation tracking: clear flag arraay)
        bool[] newGrid = (bool[])grid.Clone();
        int[] newActiveCoords = new int[activeCount * 9];
        int newActiveCount = 0;

        // check each cell
        for (int i = 0; i < activeCount; i++)
        {
            int index = activeCoords[i];

            //only compute if hanst computed already
            if (checkedGeneration[index] != generation)
            {
                // get live count
                int liveCount = 0;

                for (int n = 0; n < 8; n++)
                {
                    //get neigbhor coord and loop over edges
                    int nX = index % worldWidth + neighbors[n].X;
                    int nY = index / worldWidth + neighbors[n].Y;

                    //use if statments + math instead of modulo (%) because modulo is expensive
                    if (nX < 0)
                    {nX = worldWidth - 1;}
                    else if (nX >= worldWidth)
                    {nX = 0;}

                    if (nY < 0)
                    {nY = worldHeight - 1;}
                    else if (nY >= worldHeight)
                    {nY = 0;}

                    int nIndex = nX + nY * worldWidth;

                    // check
                    if (grid[nIndex])
                    {liveCount++;}
                }

                // check rules - extremely shortened version from the original double nested if statements
                bool newState = liveCount == 3 || (grid[index] && liveCount == 2);
                newGrid[index] = newState;

                //relevance check
                if (newGrid[index] != grid[index])
                {
                    //add currcoord to active coords
                    newActiveCoords[newActiveCount++] = index;

                    //also add all neighbors
                    for (int n = 0; n < 8; n++)
                    {
                        //get neigbhor coord and loop over edges
                        int nX = index % worldWidth + neighbors[n].X;
                        int nY = index / worldWidth + neighbors[n].Y;

                        //use if statments + math instead of modulo (%) because modulo is expensive
                        if (nX < 0)
                        {nX = worldWidth - 1;}
                        else if (nX >= worldWidth)
                        {nX = 0;}

                        if (nY < 0)
                        {nY = worldHeight - 1;}
                        else if (nY >= worldHeight)
                        {nY = 0;}

                        newActiveCoords[newActiveCount++] = nX + nY * worldWidth;
                    }
                }

                checkedGeneration[index] = generation;
            }
        }

        //swap double buffers
        var tempGrid = grid;
        grid = newGrid;
        newGrid = tempGrid;

        var tempActive = activeCoords;
        activeCoords = newActiveCoords;
        newActiveCoords = tempActive;

        activeCount = newActiveCount;

        generation++;
    }

    //grid.Draw() is replaced with DrawGrid in Program.cs because it has direct acces to the rendering pipeline
    //  additionaly, the old DrawRectangle() method of drawing each idnividual pixel was suboptimal
}