import csv
import sys
import math
from pathlib import Path
from datetime import datetime

import pygame


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = "../Data_V1.2/csv_periter.csv"

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

FPS = 60

# Graph area
GRAPH_LEFT = 80
GRAPH_RIGHT = WINDOW_WIDTH - 40
GRAPH_TOP = 70
GRAPH_BOTTOM = WINDOW_HEIGHT - 100

# Number of original generations combined into one averaged point
GRAPH_BUCKET_SIZE = 100

# When more than this many generations are visible,
# use averaged data instead of individual measurements.
FULL_RESOLUTION_THRESHOLD = 1500

# Padding above the highest timing value
Y_PADDING_FACTOR = 1.15

# Y zoom limits
MIN_Y_FACTOR = 0.05
MAX_Y_FACTOR = 100.0


# ============================================================
# COLORS
# ============================================================

BACKGROUND_COLOR = (18, 20, 24)
GRAPH_BACKGROUND = (25, 28, 34)
GRID_COLOR = (55, 60, 70)
TEXT_COLOR = (225, 228, 235)
MUTED_TEXT_COLOR = (150, 155, 165)
AXIS_COLOR = (130, 135, 145)


# ============================================================
# LANGUAGE COLORS
# ============================================================

LANGUAGE_BASE_COLORS = {
    "cr": (70, 145, 255),     # C++ / raylib
    "pp": (255, 185, 65),     # Python / Pygame
    "cs": (100, 210, 125),    # C# / OpenTK
    "js": (235, 95, 95),      # JavaScript / HTML Canvas
}

LANGUAGE_NAMES = {
    "cr": "C++ / raylib",
    "pp": "Python / Pygame",
    "cs": "C# / OpenTK",
    "js": "JavaScript / HTML Canvas",
}


# ============================================================
# CSV FIELD SIZE
# ============================================================

# The timing list can be much larger than Python's default
# CSV field size limit.

try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(2**31 - 1)


# ============================================================
# VALUE PARSING
# ============================================================

