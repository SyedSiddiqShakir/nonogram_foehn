# Shakir Nonogram Notation (SNN)

**Description:** A compact, human readable and scalable string notation for Nonogram puzzles, intend to store both the puzzle logic referred to as 'clues' and game progress referred to as state in a single string.

---

## 1. Overview
**SSN** is inspired by the existing FEN notation in Chess. It allows developers and players to share puzzles and mid-game states via a single string. It prioritizes human-readability and provides shorthand multipliers to handle large-scale puzzles (up to 100x100 and beyond) without the need for further encoding.

- **Making it LLM friendly:** One of the main motivation to generate this string instead of a traditional matrix inside a JSON file was to employ an LLM with certain specific input and output token representation in solving nonograms which require a rough string of this sort (lots of assumptions here).

---

## 2. Structure
An SSN string consists of four segments separated by specific delimiters:

`[Dimensions] : [Column Clues] : [Row Clues] ; [State Data]`

| Segment | Delimiter | Purpose |
| :--- | :--- | :--- |
| **Dimensions** | `:` | Defines the width and height of the grid. |
| **Column Clues** | `:` | Defines the logic for every column from left to right. |
| **Row Clues** | `;` | Defines the logic for every row from top to bottom. |
| **State Data** | *(End)* | Captures the current status of every cell and starts row-wise. |

---

## 3. Segment Breakdown

### A. Dimensions
**Format:** `[Width]x[Height]`  
**Example:** `15x15`, `100x100`

### B. Clue Segments
Clues are defined as sequences of numbers representing filled blocks.
- **Individual Numbers:** Separated by dotss `.` (e.g., `1.2.1`) These belong to the same column/row.
- **Line Breaks:** Each individual columns or rows are separated by commas `.` (e.g., `1.1,3,1.1`). Here as an example are 3 columns with the middle column with 1 clue only and the rest with 2 each.
- **Repetition Shorthand (The Multiplier):** To save space in large puzzles with repeating patterns, use `(clue)*count`.
  - *Example:* `(5)*10` is equivalent to `5,5,5,5,5,5,5,5,5,5`.
  - *Example:* `(1.2)*3` is equivalent to `1.2,1.2,1.2`.

### C. State Data
The state data captures the current board progress using **Row-wise Linearization** (left-to-right, then top-to-bottom).
- **Cell Status Codes:**
  - `f` : Filled (Marked)
  - `x` : Crossed (Confirmed Empty)
  - `u` : Unknown (Blank)
- **Line Delimiter:** Rows are separated by a slash `/`.
- **Run-Length Encoding (RLE):** Numbers precede the status codes to represent consecutive cells of the same type.
  - *Example:* `5f3x2u` means 5 Filled, 3 Crossed, 2 Unknown.
- **Row Multiplier:** If multiple consecutive rows are identical (e.g., 10 empty rows), use `count(row_state)`.
  - *Example:* `10(15u)` means 10 rows consisting of 15 unknown cells each.

---

## 4. Implementation Example:
A 14x13 puzzle with a fully solved Apple.

![Apple Nonogram](./images/apple.png)

**Full SN String:**
`14x13:0,4,7,9,10,10,8,2.8,2.10,2.10,9,7,4,0:2,3,1,3.3,10,12,12,12,12,10,10,9,2.2;8x2f4x/7x3f4x/7x1f6x/3x3f2x3f3x/2x10f2x/4(1x12f1x)/2(2x10f2x)/3x8f3x/4x2f2x2f4x`

### Breakdown:
1. **Header:** `14x13` (14 Wide, 13 High).
2. **Column Clues:** `0,4,7...` (Individual column logic separated by dots).
3. **Row Clues:** `2,3,1...` (Individual row logic separated by dots).
4. **Semicolon Divider:** `;` (Marks end of static puzzle logic, start of dynamic progress).
5. **State Data:** - `8x2f4x/7x...` : The first row contains 8 crosses in a row, then 2 filled and at last 4 unknowns.

---

## 5. Misc:
1. **Efficiency:** A 100x100 puzzle with 10,000 cells can be represented in as few as 20–30 characters if the board is empty. And not so much with board filled. This keeps it very well under inuitive idea that a LLM with the input of this sort can handle approximately 100 sized token length easily.
2. **Human Readable:** The primary factor in materializing to this style of notation was the ability of a human to read an SNN string and manually verify a clue or a cell status, but still be compact enough to make computationally efficient.
3. **Optimized for Parsing:** Row-wise linearization aligns with standard 2D array iteration in most programming languages.