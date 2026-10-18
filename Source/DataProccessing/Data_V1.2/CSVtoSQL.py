
import csv
import ast
import sqlite3
import sys
from pathlib import Path

csv.field_size_limit(10**8)

folder = Path(__file__).parent

individual_csv = folder / "csv_periter.csv"
accumulated_csv = folder / "csv_accumulated.csv"
db_file = folder / "cgol.db"


def read_csv(path):
    rows = []

    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, start=1):
            if not row:
                continue

            if len(row) != 6:
                raise ValueError(
                    f"{path.name}, line {line_number}: "
                    f"expected 6 fields, got {len(row)}"
                )

            # The first five fields describe the simulation.
            # The sixth field contains the timing array.
            metadata = tuple(field.strip() for field in row[:5])

            times = ast.literal_eval(row[5].strip())

            if not isinstance(times, list) or not times:
                raise ValueError(
                    f"{path.name}, line {line_number}: "
                    "expected a nonempty timing list"
                )

            if any(
                isinstance(t, bool)
                or not isinstance(t, (int, float))
                or t < 0
                for t in times
            ):
                raise ValueError(
                    f"{path.name}, line {line_number}: "
                    "invalid timing value"
                )

            rows.append((metadata, [float(t) for t in times]))

    return rows


# Read both files before opening the database.
individual_rows = read_csv(individual_csv)
accumulated_rows = read_csv(accumulated_csv)

if len(individual_rows) != len(accumulated_rows):
    raise ValueError("The two CSV files have different row counts.")

# Confirm that corresponding rows describe the same variants.
for i, (individual, accumulated) in enumerate(
    zip(individual_rows, accumulated_rows), start=1
):
    if individual[0] != accumulated[0]:
        raise ValueError(
            f"Simulation row {i} has different metadata in the two CSVs."
        )

    if len(individual[1]) != len(accumulated[1]):
        raise ValueError(
            f"Simulation row {i} has different measurement counts."
        )


# Do not silently append a duplicate import.
if db_file.exists():
    raise FileExistsError(
        f"{db_file.name} already exists. "
        "Move or delete it before importing into a fresh database."
    )

connection = sqlite3.connect(db_file)
connection.execute("PRAGMA foreign_keys = ON")

try:
    cursor = connection.cursor()

    cursor.executescript("""
        CREATE TABLE simulations (
            simulation_id INTEGER PRIMARY KEY,
            framework TEXT NOT NULL,
            logical_optimization TEXT NOT NULL,
            logic_variant TEXT NOT NULL,
            world_size INTEGER NOT NULL CHECK (world_size > 0),
            seed INTEGER,
            generations_count INTEGER NOT NULL
                CHECK (generations_count > 0)
        );

        CREATE TABLE generation_measurements (
            measurement_id INTEGER PRIMARY KEY,
            simulation_id INTEGER NOT NULL,
            generation_number INTEGER NOT NULL,
            measurement_type TEXT NOT NULL
                CHECK (
                    measurement_type IN ('individual', 'accumulated')
                ),
            time_ms REAL NOT NULL CHECK (time_ms >= 0),

            FOREIGN KEY (simulation_id)
                REFERENCES simulations(simulation_id),

            UNIQUE (
                simulation_id,
                generation_number,
                measurement_type
            ),

            CHECK (generation_number > 0)
        );

        CREATE INDEX idx_measurements_simulation
        ON generation_measurements(simulation_id);
    """)

    total_measurements = 0

    for individual, accumulated in zip(
        individual_rows, accumulated_rows
    ):
        metadata, individual_times = individual
        _, accumulated_times = accumulated

        framework = metadata[0]
        logical_optimization = metadata[1]
        logic_variant = "naive" if metadata[2] == "None" else metadata[2]
        world_size = int(metadata[3])

        if len(individual_times) != len(accumulated_times):
            raise ValueError("Measurement counts do not match.")

        # Insert one simulation record.
        cursor.execute("""
            INSERT INTO simulations (
                framework,
                logical_optimization,
                logic_variant,
                world_size,
                seed,
                generations_count
            )
            VALUES (?, ?, ?, ?, NULL, ?)
        """, (
            framework,
            logical_optimization,
            logic_variant,
            world_size,
            len(individual_times)
        ))

        simulation_id = cursor.lastrowid

        # Insert individual and accumulated measurements.
        measurements = []

        for generation, time_ms in enumerate(
            individual_times, start=1
        ):
            measurements.append((
                simulation_id,
                generation,
                "individual",
                time_ms
            ))

        for generation, time_ms in enumerate(
            accumulated_times, start=1
        ):
            measurements.append((
                simulation_id,
                generation,
                "accumulated",
                time_ms
            ))

        cursor.executemany("""
            INSERT INTO generation_measurements (
                simulation_id,
                generation_number,
                measurement_type,
                time_ms
            )
            VALUES (?, ?, ?, ?)
        """, measurements)

        total_measurements += len(measurements)

    connection.commit()

    print("Import successful!")
    print(f"Simulations: {len(individual_rows)}")
    print(f"Measurement rows: {total_measurements}")
    print(f"Database: {db_file}")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
