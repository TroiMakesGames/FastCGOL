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
        std::vector<Vector2> points[10000];

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

    void recalculatePoints(int graphWidth, int graphHeight, float maxTimeData)
    {
        float widthPerIndex = graphWidth / 10000;
        float yPerTimeUnit = graphHeight / maxTimeData;

        for (int i = 0; i < timeData.size() - 1; i++)
        {points[i] = {widthPerIndex * i, yPerTimeUnit * timeData[i]};}
    }

    void draw()
    {
        for (int i = 0; i < points.size() - 1; i++)
        {
            //get curr and next point
            Vector2 p1 = points[i];
            Vector2 p2 = points[i + 1];

            //get screen pos
            p1 = viewport.worldToScreenPos(p1);
            p2 = viewport.worldToScreenPos(p2);

            DrawLine(p1.x, p1.y, p.x, p2.y, RED);
        }
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
    dta1.recalculatePoints(800, 400, *std::max_element(dta1.timeData.begin(), dta1.timeData.end()));

    //adjust viewport zoom so that on start it doesnt draw cells too large
    viewport.zoom = 0.35f;

    //while loop
    while (!WindowShouldClose())
    {
        //update
        viewport.move(GetFrameTime());
        viewport.zoomCamera();

        // draw
        BeginDrawing();
        ClearBackground(Color{30, 30, 30, 255});

        dta1.draw();

        EndDrawing();
    }

    CloseWindow();
    return 0;
}