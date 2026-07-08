#include "raylib.h"     //raylib framework/library
#include <vector>       //includes type dynamic arrays called vectors in c++
#include <iostream>     //console logging
#include <cmath>        //math stuff like floor()
#include <random>

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
    }

    // general functions
    void updateGrid() {
        //create a new empty grid
        std::vector<int> newGrid;
        newGrid.resize(worldWidth * worldHeight);

        //loop through cells
        for (int i = 0; i < grid.size(); i++)
        {   
            // SAND --------------------------------------------------------------------
            if (grid[i] == 1)
            {
                //default to keeping the sand in the same position if its not moved in the future
                newGrid[i] = 1;

                int x = i % worldWidth;
                int y = i / worldWidth;
                
                //check if on the last row
                if (y < worldHeight - 1)
                {
                    //down
                    if (grid[i + worldWidth] == 0)
                    {
                        newGrid[i] = 0;
                        newGrid[i + worldWidth] = 1;
                    }
                    //down left
                    else if (x > 0 && grid[i + worldWidth - 1] == 0 && grid[i + worldWidth + 1] == 1)
                    {
                        newGrid[i] = 0;
                        newGrid[i + worldWidth - 1] = 1;
                    }
                    //down right
                    else if (x < worldWidth - 1 && grid[i + worldWidth + 1] == 0 && grid[i + worldWidth - 1] == 1)
                    {
                        newGrid[i] = 0;
                        newGrid[i + worldWidth + 1] = 1;
                    }
                    //both open
                    else if (x > 0 && x < worldWidth - 1 && grid[i + worldWidth - 1] == 0 && grid[i + worldWidth + 1] == 0)
                    {
                        //choose a random side
                        int choice = std::uniform_int_distribution<int>(0, 1)(gen);

                        newGrid[i] = 0;

                        if (choice == 1)
                        {newGrid[i + worldWidth + 1] = 1;}
                        else
                        {newGrid[i + worldWidth - 1] = 1;}
                    }
                }
            }
        }

        //override old grid with new
        grid = newGrid;
    }

    void draw() {
        //1D grid array
        for (int i = 0; i < worldWidth * worldHeight; i++)
        {
            int y = i / worldWidth;
            int x = i % worldWidth;

            if (grid[worldWidth * y + x] == 1)
            {DrawRectangle(cellSize * x, cellSize * y, cellSize, cellSize, Color{255, 255, 0, 255});}
        }
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
    //grid.grid[grid.worldWidth * 5 + 10] = 1;

    //while loop
    while (!WindowShouldClose()) {

        // update
        grid.updateGrid();

        //debug num of sand particles
        int count = 0;
        for (int i = 0; i < grid.grid.size(); i++)
        {if (grid.grid[i] == 1){count++;}}
        std::cout << count << std::endl;

        // draw
        BeginDrawing();
        ClearBackground(Color{30, 30, 30, 255});

        grid.draw();

        DrawText(TextFormat("%i", GetFPS()), 10, 10, 20, BLACK);

        EndDrawing();
    }

    CloseWindow();
    return 0;
}