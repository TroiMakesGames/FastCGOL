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

The collected data is in a format of time in milliseconds required to compute 1 iteration without rendering and without writing to a data file every iteration. (For example, 1 data point for Python Pygame would be 83.0233, for C# it would be 0.08364.) <br>

Instead of writing every iteration, the measured time was stored in a simple array each iteration, and after the simulation ended, the array was compiled into proper floats and written to a data.txt file of that specific implementation. <br>

Each implementation used pre-generated starting world seed data of 250 by 150 cell dimensions, which was initially generated using Python's seed, from which it was put into a seed.txt file and read by all other implementations. (Since the standard seed modules/libraries of all the languages/frameworks don't generate the same world for the same seed, I had to generate from one seed and load generated data from a specific save file.) <br>

The specific seed data used reaches just under 10k generations before it stops changing (only independent oscillators left), so I had each implementation run for 10k iterations. <br>

Each implementation was compiled into a Windows executable (if possible - not for JavaScript HTML Chrome) and also had its rendering logic removed to increase overall performance. <br>

## All implementations - cumulative time graph

This graph shows a cumulative graph of all 15 implementations. Each point represents the total required time to reach that specific iteration. (For example, unoptimised Python reached the 5000th iteration at around 457.2k milliseconds (around 7 minutes).) <br>

The graphing engine is made so that it always normalises to the worst-performing shown implementation. This is noticeable in future graphs. <br>

On the right of the graph, you can also see which implementation is shown and with what colour it is represented. <br>

<div align="center"><img src="Graph_PNGs/full.png" width="80%"></div>

## All implementations - cumulative time graph at 200 resolution average

The following graph is the same as the previous, but with one major difference: the points have been grouped and represented with a single point of their average, which results in a smoother overall graph. The graphing engine supports various group sizes, but the one I will be using in the graphs shown here will be at 1 data point per graph point (raw data - previous graph) or 200 data points per graph point. <br>

Note that this practice does reduce the actual accuracy of the graph for stable datasets, but since there are some very unstable graphs in the future, I implemented it to make it clearer ... the data loss will be acknowledged when it matters. <br>

<div align="center"><img src="Graph_PNGs/full_200.png" width="80%"></div>

## Python Pygame implementations

The first group I would like to showcase is the Python Pygame group of implementations. There are 3 total implementations. <br>

The green graph shows the naive, unoptimised implementation of computing every cell in the simulation world for every iteration ... it is used as a baseline for comparison with other implementations, since it's the worst-performing. <br>

The dark red and bright red are the 1st (ICGOL) and 2nd (LICGOL) layers of optimisation. The 2nd layer optimisation method is an upgrade of the 1st layer optimisation. Both methods are based around tracking relevant cells (cells that have a chance to change in the next generation) and only computing those, instead of every cell ... this removes most of the dead space, the computing of which is unnecessary. <br>

The main noticeable observation from this graph is how much better the optimised implementations perform... the 2nd layer is roughly 10 times faster than the baseline. In practice, this means that if it took 14 minutes to compute the baseline simulation, it would only take around 1.4 minutes to compute the simulation using an optimised method ... this is already a large improvement, but I was able to reach much better performance. <br>

<div align="center"><img src="Graph_PNGs/pp_200.png" width="80%"></div>

## First C++ Raylib implementation, compared to the best Python implementation

The next group of implementations I decided to create was the C++ Raylib implementations. <br>

This graph shows only the first naive, unoptimised C++ implementation, in comparison with the best Python implementation.

The immediate observation is that although the language might be a very important part of performance, a well-optimised system on a slow stack can perform as well as or even better than a badly optimised system on a faster stack. Therefore, the first C++ implementation reached around a 10x performance increase from the baseline. <br>

Another observation, which is noticeable in the previous graphs already, but is the clearest on this comparison, is the steepness-changing nature of the optimised method ... the start of the simulation has a slower performance than the end of the optimisation (this is shown by the steepness of the graph). This is explainable by the nature of the optimisation method, which performs better with less active cells ... and since the Conway's Game of Life simulation had a reduced number of relevant cells over time, the optimisation method was able to benefit more at the end.

