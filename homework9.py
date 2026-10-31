"""
Homework 9 - Supplemental Chapter 9
Python solution covering problems 1-5.

Run with: python homework9.py

The bouncing-ball demonstration uses tkinter (included with standard Python).
The cipher programs run from the text menu.
"""

import random
import tkinter as tk


# ---------------------------------------------------------------------------
# Problem 1: Animate three bouncing balls in one window.
# Ball data is stored in a list of dictionaries. Each dictionary keeps the
# graphics object, position, velocity, and radius for one ball.
# ---------------------------------------------------------------------------

def show_bouncing_balls():
    root = tk.Tk()
    root.title("Homework 9 - Three Bouncing Balls")
    width, height = 700, 450
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    colors = ["hot pink", "royal blue", "dark orange"]
    balls = []

    for i, color in enumerate(colors):
        radius = 18 + i * 4
        x = 100 + i * 150
        y = 100 + i * 65
        ball_id = canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline="black"
        )
        balls.append({
            "shape": ball_id,
            "x": x,
            "y": y,
            "dx": 3 + i,
            "dy": 2 + i,
            "radius": radius
        })

    def animate():
        for ball in balls:
            r = ball["radius"]
            ball["x"] += ball["dx"]
            ball["y"] += ball["dy"]

            if ball["x"] - r <= 0 or ball["x"] + r >= width:
                ball["dx"] *= -1
            if ball["y"] - r <= 0 or ball["y"] + r >= height:
                ball["dy"] *= -1

            canvas.coords(
                ball["shape"],
                ball["x"] - r, ball["y"] - r,
                ball["x"] + r, ball["y"] + r
            )

        root.after(16, animate)

    animate()
    root.mainloop()


# ---------------------------------------------------------------------------
# Problem 2: Polybius checkerboard stored as a list of lists.
# Tuples represent both the grid size and a letter's (row, column) location.
# I and J share one square.
# ---------------------------------------------------------------------------

POLYBIUS_GRID = [
    ["A", "B", "C", "D", "E"],
    ["F", "G", "H", "I/J", "K"],
    ["L", "M", "N", "O", "P"],
    ["Q", "R", "S", "T", "U"],
    ["V", "W", "X", "Y", "Z"]
]
POLYBIUS_SIZE = (5, 5)


def polybius_encode(message):
    result = []
    for character in message.upper():
        if character == "J":
            character = "I"
        if character.isalpha():
            for row in range(POLYBIUS_SIZE[0]):
                for column in range(POLYBIUS_SIZE[1]):
                    cell = POLYBIUS_GRID[row][column]
                    if character in cell:
                        result.append(f"{row + 1}{column + 1}")
                        break
                else:
                    continue
                break
        elif character.isspace():
            result.append("/")
    return " ".join(result)


def polybius_decode(code):
    decoded = []
    for pair in code.split():
        if pair == "/":
            decoded.append(" ")
        elif len(pair) == 2 and pair.isdigit():
            row, column = int(pair[0]) - 1, int(pair[1]) - 1
            if 0 <= row < POLYBIUS_SIZE[0] and 0 <= column < POLYBIUS_SIZE[1]:
                letter = POLYBIUS_GRID[row][column]
                decoded.append("I" if letter == "I/J" else letter)
    return "".join(decoded)


# ---------------------------------------------------------------------------
# Shared helpers for Problems 3-5.
# ---------------------------------------------------------------------------

def make_grid(message, rows, columns, padding="X"):
    """Put a message into a list-of-lists grid and pad unused cells."""
    if rows <= 0 or columns <= 0:
        raise ValueError("Rows and columns must be positive.")
    if len(message) > rows * columns:
        raise ValueError("The message is too long for this grid.")

    cleaned = "".join(ch for ch in message.upper() if ch.isalnum())
    if len(cleaned) > rows * columns:
        raise ValueError("The message is too long for this grid.")

    cleaned += padding * (rows * columns - len(cleaned))
    return [
        list(cleaned[row * columns:(row + 1) * columns])
        for row in range(rows)
    ]


def print_grid(grid):
    for row in grid:
        print(" ".join(row))


def keyword_column_order(keyword):
    """Return column indexes in alphabetical keyword order.

    Sorting by (letter, original position) handles repeated keyword letters.
    """
    keyword = keyword.upper()
    if not keyword or not keyword.isalpha():
        raise ValueError("Keyword must contain letters only.")
    return sorted(range(len(keyword)), key=lambda index: (keyword[index], index))


