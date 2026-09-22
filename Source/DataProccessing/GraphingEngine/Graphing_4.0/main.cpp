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
        Color color;
        std::string rawContent;
        std::string languageTag;
        std::string languageName;
        std::string logicTag;
        std::string attributeTag;
        std::string sizeTag;

        std::vector<float> timeData;
        std::vector<Vector2> points;

    public:
    DataInstance(std::string rawData, Color color) {
        rawContent = rawData;
        
        this->color = color;

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

    void recalculatePoints(int graphWidth, int graphHeight, float maxTimeData, float groupingResolution)
    {
        points.resize(10000 / static_cast<int>(groupingResolution));

        float widthPerIndex = graphWidth / 10000.0f;
        float yPerTimeUnit = graphHeight / maxTimeData * -1;

        float currAcc = 0;
        for (int i = 0; i < timeData.size() - 1; i++)
        {
            currAcc += timeData[i];

            if (i % static_cast<int>(groupingResolution) == 0)
            {
                points[i / static_cast<int>(groupingResolution)] = {widthPerIndex * i, yPerTimeUnit * (currAcc / static_cast<int>(groupingResolution))};
                currAcc = 0;
            }
        }
    }

    void draw(Viewport viewport)
    {
        for (int i = 0; i < points.size() - 2; i++)
        {
            //get curr and next point
            Vector2 p1 = points[i];
            Vector2 p2 = points[i + 1];

            //get screen pos
            p1 = viewport.worldToScreenPos(p1);
            p2 = viewport.worldToScreenPos(p2);

            DrawLine(p1.x, p1.y, p2.x, p2.y, color);
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
    float groupingResolution = 20.0f;
    std::string pathToCSV = "../../Data_V1.2/csv_accumulated.csv";

    std::vector<DataInstance> dataInstances;
    dataInstances.reserve(numOfInstances);

    Color colors[] = {
        //pp
        {100, 100, 0, 255},
        {150, 150, 0, 255},
        {200, 200, 0, 255},
        {255, 255, 0, 255},

        //js
        {150, 75, 0, 255},
        {200, 100, 0, 255},
        {255, 125, 0, 255},

        //cr
        {0, 0, 150, 255},
        {0, 0, 200, 255},
        {0, 0, 255, 255},

        {0, 200, 200, 255},
        {0, 255, 255, 255},

        //cs
        {150, 0, 150, 255},
        {200, 0, 200, 255},
        {255, 0, 255, 255},
        {255, 0, 0, 255}
    };

    std::vector<int> colorIndecies = {
        7, 7, 7,
        10, 10, 10,
        9, 9, 9,
        11, 11, 11,
        8, 8, 8,

        15, 15, 15,
        12, 12, 12,
        14, 14, 14,
        13, 13, 13,

        4, 4, 4,
        6, 6, 6,
        5, 5, 5,

        0, 0, 0,
        1, 1, 1,
        3, 3, 3,
        2, 2, 2
    };

    for (int i = 0; i < numOfInstances; i++)
    {
        DataInstance dta = DataInstance(readCSV_line(pathToCSV, i), colors[colorIndecies[i]]);

        //add to the array
        dataInstances.emplace_back(std::move(dta));
    }

    //calculate points with global maximum
    float globalMaxAverage = 0.0f;
    for (int i = 0; i < numOfInstances; i++)
    {
        //get time data
        auto& data = dataInstances[i].timeData; //auto - unassigned type (gets assigned along the way)

        //go through the instances data and get avarage of group of 200
        for (size_t start = 0; start + static_cast<int>(groupingResolution) <= data.size(); start += static_cast<int>(groupingResolution))
        {
            float sum = 0.0f;
            for (size_t j = start; j < start + static_cast<int>(groupingResolution); j++)
            {sum += data[j];}

            float average = sum / groupingResolution;
            
            //check if largest
            if (average > globalMaxAverage)
            {globalMaxAverage = average;}
        }
    }

    for (int i = 0; i < numOfInstances; i++)
    {dataInstances[i].recalculatePoints(1600, 800, globalMaxAverage, groupingResolution);}

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
            dataInstances[i].draw(viewport);
        }

        EndDrawing();
    }

    CloseWindow();
    return 0;
}