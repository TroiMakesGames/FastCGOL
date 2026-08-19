//grid class that manages pretty much everything along the lines of the cgol implementation

class Grid
{
    int worldWidth;
    int worldHeight;
    int cellSize;

    public bool[,] grid;

    public Grid(int wrldWidth, int wrldHeight, int cllSize)
    {
        worldWidth = wrldWidth;
        worldHeight = wrldHeight;
        cellSize = cllSize;

        grid = new bool[worldWidth, worldWidth];
    }

    public void Update()
    {
        // update stuff
    }

    public void Draw()
    {
        for (int i = 0; i < worldWidth; i++) 
        {
            for (int j = 0; j < worldHeight; j++) 
            {
                if (grid[i, j]) 
                {
                    Program.DrawRectangle(cellSize * i, cellSize * j, cellSize, cellSize);
                }
            }
        }
    }
}