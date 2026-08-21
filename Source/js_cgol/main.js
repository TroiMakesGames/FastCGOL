class Grid_simulation 
{
    constructor(worldWidth, worldHeight) 
    {
        this.worldWidth = worldWidth;
        this.worldHeight = worldHeight;

        this.grid = Array.from({ length: worldWidth }, () =>
            Array(worldHeight).fill(false)
        );

        this.neighbours = [[-1, -1],[0, -1],[1, -1],[1, 0],[1, 1],[0, 1],[-1, 1],[-1, 0]];
    }

    Update() 
    {
        let newGrid = Array.from(
            { length: this.worldWidth },
            () => Array(this.worldHeight).fill(false)
        );

        for (let i = 0; i < newGrid.length; i++) 
        {
            for (let j = 0; j < newGrid[i].length; j++) 
            {

                let nCount = 0;

                for (let n = 0; n < this.neighbours.length; n++) 
                {

                    let nX = (i + this.neighbours[n][0] + this.worldWidth) % this.worldWidth;
                    let nY = (j + this.neighbours[n][1] + this.worldHeight) % this.worldHeight;

                    if (this.grid[nX][nY] == true) 
                    {nCount++;}
                }

                if (this.grid[i][j] == true) 
                {
                    if (nCount >= 2 && nCount <= 3) 
                    {newGrid[i][j] = true;}
                }
                else 
                {
                    if (nCount == 3) 
                    {newGrid[i][j] = true;}
                }
            }
        }

        this.grid = newGrid;
    }
}

/* obj instantiation */
const grid = new Grid_simulation(250, 150);
let genCount = 0;
let maxGenCount = 10000;

let simulationUpdates = 0;
let simulationLastTime = performance.now();

/* random seed 
for (let i = 0; i < grid.grid.length; i++) {
    for (let j = 0; j < grid.grid[i].length; j++) 
    {grid.grid[i][j] = Math.random() < 0.5;}
}
*/

/* load seed data */ // the start of the main loop is dependant on the seed data loading so its contained within the whole fetch function
fetch("seed.txt").then(response => response.text()).then(data => {
    data = data.trim();

    for (let i = 0; i < grid.grid.length; i++) {
        for (let j = 0; j < grid.grid[i].length; j++) {
            let index = i + j * grid.worldWidth;
            grid.grid[i][j] = data[index] === "1";
        }
    }

    /* simulation loop */
    while (genCount <= maxGenCount) 
    {
        grid.Update();
        genCount += 1;

        //simulation performance
        simulationUpdates++;
        let now = performance.now();
        if (now - simulationLastTime >= 1000) {
            console.log("Simulation FPS:", simulationUpdates);
            simulationUpdates = 0;
            simulationLastTime = now;
        }

        postMessage(grid.grid);
    }
});