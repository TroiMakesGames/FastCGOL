"""
THIS GRAPHING SCRIPT IS ALMOST ENTIERLY AI GENERATED ...
ill get to making my own version at some point but for now i dont really care about this lol ... i just want nice graphs
"""

import pygame
from itertools import accumulate
from pathlib import Path
import os


# =============================================================================
# CONFIGURATION
# =============================================================================

WIDTH = 1400
HEIGHT = 850
FPS = 60

BACKGROUND = (15, 15, 18)
GRID_COLOR = (42, 42, 48)
AXIS_COLOR = (150, 150, 155)
TEXT_COLOR = (235, 235, 240)
MUTED_TEXT = (110, 110, 115)
PANEL_COLOR = (22, 22, 27)
HOVER_COLOR = (35, 35, 42)

GRAPH_RECT = pygame.Rect(
    80,
    55,
    1000,
    700,
)

LEGEND_X = 1110
LEGEND_Y = 60

DATA_DIR = Path(
    "Source/DataProccessing/Data"
)


# =============================================================================
# GRAPH RESOLUTION OPTIONS
# =============================================================================
#
# Resolution determines how many raw data points are averaged together
# to create one displayed point.
#
# 1  = every data point
# 5  = average every 5 points
# 10 = average every 10 points
# etc.
#
# [ decreases resolution
# ] increases resolution
# 0 resets to resolution 1
#
# =============================================================================

RESOLUTION_OPTIONS = [
    1,
    2,
    5,
    10,
    20,
    50,
    100,
    200,
    500,
    1000,
]


# =============================================================================
# DATASET CONFIGURATION
# =============================================================================

DATASETS = [

    {
        "name": "Python CGOL",
        "file": "data_pp_cgol.txt",
        "color": (0, 255, 0),
        "group": "Python",
        "enabled": True,
    },

    {
        "name": "Python ICGOL",
        "file": "data_pp_icgol.txt",
        "color": (200, 0, 0),
        "group": "Python",
        "enabled": True,
    },

    {
        "name": "Python LICGOL",
        "file": "data_pp_licgol.txt",
        "color": (255, 0, 0),
        "group": "Python",
        "enabled": True,
    },

    {
        "name": "JS CGOL",
        "file": "data_js_cgol.txt",
        "color": (150, 75, 0),
        "group": "JavaScript",
        "enabled": True,
    },

    {
        "name": "JS LICGOL",
        "file": "data_js_licgol.txt",
        "color": (200, 100, 0),
        "group": "JavaScript",
        "enabled": True,
    },

    {
        "name": "JS LICGOL flagged",
        "file": "data_js_licgol_flagged.txt",
        "color": (255, 125, 0),
        "group": "JavaScript",
        "enabled": True,
    },

    {
        "name": "C++ CGOL",
        "file": "data_cr_cgol.txt",
        "color": (0, 0, 150),
        "group": "C++",
        "enabled": True,
    },

    {
        "name": "C++ LICGOL",
        "file": "data_cr_licgol.txt",
        "color": (0, 0, 200),
        "group": "C++",
        "enabled": True,
    },

    {
        "name": "C++ LICGOL flagged",
        "file": "data_cr_licgol_flagged.txt",
        "color": (0, 0, 255),
        "group": "C++",
        "enabled": True,
    },

    {
        "name": "C++ LICGOL atomic",
        "file": "data_cr_licgol_atomic.txt",
        "color": (200, 200, 0),
        "group": "C++",
        "enabled": True,
    },

    {
        "name": "C++ LICGOL multithreaded",
        "file": "data_cr_licgol_multithreaded.txt",
        "color": (255, 255, 0),
        "group": "C++",
        "enabled": True,
    },

    {
        "name": "C# CGOL",
        "file": "data_cs_cgol.txt",
        "color": (150, 0, 150),
        "group": "C#",
        "enabled": True,
    },

    {
        "name": "C# LICGOL",
        "file": "data_cs_licgol.txt",
        "color": (200, 0, 200),
        "group": "C#",
        "enabled": True,
    },

    {
        "name": "C# LICGOL flagged",
        "file": "data_cs_licgol_flagged.txt",
        "color": (255, 0, 255),
        "group": "C#",
        "enabled": True,
    },

    {
        "name": "C# CGOL shader",
        "file": "data_cs_cgol_shader.txt",
        "color": (0, 255, 255),
        "group": "C#",
        "enabled": True,
    },
]


