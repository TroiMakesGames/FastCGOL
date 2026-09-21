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

#include <cctype>

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

    return line;
}

std::vector<std::string> parseCSV_line(const std::string& line)
{
    std::vector<std::string> fields;
    std::string current;
    bool insideQuotes = false;

    for (char c : line)
    {
        if (c == '"')
        {
            insideQuotes = !insideQuotes;
        }
        else if (c == ',' && !insideQuotes)
        {
            fields.push_back(current);
            current.clear();
        }
        else
        {
            current += c;
        }
    }

    fields.push_back(current);

    return fields;
}

std::vector<float> stringToFloatVector(std::string str)
{
    std::vector<float> numbers;

    // Remove whitespace around the string
    str.erase(
        std::remove_if(str.begin(), str.end(), ::isspace),
        str.end()
    );

    // Remove [ ]
    if (!str.empty() && str.front() == '[')
        str.erase(str.begin());

    if (!str.empty() && str.back() == ']')
        str.pop_back();

    std::stringstream ss(str);
    std::string value;

    while (std::getline(ss, value, ','))
    {
        if (!value.empty())
        {
            numbers.push_back(std::stof(value));
        }
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
        std::vector<Vector2> points;

    public:
    DataInstance(std::string rawData) {
        rawContent = rawData;

        //resize points to proper size
        points.resize(10000);

        //parse raw content
        std::vector<std::string> parsedCSV = parseCSV_line(rawContent);

        //    "data" = parts[0];
        languageTag = parsedCSV[0];
        logicTag = parsedCSV[1];
        attributeTag = parsedCSV[2];
        sizeTag = parsedCSV[3];
        //    "simulation iteration" = parts[4]:

        timeData = stringToFloatVector(parsedCSV[5]);

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
        float widthPerIndex = graphWidth / 10000.0f;
        float yPerTimeUnit = graphHeight / maxTimeData * -1;

        for (int i = 0; i < timeData.size() - 1; i++)
        {points[i] = {widthPerIndex * i, yPerTimeUnit * timeData[i]};}
    }

    void draw(Viewport viewport, Color lineColor)
    {
        for (int i = 0; i < points.size() - 2; i++)
        {
            //get curr and next point
            Vector2 p1 = points[i];
            Vector2 p2 = points[i + 1];

            //get screen pos
            p1 = viewport.worldToScreenPos(p1);
            p2 = viewport.worldToScreenPos(p2);

            DrawLine(p1.x, p1.y, p2.x, p2.y, lineColor);
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
    Viewport viewport = Viewport(Vector2(800, -400), 10, 0.05f, 0.05f, 5);

    int numOfInstances = 48;
    std::string pathToCSV = "../../Data_V1.2/csv_accumulated.csv";

    std::vector<DataInstance> dataInstances;
    dataInstances.reserve(numOfInstances);

    for (int i = 0; i < numOfInstances; i++)
    {
        DataInstance dta = DataInstance(readCSV_line(pathToCSV, i));
        //add to the array
        dataInstances.emplace_back(std::move(dta));
    }

    //calculate points with global maximum
    int globalMax = 0;
    for (int i = 0; i < numOfInstances; i++)
    {
        int currMax = *std::max_element(dataInstances[i].timeData.begin(), dataInstances[i].timeData.end());
        if (currMax > globalMax) {globalMax = currMax;}
    }
    for (int i = 0; i < numOfInstances; i++)
    {dataInstances[i].recalculatePoints(1600, 800, globalMax);}

    //adjust viewport zoom so that on start it doesnt draw cells too large
    viewport.zoom = 0.9f;

    //while loop
    while (!WindowShouldClose())
    {
        //update
        viewport.move(GetFrameTime());
        viewport.zoomCamera();

        // draw
        BeginDrawing();
        ClearBackground(Color{30, 30, 30, 255});

        for (int i = 0; i < numOfInstances; i++)
        {
            dataInstances[i].draw(viewport,  {255, 0, 0, 255});
        }

        EndDrawing();
    }

    CloseWindow();
    return 0;
}