<div align="center"><img src="Graph_PNGs/pp_best_vs_cr_worst_200.png" width="80%"></div>

## C++ compared to JavaScript

The next graph ... with possibly the most interesting or unexpected results ... is the comparison between the C++ and JavaScript implementation groups. <br>

Surprisingly enough, the unoptimised JavaScript implementation performed more than 2 times better than the unoptimised C++ implementation. When I saw these results, at first I thought that there must have been a mistake made somewhere, but after reading about JavaScript's performance with Chrome, I recognised the use of the JIT compiler (also used by C#, shown in the future graphs), which greatly improves the performance of small repeated tasks like large for loops or nested if statements. For the Conway's Game of Life, the improvements are especially noticeable, due to the simplistic nature of the simulation logic. <br>

The next observation is the difference in performance between the unoptimised and optimised implementations. Although JavaScript's default naive implementation is faster than C++, the optimised JavaScript implementations weren't able to benefit as much from the JIT compiler, meaning that they only improved the performance by around 40%, and C++ was able to overtake with its optimised implementations. <br>

There is an important note to take into consideration here ... when implementing the C++ LICGOL method (I implemented C++ before JavaScript), I used the unordered_set object type, which removes raw value copies from the set and with that enables the benefits of reduced lookup time of active cells and as a result allows for the actual reduction of computation steps compared to the 1st layer optimisation (which was only implemented for Python, as 2nd layer LICGOL simply performed better in all of the stacks). <br>

This object type and the operations it brings with it, although very intuitive and simple to implement, are relatively expensive when done at large scale. This is why I tried replacing the unordered_set with a 2D bool grid of flags, used to check whether a certain cell has already been processed this iteration. The use of this flag array instead of the set allowed for copies to exist within the array of relevant cells, since each cell can be processed once and then the copies get skipped. So now instead of removing copies from existence, the copies are just skipped. <br>

This simple replacement changed the operation cost by a large amount, and a great performance increase was reached ... therefore I decided to use the LICGOL flagged optimisation method in all future implementations, as they all had expensive object types in place of the unordered_set.

<div align="center"><img src="Graph_PNGs/cr_js_overlap_200.png" width="80%"></div>

## C++ CPU multithreading

The next graph also includes the 2 implementations connected to multithreading. The first of the 2, the atomic implementation, is a direct modification of the LICGOL flagged implementation, specifically made to support multithreading. Multithreading at 4 cores has the potential to improve the simulation performance by 4 times, but it's not that straightforward, because multithreading created some weird problems, specifically synchronisation issues. <br>

