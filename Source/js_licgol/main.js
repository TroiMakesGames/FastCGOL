class Grid_simulation 
{
    constructor(worldWidth, worldHeight) 
    {
        this.worldWidth = worldWidth;
        this.worldHeight = worldHeight;

        this.grid = Array.from({ length: worldWidth }, () =>
            Array(worldHeight).fill(false)
        );

        //get active coords set and add initial active cells
        this.activeCoords = new Set();
        for (let i = 0; i < this.grid.length; i++) 
        {
            for (let j = 0; j < this.grid[i].length; j++) 
            {this.activeCoords.add(i * this.worldHeight + j);}
        }

        this.neighbours = [[-1, -1],[0, -1],[1, -1],[1, 0],[1, 1],[0, 1],[-1, 1],[-1, 0]];
    }

    Update() 
    {
        let newGrid = this.grid.map(row => [...row]);

        let newActiveCoords = new Set();

        for (const key of this.activeCoords) 
        {
            let nCount = 0;
            const i = Math.floor(key / this.worldHeight);
            const j = key % this.worldHeight;

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
                if (nCount < 2 || nCount > 3)
                {newGrid[i][j] = false;}
            }
            else 
            {
                if (nCount == 3) 
                {newGrid[i][j] = true;}
            }

            //live irrelevance check
            if (newGrid[i][j] != this.grid[i][j])
            {
                //add self
                newActiveCoords.add(i * this.worldHeight + j);

                //add neighbors
                for (let n = 0; n < this.neighbours.length; n++) 
                {
                    let nX = (i + this.neighbours[n][0] + this.worldWidth) % this.worldWidth;
                    let nY = (j + this.neighbours[n][1] + this.worldHeight) % this.worldHeight;

                    newActiveCoords.add(nX * this.worldHeight + nY);
                }
            }
        }

        this.grid = newGrid;
        this.activeCoords = newActiveCoords;
    }
}

/* obj instantiation */
const grid = new Grid_simulation(250, 150);
let genCount = 0;
let maxGenCount = 10000;

let simulationUpdates = 0;
let simulationLastTime = performance.now();

let times = [];
let simProperLastTime= performance.now();

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

        let timeDiff = now - simProperLastTime;
        simProperLastTime = now;
        times.push(timeDiff);

        postMessage({type: "grid", dta: grid.grid});
    }

    //download data
    const datta = times.join("\n");
    postMessage({type: "data", dta: datta});
});