// grid class that manages pretty much everything along the lines of the CGOL implementation

using System;
using System.IO;    //file reading

class Grid
{
    int worldWidth;
    int worldHeight;
    int cellSize;

    public bool[] grid;
    public HashSet<(int X, int Y)> activeCoords;

    private (int X, int Y)[] neighbors;

    public Grid(int wrldWidth, int wrldHeight, int cllSize)
    {
        worldWidth = wrldWidth;
        worldHeight = wrldHeight;
        cellSize = cllSize;

        grid = new bool[worldWidth * worldHeight];
        activeCoords = new();

        neighbors = new (int X, int Y)[] {
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
        };

        //add every cell to active coords
        for (int i = 0; i < worldWidth; i++)
        {
            for (int j = 0; j < worldHeight; j++)
            {activeCoords.Add((i, j));}
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
        //create copy grid and new hashset
        bool[] newGrid = (bool[])grid.Clone();
        HashSet<(int X, int Y)> newActiveCoords = new();

        // check each cell
        foreach (var currCoord in activeCoords)
        {
            // get live count
            int liveCount = 0;

            for (int n = 0; n < 8; n++)
            {
                //get neigbhor coord and loop over edges
                int nX = currCoord.X + neighbors[n].X;
                int nY = currCoord.Y + neighbors[n].Y;

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
            int index = currCoord.X + currCoord.Y * worldWidth;

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

            //relevance check
            if (newGrid[index] != grid[index])
            {
                //add currcoord to active coords
                newActiveCoords.Add(currCoord);

                //also add all neighbors
                for (int n = 0; n < 8; n++)
                {
                    //get neigbhor coord and loop over edges
                    int nX = currCoord.X + neighbors[n].X;
                    int nY = currCoord.Y + neighbors[n].Y;

                    //use if statments + math instead of modulo (%) because modulo is expensive
                    if (nX < 0)
                    {nX = worldWidth - 1;}
                    else if (nX >= worldWidth)
                    {nX = 0;}

                    if (nY < 0)
                    {nY = worldHeight - 1;}
                    else if (nY >= worldHeight)
                    {nY = 0;}

                    newActiveCoords.Add((nX, nY));
                }
            }
        }

        grid = newGrid;
        activeCoords = newActiveCoords;
    }

    //grid.Draw() is replaced with DrawGrid in Program.cs because it has direct acces to the rendering pipeline
    //  additionaly, the old DrawRectangle() method of drawing each idnividual pixel was suboptimal
}