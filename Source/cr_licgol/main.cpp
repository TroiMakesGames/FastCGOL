#include "raylib.h"         //raylib framework/library
#include <vector>           //includes type dynamic arrays called vectors in c++
#include <iostream>         //console logging
#include <cmath>            //math stuff like floor()
#include <random>           //random
#include <unordered_set>    //O(1) lookup time set

//set randomness stuff
std::random_device rd;
std::mt19937 gen(rd());

//load data from an existing pregenerated world data file
#include <fstream>
#include <string>
void LoadSeed(const std::string& filename, int* grid, int width, int height)
{
    std::ifstream file(filename);
    std::string line;

    if (std::getline(file, line))
    {
        int size = width * height;

        for (int i = 0; i < size && i < (int)line.size(); i++)
        {grid[i] = line[i] - '0';}
    }
}

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

        std::unordered_set<int> activeCoords;

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

        //set random values for start if the seed file exists
        std::string pathToPregeneratedWorld = "../seed.txt";
        if (std::ifstream().good())
        {LoadSeed(pathToPregeneratedWorld, grid.data(), worldWidth, worldHeight);}
        else
        {
            for (int i = 0; i < totalCells; i++)
            {grid[i] = std::uniform_int_distribution<int>(0, 1)(gen);}
        }

        //set initial active cells
        for (int i = 0; i < totalCells; i++)
        {
            Vector2 coord = intToCoord(i);
            int unorderedSet_key = coord.x + coord.y * worldWidth;
            //no check required as initial active cells are are cells
            //  if (activeCoords.find(key) == activeCoords.end())
            activeCoords.insert(unorderedSet_key);
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
        std::unordered_set<int> newActiveCoords;

        //check each cell
        for (int key : activeCoords)
        {
            int x = key % worldWidth;
            int y = key / worldWidth;

            int liveCount = 0;
            for (int j = 0; j < 8; j++)
            {
                //get neighboring coord
                Vector2 coord = Vector2(x, y);
                coord.x += neighbors[j].x;
                coord.y += neighbors[j].y;

                //clamp within world and loop over edges
                int cx = (int)coord.x;
                int cy = (int)coord.y;

                cx = (cx % worldWidth + worldWidth) % worldWidth;
                cy = (cy % worldHeight + worldHeight) % worldHeight;

                coord.x = (float)cx;
                coord.y = (float)cy;

                int neighboringIndex = coordToInt(coord);

                if (grid[neighboringIndex] == 1)
                {liveCount += 1;}
            }

            //check for rules
            int indx = coordToInt(Vector2(x, y));
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
                Vector2 coord = intToCoord(indx);
                int unorderedSet_key = coord.x + coord.y * worldWidth;
                if (newActiveCoords.find(unorderedSet_key) == newActiveCoords.end())
                {newActiveCoords.insert(unorderedSet_key);}

                //also add all neighbors
                for (int j = 0; j < 8; j++)
                {
                    //get neighboring coord
                    Vector2 ncoord = intToCoord(indx);
                    ncoord.x += neighbors[j].x;
                    ncoord.y += neighbors[j].y;

                    //clamp within world and loop over edges
                    int cx = (int)ncoord.x;
                    int cy = (int)ncoord.y;

                    cx = (cx % worldWidth + worldWidth) % worldWidth;
                    cy = (cy % worldHeight + worldHeight) % worldHeight;

                    ncoord.x = (float)cx;
                    ncoord.y = (float)cy;
                    
                    int unorderedSet_key = ncoord.x + ncoord.y * worldWidth;
                    if (newActiveCoords.find(unorderedSet_key) == newActiveCoords.end())
                    {newActiveCoords.insert(unorderedSet_key);}
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
    const int WIDTH = 750;
    const int HEIGHT = 450;
    InitWindow(WIDTH, HEIGHT, "Fast Conways Game of Life");
    SetTargetFPS(0);

    //variable initialisation

    int cellSize = 3;
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