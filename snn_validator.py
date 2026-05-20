import re

class SNNValidator:
    """A class to validate SNN strings against a set of rules to ensure they are well-formed and logically consistent. The validation process includes checks for structure, dimension consistency, clue counts, valid characters in the state, and mathematical consistency of the RLE state data.
    """
    def __init__(self):
        self.valid_states = {'f', 'x', 'u'}

    def validate(self, snn_string):
        """ Validates the SNN string against multiple levels of checks, returning a boolean and a list of error messages.

        Args:
            snn_string (_type_): The SNN string to validate.

        Returns:
            _type_: A tuple of (is_valid: bool, errors: list of strings).
        """
        errors = []

        # STRUCTURE CHECK: Must have exactly one ';' separating logic and state, and logic must have exactly two ':' separators
        try:
            logic_str, state_str = snn_string.split(';')
            dims_str, col_clues_str, row_clues_str = logic_str.split(':')
        except ValueError:
            return False, ["Structure Error: SNN must strictly follow '[Dims]:[Cols]:[Rows];[State]'."]
    
        # Dimension Validation 
        match = re.match(r'^(\d+)x(\d+)$', dims_str)
        if not match:
            errors.append(f"Dimension Error: '{dims_str}' is invalid. Expected format 'WxH' (e.g., '10x10').")
            return False, errors # Cannot proceed without valid dimensions
            
        width = int(match.group(1))
        height = int(match.group(2))

        # Column Clue Validation 
        col_count = self._count_expanded_lines(col_clues_str, delimiter=',')
        if col_count != width:
            errors.append(f"Column Logic Error: Grid width is {width}, but found {col_count} column clues.")

        # Clue Validation for Rows
        row_count = self._count_expanded_lines(row_clues_str, delimiter=',')
        if row_count != height:
            errors.append(f"Row Logic Error: Grid height is {height}, but found {row_count} row clues.")

        # State Validation
        expanded_state = self._expand_row_multipliers(state_str)
        state_rows = expanded_state.split('/')
        
        if len(state_rows) != height:
            errors.append(f"State Rows Error: Expected {height} rows of state data, found {len(state_rows)}.")
        
        for i, row_string in enumerate(state_rows):
            if not row_string:
                continue # Skip completely empty strings if any crept in
            
            # Check for invalid characters
            clean_row = re.sub(r'\d+', '', row_string) # remove numbers
            invalid_chars = set(clean_row) - self.valid_states
            if invalid_chars:
                errors.append(f"State Char Error (Row {i+1}): Found invalid characters {invalid_chars}. Only 'f', 'x', 'u' allowed.")
            
            # Check math (does RLE sum up to the width?)
            tokens = re.findall(r'(\d+)([fxu])', row_string)
            cell_count = sum(int(count) for count, char in tokens)
            
            if cell_count != width:
                errors.append(f"State Math Error (Row {i+1}): RLE sums to {cell_count} cells, but grid width is {width}.")

        is_valid = len(errors) == 0
        return is_valid, errors

    # --- Helper Methods ---
    
    def _count_expanded_lines(self, clue_str, delimiter):
        """ Counts the number of lines in a clue string after expanding any multipliers. For example, '2(1,2)' would expand to '1,2,1,2' which counts as 4 lines.

        Args:
            clue_str (_type_): The clue string to count lines from, which may contain multipliers like '2(1,2)'.
            delimiter (_type_): The delimiter used to separate clues (e.g., ',' for columns, '.' for rows).
        """
        def expand_match(match):
            seq = match.group(1)
            count = int(match.group(2))
            return delimiter.join([seq] * count)
            
        expanded = re.sub(r'\(([^)]+)\)\*(\d+)', expand_match, clue_str)
        # If the string is empty or '0', it counts as 1 line of empty clues, otherwise split
        if not expanded: return 0
        return len(expanded.split(delimiter))

    def _expand_row_multipliers(self, state_str):
        """ Expands row multipliers in the state string. For example, '2(5u)' would expand to '5u/5u', which represents two rows of '5u'.

        Args:
            state_str (_type_): The state string to expand, which may contain multipliers like '2(5u)'.
        """
        def expand_match(match):
            count = int(match.group(1))
            row_data = match.group(2)
            return '/'.join([row_data] * count)
            
        return re.sub(r'(\d+)\(([^)]+)\)', expand_match, state_str)

# Test cases to validate the SNNValidator
if __name__ == "__main__":
    validator = SNNValidator()
    
    # Apple SNN (valid)
    print("Testing Valid Apple")
    valid_snn = "14x13:0,4,7,9,10,10,8,2.8,2.10,2.10,9,7,4,0:2,3,1,3.3,10,12,12,12,12,10,10,9,2.2;8x2f4x/7x3f4x/7x1f6x/3x3f2x3f3x/2x10f2x/4(1x12f1x)/2(2x10f2x)/3x8f3x/4x2f2x2f4x"
    is_valid, errors = validator.validate(valid_snn)
    print(f"Is Valid? {is_valid}")
    if not is_valid:
        for err in errors: print(f" - {err}")
        
    print("\nTesting Broken Strings")
    
    # broken state with too many cells in a row
    broken_state = "5x5:1.1,1,1,1,1:1,1,1,1,1;5f/3f3x/5u/5u/5u" # Row 2 has 6 cells!
    is_valid, errors = validator.validate(broken_state)
    print("Broken State Data Test:")
    for err in errors: print(f" - {err}")
    
    # missing column clues
    broken_col = "5x5:1,1,1,1:1,1,1,1,1;5(5u)" # Only 4 col clues for a 5x5
    is_valid, errors = validator.validate(broken_col)
    print("\nBroken Column Logic Test:")
    for err in errors: print(f" - {err}")
    
    # invalid character in state
    broken_char = "5x5:(1)*5:(1)*5;5u/5u/2u1y2u/5u/5u" # 'y' is not a valid character
    is_valid, errors = validator.validate(broken_char)
    print("\nBroken Character Test:")
    for err in errors: print(f" - {err}")