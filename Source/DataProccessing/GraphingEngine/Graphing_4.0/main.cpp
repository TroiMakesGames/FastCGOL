#include "raylib.h"
#include "raymath.h"

#include <vector>
#include <iostream>
#include <cmath>
#include <random>

//csv reading
#include <fstream>
#include <sstream>
#include <string>
#include <algorithm>

//include personal external tools
#include "DynamicCam.h"

std::string readCSV_line(std::string csvPath, int lineIndex)
{
    std::ifstream file(csvPath);
    if (!file.is_open()) {
        std::cerr << "Could not open file\n";
        return "None";
    }

    std::string line;
    for (int i = 0; i <= lineIndex; ++i)
    {std::getline(file, line);}
    
    std::replace(line.begin(), line.end(), ',', ' ');

    return line;
}

std::vector<float> stringToFloatVector(std::string str) {
    std::vector<float> numbers;

    str = str.substr(1, str.size() - 2); // remove [ ]

    std::stringstream ss(str);
    std::string value;

    while (std::getline(ss, value, ',')) {
        value.erase(0, value.find_first_not_of(" '"));
        value.erase(value.find_last_not_of(" '") + 1);

        numbers.push_back(std::stof(value));
    }

    return numbers;
}

class DataInstance
{
    public:
        std::string rawContent;
        std::string languageTag;
        std::string languageName;
        std::string logicTag;
        std::string attributeTag;
        std::string sizeTag;

        std::vector<float> timeData;

    public:
    DataInstance(std::string rawData) {
        rawContent = rawData;

        //parse raw data into tags
        std::stringstream ss(rawContent);
        std::string word;
        std::vector<std::string> parts;
        while (ss >> word) {
            parts.push_back(word);
        }

        //    "data" = parts[0];
        languageTag = parts[1];
        logicTag = parts[2];
        attributeTag = parts[3];
        sizeTag = parts[4];
        //    "simulation iteration" = parts[5]:
        timeData = stringToFloatVector(parts[6]);

        //get language name from tag
        if (languageTag == "pp")
        {languageName = "Python Pygame";}
        else if (languageTag == "js")
        {languageName = "JavaScript HTML";}
        else if (languageTag == "cr")
        {languageName = "C++ Raylib";}
        else if (languageTag == "cs")
        {languageName = "C# OpenTK";}
    }
};

int main() 
{
    //screen initialisation
    const int WIDTH = 1600;
    const int HEIGHT = 800;
    InitWindow(WIDTH, HEIGHT, "Fast Conways Game of Life - Graphs");

    int targetFps = 60;
    bool limitFps = true;
    SetTargetFPS(targetFps);

    //variable initialisation
    Viewport viewport = Viewport(Vector2(0, 0), 10, 0.05f, 0.05f, 5);

    DataInstance dta1 = DataInstance(readCSV_line("../../Data_V1.2/csv_periter.csv", 0));

    Vector2 objectPosition = Vector2(50, 50);
    Vector2 objectScreenPos = viewport.worldToScreenPos(objectPosition);
    Vector2 objectScale = Vector2(10, 20);
    Vector2 objectScreenScale = viewport.worldToScreenScale(objectScale);

    //adjust viewport zoom so that on start it doesnt draw cells too large
    viewport.zoom = 0.35f;

    //while loop
    while (!WindowShouldClose())
    {
        //update
        viewport.move(GetFrameTime());
        viewport.zoomCamera();

        objectScreenPos = viewport.worldToScreenPos(objectPosition);
        objectScreenScale = viewport.worldToScreenScale(objectScale);

        // draw
        BeginDrawing();
        ClearBackground(Color{30, 30, 30, 255});

        DrawRectangle(objectScreenPos.x - objectScreenScale.x/2, objectScreenPos.y - objectScreenScale.y/2, objectScreenScale.x, objectScreenScale.y, Color{255, 0, 0, 255});

        EndDrawing();
    }

    CloseWindow();
    return 0;
}