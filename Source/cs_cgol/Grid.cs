// grid class that manages pretty much everything along the lines of the CGOL implementation

using System;
using System.IO;    //file reading

class Grid
{
    int worldWidth;
    int worldHeight;
    int cellSize;

    public bool[] grid;

    private (int X, int Y)[] neighbors;

    public Grid(int wrldWidth, int wrldHeight, int cllSize)
    {
        worldWidth = wrldWidth;
        worldHeight = wrldHeight;
        cellSize = cllSize;

        grid = new bool[worldWidth * worldHeight];

        neighbors = new (int X, int Y)[] {
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
        };

        /* Initial random seed 
        Random random = new Random();

        for (int i = 0; i < worldWidth; i++)
        {
            for (int j = 0; j < worldHeight; j++)
            {
                int index = i + j * worldWidth;
                grid[index] = random.Next(2) == 0;
            }
        }
        */

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
        // create new grid
        bool[] newGrid = new bool[worldWidth * worldHeight];

        // check each cell
        for (int i = 0; i < worldWidth; i++)
        {
            for (int j = 0; j < worldHeight; j++)
            {
                // get live count
                int liveCount = 0;

                for (int n = 0; n < 8; n++)
                {
                    //get neigbhor coord and loop over edges
                    int nX = i + neighbors[n].X;
                    int nY = j + neighbors[n].Y;

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

                // current cell index
                int index = i + j * worldWidth;

                // check rules
                if (grid[index])
                {
                    if (liveCount < 2)
                    {newGrid[index] = false;}

                    if (liveCount == 3 || liveCount == 2)
                    {newGrid[index] = true;}

                    if (liveCount > 3)
                    {newGrid[index] = false;}
                }
                else
                {
                    if (liveCount == 3)
                    {newGrid[index] = true;}
                }
            }
        }

        grid = newGrid;
    }

    //grid.Draw() is replaced with DrawGrid in Program.cs because it has direct acces to the rendering pipeline
    //  additionaly, the old DrawRectangle() method of drawing each idnividual pixel was suboptimal
}