In order to support multithreading and fix up these read/write issues of async computing, atomic variables were put in place (that's what the atomic implementation is for). I'm not going to dive into what atomic vars are, but the general idea is that when an atomic bool is read, it is also immediately toggled, meaning that if 2 threads had a race condition at a certain bool and the first thread read the bool as true and wanted to toggle it as soon as possible (for example in the flag 2D array of the flagged optimisation method), the second thread won't read the same bool as true before the first could finish toggling to false... and a race condition error is avoided. Atomic bools do fix this issue, but since they are more complex object types, with more expensive operations, they also reduce the overall performance. So the atomic implementation was expected to perform slightly worse than the flagged, with the hopes that multithreading would bring a net positive performance increase. <br>

But unfortunately, the performance reduction of atomic vars was larger than the performance increase of multithreading, and the resulting performance of the multithreading implementation was overall worse than the simple flagged implementation.

<div align="center"><img src="Graph_PNGs/cr_multi_js_overlap_200.png" width="80%"></div>

## C# OpenTK + GPU Shader acceleration

The final cumulative graph includes the C# OpenTK implementations and the GPU accelerated shader implementation, alongside the best performing implementation by that point (C++ flagged). <br>

The surprising results show that C# is much faster than C++ at a simple task such as Conway's Game of Life simulation logic. C#'s naive default implementation performed around 30% better than the best C++ implementation. I imagine this is largely due to the performance improvements of the C# garbage collector, the more low-level nature of the primary C# object types like int and bool arrays, and the .NET 9 JIT compiler, that generates highly specialised machine code at runtime, when it has access to a much clearer display of what operations are being done and can optimise them more strictly, unlike C++, which has a single GCC compilation and no runtime optimisation. <br>

This observation doesn't directly mean that C# is just generally better than C++, it only shows the performance of a task such as Conway's Game of Life, at which I would actually say that C# has a clearer advantage, simply because of the simplicity of the operations, which makes the performance largely related to large-scale operations instead of low-scale high-complexity operations. <br>

The GPU shader implementation is by far the best-performing compared to all other implementations. It finished in around 1 second and ran 790 times faster than the baseline naive unoptimised Python Pygame implementation. To take this into perspective, if a single simulation took the baseline implementation 2 years to complete, it would take the GPU shader implementation less than a day to finish.

BUT there is a very big issue with the GPU shader implementation ... due to async computing issues previously mentioned in C++ CPU multithreading, the implementation uses the naive unoptimised C# implementation as a base ... which means that ALL irrelevant space is also computed ... so in a world of 10k by 10k cells, the GPU shader implementation would have to compute 100 million cells, no matter the active cell count, whereas an optimised base implementation, such as C# LICGOL flagged, could run an infinite world size as long as the relevant cell count is manageable. <br>

In practice, this means that the C# GPU shader accelerated optimisation isn't the only best implementation, and that the second-best C# LICGOL flagged is realistically very close. It all comes down to the context of the use case. In a tiny, limited world like the one used in the data collection (250x150), the GPU implementation performs 2 times better than the C# flagged implementation, but in the context of a larger, scarcely populated world of 10k by 10k cells, where only a couple thousand might be relevant, the C# flagged implementation would take over very quickly. <br>

So to conclude what language, framework, and optimisation method is best at running Conway's Game of Life - if the goal is to make an interactive world with no limits, where active cells are drawn by the user (so there isn't a huge amount of live cells), the C# flagged implementation is best, but if the goal is to run a tiny world where the relevant cell count is a large percentage of the world, the C# GPU shader accelerated implementation is by far the fastest. <br>

<div align="center"><img src="Graph_PNGs/c%23_own_league_200.png" width="80%"></div>

<!-- Per iteration graphs -->

## Time per iteration graphs

The second format of graphs I decided to analyse is a format of time required in milliseconds to compute only the n-th generation, instead of total time to reach that generation. <br>

This graph format specifically focuses on the stability of implementations, but since most of the implementations have a relatively wide range of time required, I also included data point grouping at 200 data points per graph point, so the general performance of different implementations is more clear (when we look at the performance of multiple different implementations, not their range of stability). <br>

The initial clear observation looking at all the graphs is that the ICGOL, LICGOL, LICGOL flagged, and LICGOL multithreaded all have an inconsistent time requirement per iteration. This is due to computing being dependent on the relevant cell count in these implementations, as was mentioned previously when comparing Python LICGOL and C++ unoptimised cumulative graphs. <br>

The next obvious observation is the stability of each graph, represented by the difference between the local minimum and maximum required times. The most varying performance is seen with the unoptimised Python implementation, which has a surprisingly large range of about -40% and +10% around the grouping average of 200 data points.

<div align="center"><img src="Graph_PNGs/periter_full.png" style="height:300px; object-fit:contain;"><img src="Graph_PNGs/periter_full_200.png" style="height:300px; object-fit:contain;"></div>

Taking a look at unoptimised C++ and JavaScript, specifically because of how interesting their compared results are so far, we can see that although JavaScript performs better, it is also much more unstable, with noticeable valleys but much higher peaks in the time requirements. This strange behaviour is explained by the extra tasks/requirements by the browser, specifically Chrome, like rendering the locally hosted website, checking for additional user inputs, and the simulation not having direct access to the CPU. Additionally, the JIT compiler runtime improvements cause extra disturbance, which is confirmed by the C# implementations also having similar behaviour of unnaturally high peaks (since both Chrome and .NET use the runtime JIT compiler).

<div align="center"><img src="Graph_PNGs/periter_cr_vs_js_stability.png" width="80%"></div>

## C# GPU shader implementations benchmark data collection grouping

