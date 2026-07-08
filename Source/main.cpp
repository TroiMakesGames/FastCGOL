#include "raylib.h"     //raylib framework/library
#include <vector>       //includes type dynamic arrays called vectors in c++
#include <iostream>     //console logging
#include <cmath>        //math stuff like floor()
#include <random>       //random

//set randomness stuff
std::random_device rd;
std::mt19937 gen(rd());

class Grid 
{
    public:
        //1D array for the grid
        std::vector<int> grid;

        int worldWidth;
        int worldHeight;

    private:
        int cellSize = 1;
        
        int screenWidth;
        int screenHeight;

        std::vector<Vector2> activeCoords;

        //neighboring coords
        const Vector2 neighbors[8] = {
            {-1, -1}, { 0, -1}, { 1, -1},
            {-1,  0},           { 1,  0},
            {-1,  1}, { 0,  1}, { 1,  1}
        };

    public:
    // constructor with parameters
    Grid(int screenWidth, int screenHeight, int cellSize) {
        this->cellSize = cellSize;
        this->screenWidth = screenWidth;
        this->screenHeight = screenHeight;

        //calculate world width and height
        worldWidth = screenWidth / cellSize;
        worldHeight = screenHeight / cellSize;

        //resize grid array
        int totalCells = worldWidth * worldHeight;
        grid.resize(totalCells);

        //set random values for start
        for (int i = 0; i < totalCells; i++)
        {grid[i] = std::uniform_int_distribution<int>(0, 1)(gen);}

        //set initial active cells
        for (int i = i; i < totalCells; i++)
        {
            Vector2 coord = intToCoord(i);
            activeCoords.push_back(coord);
        }
    }

    //2D coordinate to 1D index
    int coordToInt(Vector2 coord)
    {return worldWidth * coord.y + coord.x;}
    
    //1D index to 2D coordinate
    Vector2 intToCoord(int i)
    {return Vector2(i % worldWidth, i / worldWidth);}

    void draw() {
        for (int i = 0; i < worldWidth * worldHeight; i++)
        {
            if (grid[i] == 1)
            {
                Vector2 coord = intToCoord(i);
                DrawRectangle(cellSize * coord.x, cellSize * coord.y, cellSize, cellSize, Color{255, 255, 255, 255});
            }
        }
    }

    void updateGrid()
    {
        //create new array full of 0 integers
        std::vector<int> newGrid = grid;
        std::vector<Vector2> newActiveCoords;

        //check each cell
        for (int i = 0; i < activeCoords.size(); i++)
        {
            int liveCount = 0;
            for (int j = 0; j < 8; j++)
            {
                //get neighboring coord
                Vector2 coord = activeCoords[i];
                coord.x += neighbors[j].x;
                coord.y += neighbors[j].y;
                int neighboringIndex = coordToInt(coord);

                //check if coord within world
                if (coord.x < 0 || coord.x > worldWidth - 1 || coord.y < 0 || coord.y > worldHeight - 1)
                {break;}

                if (grid[neighboringIndex] == 1)
                {liveCount += 1;}
            }

            //check for rules
            int indx = coordToInt(activeCoords[i]);
            if (grid[indx] == 1)
            {
                if (liveCount < 2)
                {newGrid[indx] = 0;}
                else if (liveCount == 2 || liveCount == 3)
                {newGrid[indx] = 1;}
                else if (liveCount > 3)
                {newGrid[indx] = 0;}
            }
            else if (grid[indx] == 0)
            {
                if (liveCount == 3)
                {newGrid[indx] = 1;}
            }

            //relevance check
            if (newGrid[indx] != grid[indx])
            {
                newActiveCoords.push_back(intToCoord(indx));

                //also add all neighbors
                for (int j = 0; j < 8; j++)
                {
                    //get neighboring coord
                    Vector2 ncoord = intToCoord(indx);
                    ncoord.x += neighbors[j].x;
                    ncoord.y += neighbors[j].y;
                    
                    //check if ncoord already exists
                    bool exists = false;
                    for (int k = 0; k < newActiveCoords.size(); k++)
                    {
                        if (newActiveCoords[k].x == ncoord.x && newActiveCoords[k].y == ncoord.y)
                        {
                            exists = true;
                            break;
                        }
                    }

                    if (!exists)
                    {newActiveCoords.push_back(ncoord);}
                }
            }
        }

        //update current grid and active coords array
        grid = newGrid;
        activeCoords = newActiveCoords;
    }
};

int main() {
    //screen initialisation
    const int WIDTH = 800;
    const int HEIGHT = 600;
    InitWindow(WIDTH, HEIGHT, "Fast Conways Game of Life");
    SetTargetFPS(60);

    //variable initialisation

    int cellSize = 1;
    Grid grid = Grid(WIDTH, HEIGHT, cellSize);
    //grid.grid[grid.worldWidth * 7 + 11] = 1;

    //while loop
    while (!WindowShouldClose()) {

        // update
        grid.updateGrid();

        // draw
        BeginDrawing();
        ClearBackground(Color{30, 30, 30, 255});

        grid.draw();

        DrawText(TextFormat("%i", GetFPS()), 10, 14, 20, Color{0, 0, 0, 100});
        DrawText(TextFormat("%i", GetFPS()), 10, 11, 20, Color{0, 150, 0, 255});
        DrawText(TextFormat("%i", GetFPS()), 10, 10, 20, Color{0, 255, 0, 255});

        EndDrawing();
    }

    CloseWindow();
    return 0;
}