# =============================================================================
# DATA LOADING
# =============================================================================

def load_times(path):
    """
    Load one timing measurement per line.
    """

    with open(path, "r") as file:

        return [
            float(line.strip())
            for line in file
            if line.strip()
        ]


def accumulate_times(values):
    """
    Convert per-iteration timings into cumulative timings.

    Example:

        [2, 3, 4]

    becomes:

        [2, 5, 9]
    """

    return list(
        accumulate(values)
    )


def load_datasets():
    """
    Load all datasets.

    Both the original per-iteration values and the
    accumulated values are stored.
    """

    datasets = []

    for config in DATASETS:

        path = DATA_DIR / config["file"]

        values = load_times(path)

        dataset = config.copy()

        # Original measurements.
        dataset["raw_values"] = values

        # Cumulative measurements.
        dataset["values"] = accumulate_times(values)

        datasets.append(dataset)

    return datasets


# =============================================================================
# GRAPH
# =============================================================================

class Graph:

    def __init__(self, rect):

        self.rect = rect

        self.font = pygame.font.SysFont("verdana", 22)
        self.small_font = pygame.font.SysFont("verdana", 18)

        self.datasets = []

        self.max_x = 1
        self.max_y = 1

        # ---------------------------------------------------------------------
        # Graph mode
        #
        # "cumulative"    -> total elapsed time
        # "per_iteration" -> time required by each individual iteration
        # ---------------------------------------------------------------------

        self.graph_mode = "cumulative"

        # ---------------------------------------------------------------------
        # Point resolution
        #
        # 1 = use every point
        # 5 = average every 5 points
        # etc.
        # ---------------------------------------------------------------------

        self.resolution = 1

        self.surface = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        self.dirty = True


    # =========================================================================
    # DATA
    # =========================================================================

    def set_data(self, datasets):

        self.datasets = datasets

        self.recalculate_scale()

        self.dirty = True


    def get_enabled_datasets(self):

        return [
            dataset
            for dataset in self.datasets
            if dataset["enabled"]
        ]


    def get_dataset_values(self, dataset):
        """
        Return whichever representation of the data
        is currently being displayed.

        This does NOT apply resolution reduction yet.
        """

        if self.graph_mode == "per_iteration":

            return dataset["raw_values"]

        return dataset["values"]


    # =========================================================================
    # POINT RESOLUTION
    # =========================================================================

    def average_points(self, values):
        """
        Reduce the number of displayed points by averaging
        groups of consecutive values.

        Example:

            resolution = 5

            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        becomes:

            [3, 8]

        The final incomplete group is also averaged.

        Example:

            [1, 2, 3, 4, 5, 6, 7]

        becomes:

            [3, 6.5]
        """

        if self.resolution <= 1:

            return values


        result = []

        resolution = self.resolution


        for start in range(
            0,
            len(values),
            resolution
        ):

            group = values[
                start:start + resolution
            ]


            if not group:
                continue


            average = (
                sum(group) / len(group)
            )


            result.append(
                average
            )


        return result


    def get_display_values(self, dataset):
        """
        Get the currently selected data representation
        and apply point averaging.
        """

        values = self.get_dataset_values(
            dataset
        )


        return self.average_points(
            values
        )


    def get_display_points(self, dataset):
        """
        Return (x, y) points for the graph.

        The Y value is averaged according to resolution.

        The X position represents the center of the group
        in terms of the original iteration number.

        Example with resolution 5:

            iterations 0-4
            -> x = 2

            iterations 5-9
            -> x = 7

        This means the X axis still represents iterations,
        rather than the number of averaged points.
        """

        values = self.get_dataset_values(
            dataset
        )


        if not values:
            return []


        if self.resolution <= 1:

            return [
                (i, value)
                for i, value
                in enumerate(values)
            ]


        points = []

        resolution = self.resolution


        for start in range(
            0,
            len(values),
            resolution
        ):

            group = values[
                start:start + resolution
            ]


            if not group:
                continue


            average = (
                sum(group) / len(group)
            )


            # Put the averaged point in the
            # middle of its original range.

            center = (
                start
                + (len(group) - 1) / 2
            )


            points.append(
                (
                    center,
                    average
                )
            )


        return points


    def decrease_resolution(self):

        current_index = (
            RESOLUTION_OPTIONS.index(
                self.resolution
            )
        )


        if current_index > 0:

            self.resolution = (
                RESOLUTION_OPTIONS[
                    current_index - 1
                ]
            )


        self.recalculate_scale()

        self.dirty = True


    def increase_resolution(self):

        current_index = (
            RESOLUTION_OPTIONS.index(
                self.resolution
            )
        )


        if current_index < (
            len(RESOLUTION_OPTIONS) - 1
        ):

            self.resolution = (
                RESOLUTION_OPTIONS[
                    current_index + 1
                ]
            )


        self.recalculate_scale()

        self.dirty = True


    def reset_resolution(self):

        self.resolution = 1

        self.recalculate_scale()

        self.dirty = True


    # =========================================================================
    # GRAPH MODE
    # =========================================================================

    def toggle_graph_mode(self):
        """
        Toggle between:

            cumulative
            per iteration

        and recalculate the graph scale.
        """

        if self.graph_mode == "cumulative":

            self.graph_mode = "per_iteration"

        else:

            self.graph_mode = "cumulative"


        self.recalculate_scale()

        self.dirty = True


    # =========================================================================
    # SCALE
    # =========================================================================

    def recalculate_scale(self):

        enabled = self.get_enabled_datasets()


        if not enabled:

            self.max_x = 1
            self.max_y = 1

            return


        # ---------------------------------------------------------------------
        # X axis
        #
        # IMPORTANT:
        #
        # X remains based on the ORIGINAL number of iterations.
        #
        # Resolution only reduces the number of rendered points.
        # ---------------------------------------------------------------------

        self.max_x = max(
            len(
                self.get_dataset_values(dataset)
            )
            for dataset in enabled
        )


        self.max_x = max(
            self.max_x,
            1
        )


        # ---------------------------------------------------------------------
        # Y axis
        #
        # Uses the averaged values when resolution > 1.
        # ---------------------------------------------------------------------

        self.max_y = max(
            (
                max(
                    self.get_display_values(
                        dataset
                    ),
                    default=0
                )

                for dataset in enabled
            ),
            default=1
        )


        self.max_y = max(
            self.max_y,
            1
        )


    # =========================================================================
    # DATASET SELECTION
    # =========================================================================

    def toggle_dataset(self, index):

        if 0 <= index < len(self.datasets):

            self.datasets[index]["enabled"] = (
                not self.datasets[index]["enabled"]
            )

            self.recalculate_scale()

            self.dirty = True


    def enable_all(self):

        for dataset in self.datasets:

            dataset["enabled"] = True


        self.recalculate_scale()

        self.dirty = True


    def disable_all(self):

        for dataset in self.datasets:

            dataset["enabled"] = False


        self.recalculate_scale()

        self.dirty = True


    def reset(self):

        for dataset in self.datasets:

            dataset["enabled"] = True


        # Reset graph mode.

        self.graph_mode = "cumulative"


        # Reset point resolution.

        self.resolution = 1


        self.recalculate_scale()

        self.dirty = True


    # =========================================================================
    # COORDINATE CONVERSION
    # =========================================================================

    def data_to_screen(self, x, y):

        if self.max_x <= 1:

            x_ratio = 0

        else:

            x_ratio = (
                x / (self.max_x - 1)
            )


        y_ratio = (
            y / self.max_y
        )


        screen_x = (
            self.rect.left
            + x_ratio * self.rect.width
        )


        screen_y = (
            self.rect.bottom
            - y_ratio * self.rect.height
        )


        return (
            round(screen_x),
            round(screen_y)
        )


    # =========================================================================
    # GRID
    # =========================================================================

    def draw_grid(self, screen):

        horizontal_lines = 10
        vertical_lines = 10


        # ---------------------------------------------------------------------
        # Horizontal grid
        # ---------------------------------------------------------------------

        for i in range(
            horizontal_lines + 1
        ):

            ratio = (
                i / horizontal_lines
            )


            y = (
                self.rect.bottom
                - ratio * self.rect.height
            )


            pygame.draw.line(
                screen,
                GRID_COLOR,
                (
                    self.rect.left,
                    round(y)
                ),
                (
                    self.rect.right,
                    round(y)
                ),
                1
            )


            value = (
                ratio * self.max_y
            )


            label = self.small_font.render(
                self.format_number(value),
                True,
                TEXT_COLOR
            )


            screen.blit(
                label,
                (
                    self.rect.left
                    - label.get_width()
                    - 10,

                    round(y)
                    - label.get_height() // 2
                )
            )


        # ---------------------------------------------------------------------
        # Vertical grid
        # ---------------------------------------------------------------------

        for i in range(
            vertical_lines + 1
        ):

            ratio = (
                i / vertical_lines
            )


            x = (
                self.rect.left
                + ratio * self.rect.width
            )


            pygame.draw.line(
                screen,
                GRID_COLOR,
                (
                    round(x),
                    self.rect.top
                ),
                (
                    round(x),
                    self.rect.bottom
                ),
                1
            )


            value = (
                ratio * self.max_x
            )


            label = self.small_font.render(
                str(round(value)),
                True,
                TEXT_COLOR
            )


            screen.blit(
                label,
                (
                    round(x)
                    - label.get_width() // 2,

                    self.rect.bottom + 8
                )
            )


        # ---------------------------------------------------------------------
        # Axes
        # ---------------------------------------------------------------------

        pygame.draw.line(
            screen,
            AXIS_COLOR,
            self.rect.topleft,
            self.rect.bottomleft,
            2
        )


        pygame.draw.line(
            screen,
            AXIS_COLOR,
            self.rect.bottomleft,
            self.rect.bottomright,
            2
        )


    # =========================================================================
    # DATASET DRAWING
    # =========================================================================

    def draw_dataset(
        self,
        screen,
        dataset,
        hovered=False
    ):

        # ---------------------------------------------------------------------
        # Get points after applying the current resolution.
        # ---------------------------------------------------------------------

        data_points = self.get_display_points(
            dataset
        )


        if not data_points:
            return


        # Convert data coordinates to screen coordinates.

        points = [
            self.data_to_screen(
                x,
                value
            )

            for x, value in data_points
        ]


        color = dataset["color"]


        # ---------------------------------------------------------------------
        # Highlight hovered dataset.
        # ---------------------------------------------------------------------

        width = (
            4
            if hovered
            else 2
        )


        # ---------------------------------------------------------------------
        # Draw anti-aliased graph line.
        # ---------------------------------------------------------------------

        if len(points) >= 2:

            pygame.draw.aalines(
                screen,
                color,
                False,
                points,
                width
            )


        # ---------------------------------------------------------------------
        # Draw individual points for smaller datasets.
        #
        # With resolution reduction enabled, this becomes much
        # less likely to turn into a giant blob.
        # ---------------------------------------------------------------------

        if len(points) <= 500:

            radius = (
                3
                if hovered
                else 2
            )


            for point in points:

                pygame.draw.circle(
                    screen,
                    color,
                    point,
                    radius
                )


    # =========================================================================
    # LEGEND
    # =========================================================================

    def get_legend_rect(self, index):

        return pygame.Rect(
            LEGEND_X - 10,
            LEGEND_Y
            + index * 30
            - 4,
            270,
            28
        )


    def draw_legend(
        self,
        screen,
        mouse_position
    ):

        title = self.font.render(
            "Datasets",
            True,
            TEXT_COLOR
        )


        screen.blit(
            title,
            (
                LEGEND_X,
                LEGEND_Y - 35
            )
        )


        for index, dataset in enumerate(
            self.datasets
        ):

            rect = self.get_legend_rect(
                index
            )


            hovered = rect.collidepoint(
                mouse_position
            )


            # Highlight row on hover.

            if hovered:

                pygame.draw.rect(
                    screen,
                    HOVER_COLOR,
                    rect,
                    border_radius=4
                )


            color = dataset["color"]


            # If disabled, make colour darker.

            if dataset["enabled"]:

                line_color = color

            else:

                line_color = (
                    color[0] // 3,
                    color[1] // 3,
                    color[2] // 3
                )


            pygame.draw.line(
                screen,
                line_color,
                (
                    LEGEND_X,
                    rect.centery
                ),
                (
                    LEGEND_X + 25,
                    rect.centery
                ),
                4
            )


            text_color = (
                TEXT_COLOR
                if dataset["enabled"]
                else MUTED_TEXT
            )


            text = self.font.render(
                dataset["name"],
                True,
                text_color
            )


            screen.blit(
                text,
                (
                    LEGEND_X + 35,
                    rect.top + 4
                )
            )


    # =========================================================================
    # STATUS
    # =========================================================================

    def draw_status(self, screen):

        enabled = (
            self.get_enabled_datasets()
        )


        # ---------------------------------------------------------------------
        # Dataset count
        # ---------------------------------------------------------------------

        text = (
            f"{len(enabled)} / "
            f"{len(self.datasets)} datasets"
        )


        label = self.small_font.render(
            text,
            True,
            TEXT_COLOR
        )


        screen.blit(
            label,
            (
                LEGEND_X + 40,
                HEIGHT - 225
            )
        )


        # ---------------------------------------------------------------------
        # Current graph mode
        # ---------------------------------------------------------------------

        if self.graph_mode == "cumulative":

            mode_text = "Mode: cumulative"

        else:

            mode_text = "Mode: per iteration"


        mode_label = self.small_font.render(
            mode_text,
            True,
            TEXT_COLOR
        )


        screen.blit(
            mode_label,
            (
                LEGEND_X + 40,
                HEIGHT - 207
            )
        )


        # ---------------------------------------------------------------------
        # Current point resolution
        # ---------------------------------------------------------------------

        if self.resolution == 1:

            resolution_text = (
                "Resolution: 1 (raw)"
            )

        else:

            resolution_text = (
                f"Resolution: {self.resolution} "
                f"(avg)"
            )


        resolution_label = self.small_font.render(
            resolution_text,
            True,
            TEXT_COLOR
        )


        screen.blit(
            resolution_label,
            (
                LEGEND_X + 40,
                HEIGHT - 189
            )
        )


        # ---------------------------------------------------------------------
        # Instructions
        # ---------------------------------------------------------------------

        instructions = [
            "Click dataset: toggle",
            "A: enable all",
            "N: disable all",
            "R: reset",
            "P: toggle graph mode",
            "Z/U: point resolution",
            "0: raw resolution",
            "S: save graph",
        ]


        y = HEIGHT - 167


        for instruction in instructions:

            label = self.small_font.render(
                instruction,
                True,
                MUTED_TEXT
            )


            screen.blit(
                label,
                (
                    LEGEND_X + 40,
                    y
                )
            )


            y += 18


    # =========================================================================
    # DRAW EVERYTHING
    # =========================================================================

    def rebuild(
        self,
        mouse_position
    ):

        self.surface.fill(
            BACKGROUND
        )


        enabled = (
            self.get_enabled_datasets()
        )


        if enabled:

            self.draw_grid(
                self.surface
            )


            for dataset in enabled:

                self.draw_dataset(
                    self.surface,
                    dataset
                )

        else:

            # Nothing selected.

            text = self.font.render(
                "No datasets selected",
                True,
                MUTED_TEXT
            )


            self.surface.blit(
                text,
                (
                    self.rect.centerx
                    - text.get_width() // 2,

                    self.rect.centery
                    - text.get_height() // 2
                )
            )


        self.draw_legend(
            self.surface,
            mouse_position
        )


        self.draw_status(
            self.surface
        )


        self.dirty = False


    def draw(
        self,
        screen,
        mouse_position
    ):

        # Rebuild every frame so legend hover
        # works correctly.

        self.rebuild(
            mouse_position
        )


        screen.blit(
            self.surface,
            (0, 0)
        )


    # =========================================================================
    # UTILITY
    # =========================================================================

    @staticmethod
    def format_number(value):

        if value >= 1_000_000:

            return (
                f"{value / 1_000_000:.1f}M"
            )


        if value >= 1_000:

            return (
                f"{value / 1_000:.1f}k"
            )


        if value < 1:

            return f"{value:.3f}"


        return f"{value:.0f}"


