#version 430 core

in vec2 texCoord;

out vec4 FragColor;

layout(std430, binding = 0) readonly buffer Grid
{
    uint grid[];
};

uniform int width;
uniform int height;

void main()
{
    int x = int(texCoord.x * float(width));
    int y = height - 1 - int(texCoord.y * float(height));

    int index = x + y * width;

    uint alive = grid[index];

    if (alive == 1)
    {
        FragColor = vec4(1.0, 1.0, 1.0, 1.0);
    }
    else
    {
        FragColor = vec4(0.1, 0.1, 0.1, 1.0);
    }
}