# ---------------------------------------------------------------------------
# Problem 3: Key Word cipher.
# The keyword determines the order in which columns are read.
# ---------------------------------------------------------------------------

def keyword_encrypt(message, keyword, rows=None, columns=None):
    keyword = keyword.upper()
    if columns is None:
        columns = len(keyword)
    if columns != len(keyword):
        raise ValueError("The grid column count must equal the keyword length.")
    cleaned = "".join(ch for ch in message.upper() if ch.isalnum())
    if rows is None:
        rows = (len(cleaned) + columns - 1) // columns
    grid = make_grid(cleaned, rows, columns)
    order = keyword_column_order(keyword)

    ciphertext = []
    for column in order:
        for row in range(rows):
            ciphertext.append(grid[row][column])
    return " ".join(
        "".join(ciphertext[i:i + 5])
        for i in range(0, len(ciphertext), 5)
    )


def keyword_decrypt(ciphertext, keyword, rows, columns):
    keyword = keyword.upper()
    if columns != len(keyword):
        raise ValueError("The grid column count must equal the keyword length.")
    letters = "".join(ch for ch in ciphertext.upper() if ch.isalnum())
    if len(letters) != rows * columns:
        raise ValueError("Ciphertext length must match the grid size.")

    order = keyword_column_order(keyword)
    grid = [[""] * columns for _ in range(rows)]
    position = 0

    # Fill columns in the same order they were read during encryption.
    for column in order:
        for row in range(rows):
            grid[row][column] = letters[position]
            position += 1

    return "".join("".join(row) for row in grid)


# ---------------------------------------------------------------------------
# Problem 4: Twisted Path cipher.
# A path is a list of (row, column) tuples. The path must visit every grid
# location exactly once. The examples below are fixed 5-by-6 paths.
# ---------------------------------------------------------------------------

def row_snake_path(rows, columns, start_at_bottom=False):
    path = []
    row_order = range(rows - 1, -1, -1) if start_at_bottom else range(rows)
    for row in row_order:
        if (rows - 1 - row if start_at_bottom else row) % 2 == 0:
            col_order = range(columns)
        else:
            col_order = range(columns - 1, -1, -1)
        for column in col_order:
            path.append((row, column))
    return path


def column_snake_path(rows, columns, start_at_bottom=False):
    path = []
    col_order = range(columns)
    for column in col_order:
        if column % 2 == 0:
            row_order = range(rows - 1, -1, -1) if start_at_bottom else range(rows)
        else:
            row_order = range(rows) if start_at_bottom else range(rows - 1, -1, -1)
        for row in row_order:
            path.append((row, column))
    return path


def spiral_path(rows, columns):
    path = []
    top, bottom = 0, rows - 1
    left, right = 0, columns - 1
    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            path.append((top, col))
        top += 1
        for row in range(top, bottom + 1):
            path.append((row, right))
        right -= 1
        if top <= bottom:
            for col in range(right, left - 1, -1):
                path.append((bottom, col))
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                path.append((row, left))
            left += 1
    return path


def validate_path(path, rows, columns):
    expected = {(r, c) for r in range(rows) for c in range(columns)}
    if len(path) != rows * columns or set(path) != expected:
        raise ValueError("Path must visit every grid location exactly once.")


def path_encrypt(message, rows=5, columns=6, path=None):
    cleaned = "".join(ch for ch in message.upper() if ch.isalnum())
    grid = make_grid(cleaned, rows, columns)
    if path is None:
        path = spiral_path(rows, columns)
    validate_path(path, rows, columns)
    ciphertext = "".join(grid[row][column] for row, column in path)
    return " ".join(ciphertext[i:i + 5] for i in range(0, len(ciphertext), 5))


def path_decrypt(ciphertext, rows=5, columns=6, path=None):
    letters = "".join(ch for ch in ciphertext.upper() if ch.isalnum())
    if len(letters) != rows * columns:
        raise ValueError("Ciphertext length must match the grid size.")
    if path is None:
        path = spiral_path(rows, columns)
    validate_path(path, rows, columns)

    grid = [[""] * columns for _ in range(rows)]
    for index, (row, column) in enumerate(path):
        grid[row][column] = letters[index]
    return "".join("".join(row) for row in grid)


# ---------------------------------------------------------------------------
# Problem 5: Combine a keyword, grid size, and agreed-upon path.
# First read the columns in keyword order; within each column, follow the
# agreed path's row order. The receiver reverses those exact steps.
# ---------------------------------------------------------------------------