It's important to note that even observing the simulation introduces new problems and inconsistencies in performance. Due to the nature of asynchronous computing, having to store the benchmark data while the simulation is running is especially challenging with GPU acceleration and multithreading. <br>

For the C# GPU shader implementation specifically, I had to separate the benchmarking/measuring from the actual computation that was being performed on the GPU, since checking the completion of one generation on the CPU was completely independent from the rest of the Conway's Game of Life logic computing. This means that if I were to store the required time per iteration for each iteration, I would have very unstable and inconsistent results. Therefore, to reduce the inconsistencies, I tracked the accumulated time of 100 generations, and stored the average after each 100 generations ... so it's similar to what the data point grouping within the graphing engine is doing to clear stability, but done for a different reason. <br>

Unfortunately, as mentioned during the introduction of the data point grouping of the graphing engine, this practice does lose detail, specifically the stability, but although it's improper to compare the stability of this implementation with any other implementation, this does improve the overall results of the data and somewhat fixes the async GPU runtime reading problems. <br>

Since the grouping is done at a resolution of 100 generations per read, the resulting graph has a very distinct shape of a column graph.

<div align="center"><img src="Graph_PNGs/periter_cs_shader_benchmark_grouping.png" width="80%"></div>

## C# flagged already overtakes the C# GPU shader implementation

As mentioned during the first efficiency comparisons of the C# GPU accelerated and C# flagged implementations, the flagged implementation has an advantage in a scarcely populated world. Understanding at which point the flagged implementation becomes more efficient is relatively hard from all previous graphs, but this comparison shows that, even at a tiny world scale of 250 by 150, in the final few iterations the GPU already performed worse. This means that all my previous mentions of 10k by 10k worlds was a largely overestimated guess ... the fine line is actually much closer to 250 by 150.

<div align="center"><img src="Graph_PNGs/periter_cs_flagged_vs_cs_shader_overtake_200.png" width="80%"></div>

## Possible error introduction

All of the data and observations must be taken with a grain of salt and it shouldn't be understood as the factual results, simply because there are so many variables that change the outcome of each implementation's efficiency, but it should serve as a baseline of understanding why a certain stack performs better or worse than a different stack. <br>

Some of the reasons why there could be errors are:

- **Inconsistent implementation standard**: The process of implementing all of the various stacks took multiple hours over the span of around 2-3 months, so my personal understanding and standard of how the Conway's Game of Life simulation works and how it's implemented changed drastically. This can also be seen by the fact that the Python stack doesn't include a flagged LICGOL implementation, and possibly why JavaScript might have an advantage over C++ as it was implemented last. To give an example of this error ... by the time I came to JavaScript, my standard of implementation already included the grid state variable as a 1-dimensional array of bools instead of a 2-dimensional array of 0 or 1 ints, which is generally a more expensive object type.
  
- **Inconsistent builds and interpreter environments**: Each implementation came with its own executable builds and compiling, which undeniably gives C++ and C# an unfair advantage over JavaScript and Python.
  
- **Data collection ran only once**: For each implementation I only performed one instance of data collection and got 1 dataset, instead of running multiple and finding the average or maybe just putting all of the datasets of one implementation on the graph ... (now that I think about it, this would have introduced another property to look at ... stability per instance of computing) ... the reason for that is mainly because when I started this project with only 3 Python implementations, I didn't expect to dive into 3 other stacks, so I used a simple .txt file instead of something like CSVs.

- **Hardware**: I ran all of the implementations on the same PC that has an Intel Core i7-6700 CPU and a 128MB Intel HD 350 Graphics card. Under this category, I'd also like to include the browser (Chrome) and the virtual environment for Python (VS Code IDE), which may or may not have affected the results.

- **External reading/writing**: I would specifically like to mention the use of reading from a .txt file to load the initial starting world data on all implementations except for Python's, which used its seed module to generate the file data in the first place, and the effects of collecting benchmark data, which caused additional disruption, as already mentioned during the showcase of C# GPU shader implementations non-accumulative graph (100 data point grouping already performed during data collection).

- **World simulation size**: All of the implementations ran on a 250 by 150 grid. To get more detailed results, I should have also included larger grids.