# =============================================================================
# STATISTICS
# =============================================================================

def print_statistics(datasets):

    results = []


    for dataset in datasets:

        # Statistics always use total cumulative time,
        # regardless of which graph mode is selected.

        values = dataset["values"]


        if not values:
            continue


        results.append(
            (
                dataset["name"],
                values[-1]
            )
        )


    results.sort(
        key=lambda x: x[1]
    )


    if not results:
        return


    fastest = results[0][1]


    print()
    print("Performance")
    print("-" * 70)


    for name, total in results:

        slowdown = (
            total / fastest
        )


        print(
            f"{name:<35}"
            f"{total:>12.2f} ms"
            f"   {slowdown:>8.2f}x"
        )


# =============================================================================
# SAVE
# =============================================================================

def save_graph(graph):

    base_name = "Graph"
    extension = ".png"

    filename = f"{base_name}{extension}"
    counter = 1

    while os.path.exists(filename):
        filename = f"{base_name}_{counter}{extension}"
        counter += 1

    pygame.image.save(
        graph.surface,
        filename
    )

    print(
        f"Saved graph to {filename}"
    )


# =============================================================================
# MAIN
# =============================================================================

def main():

    pygame.init()


    screen = pygame.display.set_mode(
        (
            WIDTH,
            HEIGHT
        )
    )


    pygame.display.set_caption(
        "Conway's Game of Life - Performance"
    )


    clock = pygame.time.Clock()


    # -------------------------------------------------------------------------
    # Load data
    # -------------------------------------------------------------------------

    datasets = load_datasets()


    print_statistics(
        datasets
    )


    # -------------------------------------------------------------------------
    # Create graph
    # -------------------------------------------------------------------------

    graph = Graph(
        GRAPH_RECT
    )


    graph.set_data(
        datasets
    )


    # Initial mouse position.

    mouse_position = pygame.mouse.get_pos()


    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------

    running = True


    while running:

        mouse_position = pygame.mouse.get_pos()


        for event in pygame.event.get():

            # =================================================================
            # Window closed
            # =================================================================

            if event.type == pygame.QUIT:

                running = False


            # =================================================================
            # Mouse click
            # =================================================================

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    for index in range(
                        len(graph.datasets)
                    ):

                        rect = (
                            graph.get_legend_rect(
                                index
                            )
                        )


                        if rect.collidepoint(
                            event.pos
                        ):

                            graph.toggle_dataset(
                                index
                            )

                            break


            # =================================================================
            # Keyboard
            # =================================================================

            elif event.type == pygame.KEYDOWN:

                # -------------------------------------------------------------
                # Enable everything
                # -------------------------------------------------------------

                if event.key == pygame.K_a:

                    graph.enable_all()


                # -------------------------------------------------------------
                # Disable everything
                # -------------------------------------------------------------

                elif event.key == pygame.K_n:

                    graph.disable_all()


                # -------------------------------------------------------------
                # Reset
                # -------------------------------------------------------------

                elif event.key == pygame.K_r:

                    graph.reset()


                # -------------------------------------------------------------
                # Toggle cumulative / per iteration
                # -------------------------------------------------------------

                elif event.key == pygame.K_p:

                    graph.toggle_graph_mode()


                # -------------------------------------------------------------
                # Decrease point resolution
                # -------------------------------------------------------------

                elif event.key == pygame.K_z:

                    graph.decrease_resolution()


                # -------------------------------------------------------------
                # Increase point resolution
                # -------------------------------------------------------------

                elif event.key == pygame.K_u:

                    graph.increase_resolution()


                # -------------------------------------------------------------
                # Reset point resolution to raw
                # -------------------------------------------------------------

                elif event.key == pygame.K_0:

                    graph.reset_resolution()


                # -------------------------------------------------------------
                # Save
                # -------------------------------------------------------------

                elif event.key == pygame.K_s:

                    save_graph(
                        graph
                    )


        # ---------------------------------------------------------------------
        # Draw
        # ---------------------------------------------------------------------

        graph.draw(
            screen,
            mouse_position
        )


        pygame.display.flip()


        clock.tick(FPS)


    pygame.quit()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    main()