def combined_encrypt(message, keyword, rows, columns, path):
    keyword = keyword.upper()
    if len(keyword) != columns:
        raise ValueError("Keyword length must equal the number of columns.")
    validate_path(path, rows, columns)
    grid = make_grid(message, rows, columns)

    # Build the agreed row order for each column from the path tuple list.
    row_order_by_column = {column: [] for column in range(columns)}
    for row, column in path:
        row_order_by_column[column].append(row)

    encrypted = []
    for column in keyword_column_order(keyword):
        for row in row_order_by_column[column]:
            encrypted.append(grid[row][column])

    return "".join(encrypted)


def combined_decrypt(ciphertext, keyword, rows, columns, path):
    keyword = keyword.upper()
    if len(keyword) != columns:
        raise ValueError("Keyword length must equal the number of columns.")
    validate_path(path, rows, columns)
    letters = "".join(ch for ch in ciphertext.upper() if ch.isalnum())
    if len(letters) != rows * columns:
        raise ValueError("Ciphertext length must match the grid size.")

    row_order_by_column = {column: [] for column in range(columns)}
    for row, column in path:
        row_order_by_column[column].append(row)

    grid = [[""] * columns for _ in range(rows)]
    position = 0
    for column in keyword_column_order(keyword):
        for row in row_order_by_column[column]:
            grid[row][column] = letters[position]
            position += 1

    return "".join("".join(row) for row in grid)


# ---------------------------------------------------------------------------
# Main menu and quick examples.
# ---------------------------------------------------------------------------

def main():
    while True:
        print("\nHOMEWORK 9")
        print("1. Show three bouncing balls")
        print("2. Polybius checkerboard")
        print("3. Key Word cipher")
        print("4. Twisted Path cipher")
        print("5. Combined keyword and path cipher")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                show_bouncing_balls()

            elif choice == "2":
                mode = input("Encode or decode (e/d): ").strip().lower()
                if mode == "e":
                    message = input("Enter a message: ")
                    print("Encoded:", polybius_encode(message))
                elif mode == "d":
                    code = input("Enter number pairs separated by spaces: ")
                    print("Decoded:", polybius_decode(code))
                else:
                    print("Please enter e or d.")

            elif choice == "3":
                mode = input("Encrypt or decrypt (e/d): ").strip().lower()
                keyword = input("Enter keyword: ").strip().upper()
                rows = int(input("Enter number of rows: "))
                columns = len(keyword)
                if mode == "e":
                    message = input("Enter message: ")
                    print("Ciphertext:", keyword_encrypt(message, keyword, rows, columns))
                elif mode == "d":
                    code = input("Enter ciphertext: ")
                    print("Plaintext:", keyword_decrypt(code, keyword, rows, columns))
                else:
                    print("Please enter e or d.")

            elif choice == "4":
                mode = input("Encrypt or decrypt (e/d): ").strip().lower()
                rows, columns = 5, 6
                path_choice = input("Choose path: 1=row snake, 2=column snake, 3=spiral: ")
                if path_choice == "1":
                    path = row_snake_path(rows, columns)
                elif path_choice == "2":
                    path = column_snake_path(rows, columns)
                else:
                    path = spiral_path(rows, columns)

                if mode == "e":
                    message = input("Enter message (maximum 30 letters): ")
                    print("Ciphertext:", path_encrypt(message, rows, columns, path))
                elif mode == "d":
                    code = input("Enter ciphertext: ")
                    print("Plaintext:", path_decrypt(code, rows, columns, path))
                else:
                    print("Please enter e or d.")

            elif choice == "5":
                mode = input("Encrypt or decrypt (e/d): ").strip().lower()
                keyword = input("Enter keyword (its length is the column count): ").strip().upper()
                rows = int(input("Enter number of rows: "))
                columns = len(keyword)
                path_choice = input("Choose path: 1=row snake, 2=column snake, 3=spiral: ")
                if path_choice == "1":
                    path = row_snake_path(rows, columns)
                elif path_choice == "2":
                    path = column_snake_path(rows, columns)
                else:
                    path = spiral_path(rows, columns)

                if mode == "e":
                    message = input("Enter message: ")
                    print("Ciphertext:", combined_encrypt(message, keyword, rows, columns, path))
                elif mode == "d":
                    code = input("Enter ciphertext: ")
                    print("Plaintext:", combined_decrypt(code, keyword, rows, columns, path))
                else:
                    print("Please enter e or d.")

            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Please choose a number from 1 to 6.")

        except ValueError as error:
            print("Error:", error)


if __name__ == "__main__":
    main()