def parse_time_value(value):
    """
    Convert one timing value to a float.

    Handles:
        890.689
        3,0083169999999995
        6.95175e-310

    Extremely tiny e-310 values are treated as invalid.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    # Remove surrounding quotes
    if len(value) >= 2:

        if (
            (value[0] == "'" and value[-1] == "'")
            or
            (value[0] == '"' and value[-1] == '"')
        ):
            value = value[1:-1]

    # Handle decimal comma
    if "," in value and "." not in value:
        value = value.replace(",", ".")

    try:
        number = float(value)

    except ValueError:
        return None

    # Ignore NaN / infinity
    if not math.isfinite(number):
        return None

    # Ignore extremely tiny garbage/uninitialized values
    if abs(number) < 1e-10:
        return None

    # Negative execution times are invalid
    if number < 0:
        return None

    return number


# ============================================================
# TIMING LIST PARSER
# ============================================================

def parse_timing_list(raw):
    """
    Convert:

        ['12.5', '14.2', '890.1']

    into:

        [12.5, 14.2, 890.1]
    """

    if raw is None:
        return []

    raw = raw.strip()

    # Remove outer quotes
    if len(raw) >= 2:

        if (
            (raw[0] == '"' and raw[-1] == '"')
            or
            (raw[0] == "'" and raw[-1] == "'")
        ):
            raw = raw[1:-1]

    # Remove list brackets
    if raw.startswith("["):
        raw = raw[1:]

    if raw.endswith("]"):
        raw = raw[:-1]

    if not raw:
        return []

    parts = raw.split(",")

    values = []

    for part in parts:

        value = parse_time_value(part)

        values.append(value)

    return values


# ============================================================
# COLOR SHADING
# ============================================================

def shade_color(base_color, index, total):
    """
    Give each simulation within the same language a different
    shade while preserving the language's base color.
    """

    if total <= 1:
        return base_color

    position = index / max(1, total - 1)

    factor = 0.70 + position * 0.60

    r = max(
        0,
        min(
            255,
            int(base_color[0] * factor)
        )
    )

    g = max(
        0,
        min(
            255,
            int(base_color[1] * factor)
        )
    )

    b = max(
        0,
        min(
            255,
            int(base_color[2] * factor)
        )
    )

    return (r, g, b)


# ============================================================
# SIMULATION
# ============================================================

class Simulation:

    def __init__(
        self,
        language,
        logic,
        attribute,
        world_size,
        simulation_index,
        times
    ):

        self.language = language
        self.logic = logic
        self.attribute = attribute
        self.world_size = world_size
        self.simulation_index = simulation_index

        # Full-resolution timing data
        self.times = times

        # Cached maximum.
        #
        # This is VERY important for performance because we
        # never have to scan self.times during rendering.
        self.max_time = 0.0

        # Precomputed averaged data.
        #
        # Format:
        #
        #     [(generation, average), ...]
        #
        self.averaged_times = []

        # Calculate expensive information once
        self.prepare_data()


    # ========================================================
    # PREPARE DATA
    # ========================================================

    def prepare_data(self):

        # ----------------------------------------------------
        # Find maximum timing value ONCE
        # ----------------------------------------------------

        maximum = 0.0

        for value in self.times:

            if value is None:
                continue

            if value > maximum:
                maximum = value

        self.max_time = maximum

        # ----------------------------------------------------
        # Build averaged data ONCE
        # ----------------------------------------------------

        bucket_size = GRAPH_BUCKET_SIZE

        total = len(self.times)

        averaged = []

        for start in range(
            0,
            total,
            bucket_size
        ):

            end = min(
                start + bucket_size,
                total
            )

            bucket = self.times[
                start:end
            ]

            total_value = 0.0
            count = 0

            for value in bucket:

                if value is None:
                    continue

                total_value += value
                count += 1

            if count == 0:
                continue

            average = (
                total_value / count
            )

            # Middle of the bucket
            generation = (
                start
                + (end - start - 1) / 2
            )

            averaged.append(
                (
                    generation,
                    average
                )
            )

        self.averaged_times = averaged


# ============================================================
# GRAPH ENGINE
# ============================================================

class GraphEngine:

    def __init__(self, simulations):

        self.simulations = simulations

        # ----------------------------------------------------
        # Filters
        # ----------------------------------------------------

        self.language_filter = None
        self.logic_filter = None
        self.attribute_filter = None
        self.world_size_filter = None

        # ----------------------------------------------------
        # Cached global information
        # ----------------------------------------------------

        self.global_max_time = 1.0
        self.max_generation = 1

        self.recalculate_global_cache()

        # ----------------------------------------------------
        # View
        # ----------------------------------------------------

        self.x_min = 0.0
        self.x_max = float(
            self.max_generation
        )

        self.y_min = 0.0

        # Y zoom multiplier
        self.y_max_factor = 1.0

        # ----------------------------------------------------
        # Interaction
        # ----------------------------------------------------

        self.dragging = False
        self.last_mouse_pos = None

        self.show_legend = True

        # ----------------------------------------------------
        # Pygame
        # ----------------------------------------------------

        pygame.init()

        pygame.display.set_caption(
            "CGOL Performance Graph"
        )

        self.screen = pygame.display.set_mode(
            (
                WINDOW_WIDTH,
                WINDOW_HEIGHT
            )
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "Arial",
            16
        )

        self.small_font = pygame.font.SysFont(
            "Arial",
            13
        )

        self.title_font = pygame.font.SysFont(
            "Arial",
            22,
            bold=True
        )

        self.reset_view()


    # ========================================================
    # GLOBAL CACHE
    # ========================================================

    def recalculate_global_cache(self):

        maximum = 1.0
        generation_max = 1

        for simulation in self.simulations:

            if simulation.max_time > maximum:
                maximum = simulation.max_time

            if len(simulation.times) > generation_max:
                generation_max = len(
                    simulation.times
                )

        self.global_max_time = maximum
        self.max_generation = generation_max


    # ========================================================
    # FILTERING
    # ========================================================

    def get_visible_simulations(self):

        visible = []

        for simulation in self.simulations:

            if (
                self.language_filter is not None
                and simulation.language
                != self.language_filter
            ):
                continue

            if (
                self.logic_filter is not None
                and simulation.logic
                != self.logic_filter
            ):
                continue

            if (
                self.attribute_filter is not None
                and simulation.attribute
                != self.attribute_filter
            ):
                continue

            if (
                self.world_size_filter is not None
                and simulation.world_size
                != self.world_size_filter
            ):
                continue

            visible.append(
                simulation
            )

        return visible


    # ========================================================
    # Y MAX
    # ========================================================

    def get_base_y_max(self):

        visible = self.get_visible_simulations()

        # If there is a filter, we need to find the maximum
        # among the visible simulations.
        #
        # IMPORTANT:
        # We use cached simulation.max_time values.
        # No 10,000-point arrays are scanned here.

        maximum = 1.0

        for simulation in visible:

            if simulation.max_time > maximum:

                maximum = (
                    simulation.max_time
                )

        return (
            maximum
            * Y_PADDING_FACTOR
        )


    # ========================================================
    # RESET VIEW
    # ========================================================

    def reset_view(self):

        self.x_min = 0.0

        self.x_max = float(
            self.max_generation
        )

        self.y_min = 0.0

        self.y_max_factor = 1.0


    # ========================================================
    # GRAPH -> SCREEN
    # ========================================================

    def graph_to_screen(
        self,
        generation,
        time_value
    ):

        graph_width = (
            GRAPH_RIGHT
            - GRAPH_LEFT
        )

        graph_height = (
            GRAPH_BOTTOM
            - GRAPH_TOP
        )

        x_range = (
            self.x_max
            - self.x_min
        )

        if x_range <= 0:
            x_range = 1

        x_ratio = (
            generation
            - self.x_min
        ) / x_range

        y_max = (
            self.get_base_y_max()
            * self.y_max_factor
        )

        if y_max <= self.y_min:
            y_max = (
                self.y_min
                + 1
            )

        y_ratio = (
            time_value
            - self.y_min
        ) / (
            y_max
            - self.y_min
        )

        screen_x = (
            GRAPH_LEFT
            + x_ratio
            * graph_width
        )

        screen_y = (
            GRAPH_BOTTOM
            - y_ratio
            * graph_height
        )

        return (
            screen_x,
            screen_y
        )


    # ========================================================
    # SCREEN -> GRAPH
    # ========================================================

    def screen_to_graph(
        self,
        screen_x,
        screen_y
    ):

        graph_width = (
            GRAPH_RIGHT
            - GRAPH_LEFT
        )

        graph_height = (
            GRAPH_BOTTOM
            - GRAPH_TOP
        )

        x_ratio = (
            screen_x
            - GRAPH_LEFT
        ) / graph_width

        generation = (
            self.x_min
            + x_ratio
            * (
                self.x_max
                - self.x_min
            )
        )

        y_max = (
            self.get_base_y_max()
            * self.y_max_factor
        )

        y_ratio = (
            GRAPH_BOTTOM
            - screen_y
        ) / graph_height

        value = (
            self.y_min
            + y_ratio
            * (
                y_max
                - self.y_min
            )
        )

        return (
            generation,
            value
        )


    # ========================================================
    # DRAW GRID
    # ========================================================

    def draw_grid(self):

        pygame.draw.rect(
            self.screen,
            GRAPH_BACKGROUND,
            (
                GRAPH_LEFT,
                GRAPH_TOP,
                GRAPH_RIGHT - GRAPH_LEFT,
                GRAPH_BOTTOM - GRAPH_TOP
            )
        )

        graph_width = (
            GRAPH_RIGHT
            - GRAPH_LEFT
        )

        graph_height = (
            GRAPH_BOTTOM
            - GRAPH_TOP
        )

        # ----------------------------------------------------
        # Vertical grid
        # ----------------------------------------------------

        visible_range = (
            self.x_max
            - self.x_min
        )

        if visible_range <= 20:
            x_step = 1

        elif visible_range <= 100:
            x_step = 10

        elif visible_range <= 500:
            x_step = 50

        elif visible_range <= 2000:
            x_step = 200

        elif visible_range <= 10000:
            x_step = 1000

        else:
            x_step = 5000

        first_x = (
            math.floor(
                self.x_min / x_step
            )
            * x_step
        )

        generation = first_x

        while generation <= self.x_max:

            screen_x, _ = (
                self.graph_to_screen(
                    generation,
                    self.y_min
                )
            )

            if (
                GRAPH_LEFT
                <= screen_x
                <= GRAPH_RIGHT
            ):

                pygame.draw.line(
                    self.screen,
                    GRID_COLOR,
                    (
                        int(screen_x),
                        GRAPH_TOP
                    ),
                    (
                        int(screen_x),
                        GRAPH_BOTTOM
                    )
                )

                label = self.small_font.render(
                    str(int(generation)),
                    True,
                    MUTED_TEXT_COLOR
                )

                self.screen.blit(
                    label,
                    (
                        int(screen_x)
                        - label.get_width() // 2,
                        GRAPH_BOTTOM + 8
                    )
                )

            generation += x_step

        # ----------------------------------------------------
        # Horizontal grid
        # ----------------------------------------------------

        y_max = (
            self.get_base_y_max()
            * self.y_max_factor
        )

        if y_max <= 0:
            y_max = 1

        y_divisions = 8

        for i in range(
            y_divisions + 1
        ):

            value = (
                self.y_min
                + (
                    y_max
                    - self.y_min
                )
                * i
                / y_divisions
            )

            screen_y = (
                GRAPH_BOTTOM
                - (
                    (
                        value
                        - self.y_min
                    )
                    / (
                        y_max
                        - self.y_min
                    )
                )
                * graph_height
            )

            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (
                    GRAPH_LEFT,
                    int(screen_y)
                ),
                (
                    GRAPH_RIGHT,
                    int(screen_y)
                )
            )

            if value >= 1000:
                text = f"{value:.0f}"

            elif value >= 10:
                text = f"{value:.1f}"

            else:
                text = f"{value:.2f}"

            label = self.small_font.render(
                text,
                True,
                MUTED_TEXT_COLOR
            )

            self.screen.blit(
                label,
                (
                    GRAPH_LEFT
                    - label.get_width()
                    - 8,
                    int(screen_y)
                    - label.get_height() // 2
                )
            )

        # ----------------------------------------------------
        # Axes
        # ----------------------------------------------------

        pygame.draw.line(
            self.screen,
            AXIS_COLOR,
            (
                GRAPH_LEFT,
                GRAPH_BOTTOM
            ),
            (
                GRAPH_RIGHT,
                GRAPH_BOTTOM
            ),
            2
        )

        pygame.draw.line(
            self.screen,
            AXIS_COLOR,
            (
                GRAPH_LEFT,
                GRAPH_TOP
            ),
            (
                GRAPH_LEFT,
                GRAPH_BOTTOM
            ),
            2
        )


    # ========================================================
    # DRAW ONE SIMULATION
    # ========================================================

    def draw_simulation(
        self,
        simulation,
        color
    ):

        visible_range = (
            self.x_max
            - self.x_min
        )

        # ----------------------------------------------------
        # Select resolution
        # ----------------------------------------------------

        use_averaged = (
            visible_range
            > FULL_RESOLUTION_THRESHOLD
        )

        if use_averaged:

            data = (
                simulation.averaged_times
            )

            # Since averaged data is sorted by generation,
            # we can directly calculate which buckets matter.
            bucket_size = (
                GRAPH_BUCKET_SIZE
            )

            start_index = max(
                0,
                int(
                    self.x_min
                    / bucket_size
                ) - 1
            )

            end_index = min(
                len(data),
                int(
                    self.x_max
                    / bucket_size
                ) + 2
            )

            data_to_draw = data[
                start_index:end_index
            ]

            points = []

            for generation, value in data_to_draw:

                screen_x, screen_y = (
                    self.graph_to_screen(
                        generation,
                        value
                    )
                )

                # Skip points far outside graph
                if (
                    screen_x
                    < GRAPH_LEFT - 2
                ):
                    continue

                if (
                    screen_x
                    > GRAPH_RIGHT + 2
                ):
                    continue

                if (
                    screen_y
                    < GRAPH_TOP - 50
                ):
                    continue

                if (
                    screen_y
                    > GRAPH_BOTTOM + 50
                ):
                    continue

                points.append(
                    (
                        int(screen_x),
                        int(screen_y)
                    )
                )

        # ----------------------------------------------------
        # Full-resolution mode
        # ----------------------------------------------------

        else:

            start_generation = max(
                0,
                int(
                    self.x_min
                ) - 1
            )

            end_generation = min(
                len(
                    simulation.times
                ),
                int(
                    self.x_max
                ) + 2
            )

            points = []

            for generation in range(
                start_generation,
                end_generation
            ):

                value = (
                    simulation.times[
                        generation
                    ]
                )

                if value is None:
                    continue

                screen_x, screen_y = (
                    self.graph_to_screen(
                        generation,
                        value
                    )
                )

                if (
                    screen_x
                    < GRAPH_LEFT - 2
                ):
                    continue

                if (
                    screen_x
                    > GRAPH_RIGHT + 2
                ):
                    continue

                if (
                    screen_y
                    < GRAPH_TOP - 50
                ):
                    continue

                if (
                    screen_y
                    > GRAPH_BOTTOM + 50
                ):
                    continue

                points.append(
                    (
                        int(screen_x),
                        int(screen_y)
                    )
                )

        # ----------------------------------------------------
        # Draw line
        # ----------------------------------------------------

        if len(points) >= 2:

            pygame.draw.lines(
                self.screen,
                color,
                False,
                points,
                2
            )

        elif len(points) == 1:

            pygame.draw.circle(
                self.screen,
                color,
                points[0],
                2
            )


    # ========================================================
    # LEGEND
    # ========================================================

    def draw_legend(self):

        if not self.show_legend:
            return

        visible = (
            self.get_visible_simulations()
        )

        if not visible:
            return

        x = GRAPH_LEFT + 15
        y = GRAPH_TOP + 15

        # Group by language
        language_counts = {}

        for simulation in visible:

            language_counts[
                simulation.language
            ] = (
                language_counts.get(
                    simulation.language,
                    0
                ) + 1
            )

        language_indices = {}

        legend_entries = []

        for simulation in visible:

            language = (
                simulation.language
            )

            index = language_indices.get(
                language,
                0
            )

            language_indices[
                language
            ] = index + 1

            base_color = (
                LANGUAGE_BASE_COLORS.get(
                    language,
                    (200, 200, 200)
                )
            )

            total = (
                language_counts[
                    language
                ]
            )

            color = shade_color(
                base_color,
                index,
                total
            )

            label = (
                self.make_simulation_label(
                    simulation
                )
            )

            legend_entries.append(
                (
                    color,
                    label
                )
            )

        # Don't let the legend consume the entire screen
        max_entries = 25

        if len(legend_entries) > max_entries:

            legend_entries = (
                legend_entries[
                    :max_entries
                ]
            )

        box_width = 390

        box_height = (
            30
            + len(legend_entries)
            * 20
        )

        surface = pygame.Surface(
            (
                box_width,
                box_height
            ),
            pygame.SRCALPHA
        )

        surface.fill(
            (
                10,
                12,
                16,
                220
            )
        )

        self.screen.blit(
            surface,
            (
                x,
                y
            )
        )

        title = self.small_font.render(
            "Simulations",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            title,
            (
                x + 10,
                y + 7
            )
        )

        current_y = y + 28

        for color, label in legend_entries:

            pygame.draw.line(
                self.screen,
                color,
                (
                    x + 10,
                    current_y + 7
                ),
                (
                    x + 32,
                    current_y + 7
                ),
                3
            )

            text = self.small_font.render(
                label,
                True,
                TEXT_COLOR
            )

            self.screen.blit(
                text,
                (
                    x + 40,
                    current_y
                )
            )

            current_y += 20


    # ========================================================
    # LABEL
    # ========================================================

    def make_simulation_label(
        self,
        simulation
    ):

        language_name = (
            LANGUAGE_NAMES.get(
                simulation.language,
                simulation.language
            )
        )

        logic = (
            simulation.logic
            if simulation.logic
            else "-"
        )

        attribute = (
            simulation.attribute
            if simulation.attribute
            else "-"
        )

        return (
            f"{language_name} | "
            f"{logic} | "
            f"{attribute} | "
            f"{simulation.world_size}"
        )


    # ========================================================
    # HEADER
    # ========================================================

    def draw_header(self):

        title = self.title_font.render(
            "CGOL Performance Graph",
            True,
            TEXT_COLOR
        )

        self.screen.blit(
            title,
            (
                GRAPH_LEFT,
                18
            )
        )

        visible = (
            self.get_visible_simulations()
        )

        visible_range = (
            self.x_max
            - self.x_min
        )

        if visible_range > FULL_RESOLUTION_THRESHOLD:

            resolution_text = (
                "averaged"
            )

        else:

            resolution_text = (
                "full resolution"
            )

        info = (
            f"{len(visible)} simulations"
            f"   |   "
            f"X: {self.x_min:.0f}"
            f" - "
            f"{self.x_max:.0f}"
            f"   |   "
            f"{resolution_text}"
        )

        text = self.small_font.render(
            info,
            True,
            MUTED_TEXT_COLOR
        )

        self.screen.blit(
            text,
            (
                GRAPH_LEFT,
                GRAPH_BOTTOM + 45
            )
        )


    # ========================================================
    # CONTROLS
    # ========================================================

    def draw_controls(self):

        lines = [
            "Mouse wheel     X zoom",
            "Shift + wheel   Y zoom",
            "Middle drag     Pan",
            "Left drag       Pan",
            "L               Toggle legend",
            "R               Reset view",
            "S               Save PNG",
            "ESC             Quit",
        ]

        x = WINDOW_WIDTH - 250
        y = 15

        for line in lines:

            text = self.small_font.render(
                line,
                True,
                MUTED_TEXT_COLOR
            )

            self.screen.blit(
                text,
                (
                    x,
                    y
                )
            )

            y += 17


    # ========================================================
    # SCREENSHOT
    # ========================================================

    def save_screenshot(self):

        timestamp = (
            datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        screenshot_dir = Path(
            "screenshots"
        )

        screenshot_dir.mkdir(
            exist_ok=True
        )

        filename = (
            screenshot_dir
            / f"cgol_graph_{timestamp}.png"
        )

        pygame.image.save(
            self.screen,
            filename
        )

        print(
            f"Screenshot saved: {filename}"
        )


    # ========================================================
    # X ZOOM
    # ========================================================

    def zoom_x(
        self,
        mouse_x,
        zoom_factor
    ):

        if not (
            GRAPH_LEFT
            <= mouse_x
            <= GRAPH_RIGHT
        ):
            return

        old_range = (
            self.x_max
            - self.x_min
        )

        if old_range <= 0:
            return

        # Find generation under mouse
        mouse_generation, _ = (
            self.screen_to_graph(
                mouse_x,
                GRAPH_BOTTOM
            )
        )

        new_range = (
            old_range
            / zoom_factor
        )

        new_range = max(
            1.0,
            min(
                float(self.max_generation),
                new_range
            )
        )

        ratio = (
            mouse_generation
            - self.x_min
        ) / old_range

        self.x_min = (
            mouse_generation
            - ratio
            * new_range
        )

        self.x_max = (
            self.x_min
            + new_range
        )

        self.keep_x_in_bounds()


    # ========================================================
    # Y ZOOM
    # ========================================================

    def zoom_y(
        self,
        mouse_y,
        zoom_factor
    ):

        if not (
            GRAPH_TOP
            <= mouse_y
            <= GRAPH_BOTTOM
        ):
            return

        self.y_max_factor /= zoom_factor

        self.y_max_factor = max(
            MIN_Y_FACTOR,
            min(
                MAX_Y_FACTOR,
                self.y_max_factor
            )
        )


    # ========================================================
    # KEEP X IN BOUNDS
    # ========================================================

    def keep_x_in_bounds(self):

        current_range = (
            self.x_max
            - self.x_min
        )

        max_generation = (
            float(self.max_generation)
        )

        if current_range >= max_generation:

            self.x_min = 0
            self.x_max = max_generation

            return

        if self.x_min < 0:

            self.x_min = 0

            self.x_max = (
                self.x_min
                + current_range
            )

        if self.x_max > max_generation:

            self.x_max = (
                max_generation
            )

            self.x_min = (
                self.x_max
                - current_range
            )

        self.x_min = max(
            0.0,
            self.x_min
        )


    # ========================================================
    # PAN
    # ========================================================

    def pan(
        self,
        dx,
        dy
    ):

        graph_width = (
            GRAPH_RIGHT
            - GRAPH_LEFT
        )

        graph_height = (
            GRAPH_BOTTOM
            - GRAPH_TOP
        )

        # ----------------------------------------------------
        # X
        # ----------------------------------------------------

        x_range = (
            self.x_max
            - self.x_min
        )

        generation_delta = (
            dx
            / graph_width
            * x_range
        )

        self.x_min -= (
            generation_delta
        )

        self.x_max -= (
            generation_delta
        )

        self.keep_x_in_bounds()

        # ----------------------------------------------------
        # Y
        # ----------------------------------------------------

        y_max = (
            self.get_base_y_max()
            * self.y_max_factor
        )

        y_range = (
            y_max
            - self.y_min
        )

        if y_range <= 0:
            return

        value_delta = (
            dy
            / graph_height
            * y_range
        )

        self.y_min += (
            value_delta
        )

        if self.y_min < 0:

            self.y_min = 0


    # ========================================================
    # EVENTS
    # ========================================================

    def handle_event(
        self,
        event
    ):

        # ----------------------------------------------------
        # Window close
        # ----------------------------------------------------

        if event.type == pygame.QUIT:

            return False

        # ----------------------------------------------------
        # Keyboard
        # ----------------------------------------------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                return False

            elif event.key == pygame.K_l:

                self.show_legend = (
                    not self.show_legend
                )

            elif event.key == pygame.K_r:

                self.reset_view()

            elif event.key == pygame.K_s:

                self.save_screenshot()

        # ----------------------------------------------------
        # Mouse wheel
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEWHEEL:

            mouse_x, mouse_y = (
                pygame.mouse.get_pos()
            )

            modifiers = (
                pygame.key.get_mods()
            )

            # Shift = Y zoom
            if modifiers & pygame.KMOD_SHIFT:

                if event.y > 0:

                    self.zoom_y(
                        mouse_y,
                        1.25
                    )

                elif event.y < 0:

                    self.zoom_y(
                        mouse_y,
                        0.8
                    )

            # Normal wheel = X zoom
            else:

                if event.y > 0:

                    self.zoom_x(
                        mouse_x,
                        1.25
                    )

                elif event.y < 0:

                    self.zoom_x(
                        mouse_x,
                        0.8
                    )

        # ----------------------------------------------------
        # Mouse down
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            # Middle mouse
            if event.button == 2:

                self.dragging = True

                self.last_mouse_pos = (
                    event.pos
                )

            # Left mouse
            elif event.button == 1:

                if (
                    GRAPH_LEFT
                    <= event.pos[0]
                    <= GRAPH_RIGHT
                    and
                    GRAPH_TOP
                    <= event.pos[1]
                    <= GRAPH_BOTTOM
                ):

                    self.dragging = True

                    self.last_mouse_pos = (
                        event.pos
                    )

        # ----------------------------------------------------
        # Mouse up
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button in (1, 2):

                self.dragging = False

                self.last_mouse_pos = None

        # ----------------------------------------------------
        # Mouse movement
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEMOTION:

            if self.dragging:

                if self.last_mouse_pos is None:

                    self.last_mouse_pos = (
                        event.pos
                    )

                dx = (
                    event.pos[0]
                    - self.last_mouse_pos[0]
                )

                dy = (
                    event.pos[1]
                    - self.last_mouse_pos[1]
                )

                self.pan(
                    dx,
                    dy
                )

                self.last_mouse_pos = (
                    event.pos
                )

        return True


    # ========================================================
    # DRAW EVERYTHING
    # ========================================================

    def draw(self):

        self.screen.fill(
            BACKGROUND_COLOR
        )

        # Grid first
        self.draw_grid()

        # ----------------------------------------------------
        # Draw simulations
        # ----------------------------------------------------

        visible = (
            self.get_visible_simulations()
        )

        # Group simulations by language
        language_groups = {}

        for simulation in visible:

            language_groups.setdefault(
                simulation.language,
                []
            ).append(simulation)

        for language, simulations in (
            language_groups.items()
        ):

            base_color = (
                LANGUAGE_BASE_COLORS.get(
                    language,
                    (200, 200, 200)
                )
            )

            total = len(simulations)

            for index, simulation in enumerate(
                simulations
            ):

                color = shade_color(
                    base_color,
                    index,
                    total
                )

                self.draw_simulation(
                    simulation,
                    color
                )

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.draw_legend()

        self.draw_header()

        self.draw_controls()

        pygame.display.flip()


    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self):

        running = True

        while running:

            for event in pygame.event.get():

                running = (
                    self.handle_event(
                        event
                    )
                )

                if not running:
                    break

            self.draw()

            self.clock.tick(
                FPS
            )

        pygame.quit()


# ============================================================
# CSV LOADER
# ============================================================

def load_csv(filename):

    simulations = []

    print(
        f"Loading CSV: {filename}"
    )

    with open(
        filename,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.reader(
            file
        )

        for row_number, row in enumerate(
            reader,
            start=1
        ):

            if not row:
                continue

            # Expected:
            #
            # 0 = language
            # 1 = logic
            # 2 = attribute
            # 3 = world size
            # 4 = simulation index
            # 5 = timing list

            if len(row) < 6:

                print(
                    f"Skipping row {row_number}: "
                    f"not enough columns"
                )

                continue

            language = (
                row[0].strip()
            )

            logic = (
                row[1].strip()
            )

            attribute = (
                row[2].strip()
            )

            world_size_text = (
                row[3].strip()
            )

            simulation_index = (
                row[4].strip()
            )

            raw_times = row[5]

            # ------------------------------------------------
            # World size
            # ------------------------------------------------

            try:

                world_size = int(
                    world_size_text
                )

            except ValueError:

                print(
                    f"Skipping row {row_number}: "
                    f"invalid world size "
                    f"{world_size_text!r}"
                )

                continue

            # ------------------------------------------------
            # Parse timings
            # ------------------------------------------------

            times = parse_timing_list(
                raw_times
            )

            if not times:

                print(
                    f"Skipping row {row_number}: "
                    f"no timing data"
                )

                continue

            # ------------------------------------------------
            # Create simulation
            # ------------------------------------------------

            simulation = Simulation(
                language=language,
                logic=logic,
                attribute=attribute,
                world_size=world_size,
                simulation_index=simulation_index,
                times=times
            )

            simulations.append(
                simulation
            )

            if row_number % 10 == 0:

                print(
                    f"Loaded "
                    f"{row_number} CSV rows..."
                )

    print()
    print(
        f"Loaded {len(simulations)} simulations."
    )

    return simulations


# ============================================================
# MAIN
# ============================================================

def main():

    csv_path = Path(
        CSV_FILE
    )

    if not csv_path.exists():

        print(
            "ERROR: CSV file not found:"
        )

        print(
            csv_path.resolve()
        )

        print()

        print(
            f"Put the CSV next to this Python file "
            f"and name it {CSV_FILE!r}, "
            f"or change CSV_FILE at the top."
        )

        input(
            "\nPress Enter to exit..."
        )

        return

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    simulations = load_csv(
        csv_path
    )

    if not simulations:

        print(
            "ERROR: No valid simulations were found."
        )

        input(
            "\nPress Enter to exit..."
        )

        return

    # --------------------------------------------------------
    # Start engine
    # --------------------------------------------------------

    engine = GraphEngine(
        simulations
    )

    engine.run()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()