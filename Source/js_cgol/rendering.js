const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

/* class def */
class Grid_rendering 
{
    constructor(worldWidth, worldHeight, cellSize) 
    {
        this.worldWidth = worldWidth;
        this.worldHeight = worldHeight;

        this.cellSize = cellSize;

        this.grid = Array.from({ length: worldWidth }, () =>
            Array(worldHeight).fill(false)
        );
    }

    Draw() 
    {
        ctx.fillStyle = "white";

        for (let i = 0; i < this.grid.length; i++) 
        {
            for (let j = 0; j < this.grid[i].length; j++) 
            {
                if (this.grid[i][j] == true) 
                {ctx.fillRect(i * this.cellSize, j * this.cellSize, this.cellSize, this.cellSize);}
            }
        }
    }
}

/* obj instantiation */
const grid = new Grid_rendering(250, 150, 3);

let renderFrames = 0;
let renderLastTime = performance.now();

/* simulation worker - get independant simulation state from main.js */
const worker = new Worker("main.js");
worker.onmessage = function(event) 
{grid.grid = event.data;};

/* rendering loop */
function gameLoop() 
{
    /* rendering removed from data collection
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    grid.Draw();

    //rendering performance
    renderFrames++;
    let now = performance.now();
    if (now - renderLastTime >= 1000) {
        console.log("Render FPS:", renderFrames);
        renderFrames = 0;
        renderLastTime = now;
    }

    requestAnimationFrame(gameLoop);
    */
}

gameLoop();