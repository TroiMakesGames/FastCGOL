#include "raylib.h"         //raylib framework/library
#include <vector>           //includes type dynamic arrays called vectors in c++
#include <iostream>         //console logging
#include <cmath>            //math stuff like floor()
#include <random>           //random
#include <atomic>           //atomic bool flag array
#include <memory>               //same
#include <chrono>           //performance tracking

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

        std::vector<Vector2> activeCoords;
        std::unique_ptr<std::atomic<bool>[]> hasCoordBeenChecked;

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
            activeCoords.push_back(coord);
        }

        //set checked flag array values
        hasCoordBeenChecked = std::make_unique<std::atomic<bool>[]>(totalCells);
        for (int i = 0; i < totalCells; i++) 
        {hasCoordBeenChecked[i].store(false);}
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
        //create new array full of 0 integers, reset checked flags
        std::vector<int> newGrid = grid;
        std::vector<Vector2> newActiveCoords;

        for (int i = 0; i < worldWidth * worldHeight; i++)
        {hasCoordBeenChecked[i].store(false);}

        //check each cell
        for (int i = 0; i < activeCoords.size(); i++)
        {
            //get coord and indx from key
            int x = activeCoords[i].x;
            int y = activeCoords[i].y;

            Vector2 coord = Vector2(x, y);
            int indx = coordToInt(coord);

            //only compute if hasnt been checked yet
            if (hasCoordBeenChecked[indx].exchange(true)) 
            {continue;}

            //count live neighbors
            int liveCount = 0;
            for (int j = 0; j < 8; j++)
            {
                //get neighboring coord using neighbor offsets
                Vector2 copyCoord = Vector2(x, y);
                copyCoord.x += neighbors[j].x;
                copyCoord.y += neighbors[j].y;

                //clamp within world and loop over edges
                int cx = (int)copyCoord.x;
                int cy = (int)copyCoord.y;

                cx = (cx % worldWidth + worldWidth) % worldWidth;
                cy = (cy % worldHeight + worldHeight) % worldHeight;

                copyCoord.x = (float)cx;
                copyCoord.y = (float)cy;

                //get correctly clamped/looped index
                int neighboringIndex = coordToInt(copyCoord);

                //tally counter
                if (grid[neighboringIndex] == 1)
                {liveCount += 1;}
            }

            //check for rules
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
                //add current coord to nextActiveCoords
                newActiveCoords.push_back(coord);

                //also add all neighbors
                for (int j = 0; j < 8; j++)
                {
                    //get neighboring coord
                    Vector2 copyCoord = intToCoord(indx);
                    copyCoord.x += neighbors[j].x;
                    copyCoord.y += neighbors[j].y;

                    //clamp within world and loop over edges
                    int cx = (int)copyCoord.x;
                    int cy = (int)copyCoord.y;

                    cx = (cx % worldWidth + worldWidth) % worldWidth;
                    cy = (cy % worldHeight + worldHeight) % worldHeight;

                    copyCoord.x = (float)cx;
                    copyCoord.y = (float)cy;
                        
                    newActiveCoords.push_back(copyCoord);
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

    //track generation count to stop at a certain state
    int generationCount = 0;
    int maxGenerationCount = 10000;
    double times[10000];;  //store time required localy then save after the simulation finishes

    //while loop
    while (!WindowShouldClose() && generationCount < maxGenerationCount) {

        //start tracking how long it takes for the operations in between the chrono events to execute
        auto start = std::chrono::high_resolution_clock::now();
            
        grid.updateGrid();
        generationCount += 1;

        //... end tracking
        auto end = std::chrono::high_resolution_clock::now();

        //save the time required to procces
        double ms = std::chrono::duration<double, std::milli>(end - start).count();
        times[generationCount] = ms;

        // draw
        /*
        BeginDrawing();
        ClearBackground(Color{30, 30, 30, 255});

        grid.draw();

        DrawText(TextFormat("%i", GetFPS()), 10, 14, 20, Color{0, 0, 0, 100});
        DrawText(TextFormat("%i", GetFPS()), 10, 11, 20, Color{0, 150, 0, 255});
        DrawText(TextFormat("%i", GetFPS()), 10, 10, 20, Color{0, 255, 0, 255});

        EndDrawing();
        */
    }

    //save time data
    std::ofstream dataFile("data.txt");
    for (int i = 0; i < generationCount; i++)
    {dataFile << times[i] << "\n";}
    dataFile.close();

    CloseWindow();
    return 0;
}