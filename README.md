# FastCGOL
... work in progress ...

( this is an extension of my initial cellular automaton project found here https://github.com/TroiMakesGames/ConwaysGOL )

Exploring different methods of optimisation for grid based cellular automaton systems with 8 neighbors (using the rules of Conway's Game of Life), specificaly logic/CPU/GPU/shader optimisations using the following languages and frameworks:
- Python Pygame
- JavaScript HTML Canvas (ran on Chrome)
- C++ Raylib (+ multithreading on 4 cores)
- C# OpenTK (.NET OpenGL wrapper for C#) (+ GPU/shader accelaration)

If youd like to read more about the 1st and 2nd layer of optimisation methods (Irelevance check / Live irelevance check) you can find a detailed descirption (honestly more of a yapp) on my initial Conways Game of Life project repo https://github.com/TroiMakesGames/ConwaysGOL ... and an extension of it, which inlcudes some other variable types, multithreading and fixes, in PerformanceBoostConcepts.txt. <br>

# Graphs and observations (Work in progress)

## Data format
The collected data is in a format of time in miliseconds required to compute 1 iteration without rendering and without writting to a data file every iteration. (for example 1 data point for Python Pygame would be 83.0233, for C# it would be 0.08364) <br>

Instead of writting every iteration, the measured time was stored in a simple array each iteration and after the simulation ended the array was compiled into proper floats and written to a data.txt file of that specific implementation. <br>

Each implementation used pre-generated starting world seed data which was initialy generated using Pythons seed, from which it was put into a seed.txt file and read by all other implementations. (since the standard seed modules/libraries of all the languages/frameworks doesnt generate the same world for the same seed i had to generate from one seed and load generated data from a specific save file) <br>

The specific seed data used reaches just under 10k generations before it stops changing (only independant oscilators left), so i had each implementation run for 10k iterations. <br>

Each implementation was compiled into a windows executable (if possible - not for JavaScript HTML Chrome) and also had its rendering logic removed to increase overall performance. <br>

## All implementations - cumulative time graph
This graph shows a cumulative graph of all 15 implementations. Each point represents the total required time to reach that specific iteration. (for example unoptimised python reached the 5000th iteration at around 457.2k miliseconds (around 7 minutes)) <br>

The graphing engine is made so that it always normalizes to the worst performing shown implementation. This is noticable in future graphs. <br>

On the right of the graph you can also see which implementation is shown and with what color it is represented. <br>

<div align="center"><img src="Graph_PNGs/full.png" width="80%"></div>

## All implementations - cumulative time graph at 200 resolution avarage
The following graph is the same as the previous, but with one major difference, the points have been grouped and represented with a single point of their avarage, which results in a smoother overal graph. The graphing engine supports various group sizes but the one i will be using in the graphs shown here will be at 1 data point per graph point (raw data - previous graph) or 200 data points per graph point. <br>

Note that this practice does reduce the acctual accuracy of the graph for stable datasets but since there are some very unstable graphs in the future i implemented it to make it clearer ... the data loss will be acknowladged in the when it matters
<div align="center"><img src="Graph_PNGs/full_200.png" width="80%"></div>

## Python Pygame implementations
The first group i would like to showcase is the Python Pygame group of implementations. There are 3 total implementations. <br>

The green graph shows the naive unoptimised implementation of computing every cell in the simulation world for every iteration ... it is used as a baseline for comparison with other implementations, since its the worst performing. <br>

The dark red and bright red are the 1st (ICGOL) and 2nd (LICGOL) layers of optimisation. The 2nd layer optimisation method is an upgrade of the 1st layer opsitmisation. Both methods are based around tracking relevant cells (cells that have a chance to change in the next generation) and only computing those, instead of every cell ... this removes most of the dead space, the computing of which is unneccesary. <br>

The main noticable observation from this graph is how much better the omptimised implementations perform... the 2nd layer is roughly 10 times faster than the baseline. In practice this means that if it took 14 minutes to compute the baseline simulation, it would only take around 1.4 minutes to compute the simulation using an optimised method ... this is already a large improvement, but i was able to reach much better performance. <br>
<div align="center"><img src="Graph_PNGs/pp_200.png" width="80%"></div>

## First C++ Raylib implementation, compared to the best Python implementation
The next group of implementations i decided to create was the C++ Raylib implementations. <br>

This graph shows only the first naive unoptimised C++ implementation, in comparison with the best Python implementation.

The immediate observation is that although the language might be a very important part of performance, a well optimised system on a slow stack can perform as well as or even better than a badly optimised system on a faster stack. Therefore, the first C++ implementation reached around 10x performance increase from the baseline. <br>

Another observation, which is noticable in the previous graphs already, but is the clearest on this comparison, is the steepnes changing nature of the optimised method ... the start of the simulation has a slower performance than the end of the optimisation (this is shwon by the steepnes of the graph). This is explainable by the nature of the optimisation method, which performs better with less active cells ... and since the conways game of life simulation had a reduced number of relevant cells over time, the optimisation method was able to benefit more at the end.
<div align="center"><img src="Graph_PNGs/pp_best_vs_cr_worst_200.png" width="80%"></div>

## C++ compared to JavaScript
The next graph ... with possibly the most interesting or unexpected results ... is the comparison between the C++ and Javascript implementation groups. <br>

Surprisingly enough, the unotpimised JavaScript implementation performed more than 2 times better than the unoptimised C++ implementation. When i saw theese results, at first i though that there must have been a mistake made somewhere, but after reading about JavaScripts performance with Chrome i recognised the use of the JIT-compiler (Also used by C#, shown in the future graphs), which greatly improves the performance of small repeated tasks like large for loops or nested if statements. For the conways game of life, the improvements are especialy noticable, due to the simplistic nature of the simulation logic. <br>

The next observation is the difference in performance between the unoptimised and optimised implementaitons. Although JavaScripts default naive implementation is faster than C++, the optimised JavaScript implementations werent able to benefit as much from the JIT-compiler, meaning that they only imrpoved the performance by aroun 40%, and C++ was able to overtake with its optimised implementations. <br>

There is an important note to take into consideration here ... when implementing the C++ LICGOL method (i implemented C++ before JavaScript) i used the unordered_set object type, which removes raw value copies from the set and with that enables the benefits of reduced lookup time of active cells and as a result allows for the acctual reduction of computation steps compared to the 1st layer optimisation (which was only implemented for Python, as 2nd layer LICGOl simply performed better in all of the stacks). <br>

This object type and the operations it brings with it, although very intuitive and simple to implement, are relatively expensive when done at large scale. This is why i tried replacing the unordered_set with a 2D bool grid of flags, used to check whether a certain cell has already been proccesed this iteration. The use of this flag array instead of the set allowed for copies to exist within the aray of relevant cells, since each cell can be proccessed once and then the copies get skipped. So now instead of removing copies from existance, the copies are just skipped. <br>

This simple replacement changed the operation cost by a large amount, and a great performance increase was reached ... therefore i decided to use the LICGOL flagged optimisation method in all future implementations, as they all had expensive object types in place of the unordered_set.
<div align="center"><img src="Graph_PNGs/cr_js_overlap_200.png" width="80%"></div>

## C++ multithreading
<div align="center"><img src="Graph_PNGs/cr_multi_js_overlap_200.png" width="80%"></div>

## cr flagged + c# all res 200
<div align="center"><img src="Graph_PNGs/c%23_own_league_200.png" width="80%"></div>

<!-- Per iteration graphs -->

## periter full
<div align="center"><img src="Graph_PNGs/periter_full.png" width="80%"></div>

## periter full res 200
<div align="center"><img src="Graph_PNGs/periter_full_200.png" width="80%"></div>

## periter pp all res 200
<div align="center"><img src="Graph_PNGs/periter_pp_200.png" width="80%"></div>

## cr vs pp stability
<div align="center"><img src="Graph_PNGs/periter_cr_vs_pp_stability.png" width="80%"></div>

## cr vs js stability
<div align="center"><img src="Graph_PNGs/periter_cr_vs_js_stability.png" width="80%"></div>

## cs shader benchmark groupin
<div align="center"><img src="Graph_PNGs/periter_cs_shader_benchmark_grouping.png" width="80%"></div>

## cs shader vs cs flagged overtake
<div align="center"><img src="Graph_PNGs/periter_cs_flagged_vs_cs_shader_overtake_200.png" width="80%"></div>
