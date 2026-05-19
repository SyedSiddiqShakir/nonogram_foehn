import re

class SNNParser:
    def __init__(self):
        """map SNN characters to matrix integers for easier processing
        """
        # 1 = Filled, 
        #-1 = Crossed/Empty, 
        # 0 = Unknown
        self.state_map = {'f': 1, 'x': -1, 'u': 0}

    def parse(self, snn_string):
        """Main parsing function. Converts SNN string to a dictionary containing all game data.

        Args:
            snn_string (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        #split into Logic (Clues) and State (Progress)
        try:
            logic_str, state_str = snn_string.split(';')
            dims_str, col_clues_str, row_clues_str = logic_str.split(':')
        except ValueError:
            raise ValueError("Invalid SNN format. Expected [Dims]:[Cols]:[Rows];[State]")

        #parse Dimensions
        width, height = map(int, dims_str.split('x'))

        #parse Clues
        col_clues = self._parse_clues(col_clues_str)
        row_clues = self._parse_clues(row_clues_str)

        #parse State into a 2D Matrix
        matrix = self._parse_state(state_str, width, height)

        return {
            'width': width,
            'height': height,
            'col_clues': col_clues,
            'row_clues': row_clues,
            'matrix': matrix
        }

    def _parse_clues(self, clue_str):
        """Expands multipliers and parses clue segments._summary_

        Args:
            clue_str (_type_): _description_

        Returns:
            _type_: _description_
        """
        #regex to find (clue)*count
        def expand_clue_match(match):
            clue_sequence = match.group(1)
            count = int(match.group(2))
            return ','.join([clue_sequence] * count)

        #expand multipliers
        expanded_str = re.sub(r'\(([^)]+)\)\*(\d+)', expand_clue_match, clue_str)

        parsed_clues = []
        for line in expanded_str.split(','):
            if line == '0' or line == '': #handle empty rows/cols
                parsed_clues.append([])
            else:
                parsed_clues.append([int(x) for x in line.split('.')])
                
        return parsed_clues

    def _parse_state(self, state_str, width, height):
        """Expands row multipliers and decodes RLE into a 2D matrix.

        Args:
            state_str (_type_): _description_
            width (_type_): _description_
            height (_type_): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        #regex to find count(row_state) e.g., 10(14u)
        def expand_row_match(match):
            count = int(match.group(1))
            row_data = match.group(2)
            return '/'.join([row_data] * count)

        #expand row multipliers
        expanded_state = re.sub(r'(\d+)\(([^)]+)\)', expand_row_match, state_str)

        matrix = []
        for row_str in expanded_state.split('/'):
            if not row_str: continue
            
            #find all RLE pairs 
            tokens = re.findall(r'(\d+)([fxu])', row_str)
            
            row_data = []
            for count_str, char in tokens:
                count = int(count_str)
                row_data.extend([self.state_map[char]] * count)
            
            #validation
            if len(row_data) != width:
                raise ValueError(f"Row logic error: parsed {len(row_data)} cells, expected {width}.")
            
            matrix.append(row_data)
            
        #validation
        if len(matrix) != height:
            raise ValueError(f"Height logic error: parsed {len(matrix)} rows, expected {height}.")
            
        return matrix

    def display(self, parsed_data):
        """A simple terminal visualizer for debugging.

        Args:
            parsed_data (_type_): _description_
        """
        print(f"\n--- SNN Parsed: {parsed_data['width']}x{parsed_data['height']} ---")
        
        #we will use ASCII blocks to visualize the matrix
        # █ = Filled (1), · = Unknown (0), X = Crossed (-1)
        char_map = {1: '██', -1: 'XX', 0: '··'}
        
        for row in parsed_data['matrix']:
            print(''.join(char_map[cell] for cell in row))
        print("------------------------\n")


#DISCLAIMER: This is a basic implementation of an SNN parser. It may not cover all edge cases or optimizations, but it should work for standard SNN strings. The display function is a simple terminal visualizer and can be enhanced with better formatting or color coding if desired.
if __name__ == "__main__":
    parser = SNNParser()
    
    #Apple SNN string
    apple_snn = "14x13:0,4,7,9,10,10,8,2.8,2.10,2.10,9,7,4,0:2,3,1,3.3,10,12,12,12,12,10,10,9,2.2;8x2f4x/7x3f4x/7x1f6x/3x3f2x3f3x/2x10f2x/4(1x12f1x)/2(2x10f2x)/3x8f3x/4x2f2x2f4x"
    
    try:
        data = parser.parse(apple_snn)
        parser.display(data)
        
        #to prove the clues parsed correctly:
        print("First 3 Column Clues:", data['col_clues'][:3])
        print("First 3 Row Clues:", data['row_clues'][:3])
        
    except Exception as e:
        print(f"Error parsing SNN: {e}")