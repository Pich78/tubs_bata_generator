import sys
import re

# Map from TUBS symbols to SVG shapes.
# The fill color will be added dynamically based on the drum.
# Stroke color is now white.
symbol_map = {
    '-': '',
    'A': '<circle cx="15" cy="15" r="10" stroke="white" stroke-width="2" fill="{fill_color}" />',
    'P': '<circle cx="15" cy="15" r="10" stroke="white" stroke-width="2" fill="{fill_color}" stroke-dasharray="4" />',
    'S': '<polygon points="15,5 25,25 5,25" stroke="white" stroke-width="2" fill="{fill_color}" />',
    'I': '<circle cx="15" cy="15" r="10" stroke="white" stroke-width="2" fill="{fill_color}" />' +
         '<polygon points="15,7.3 21,20 9,20" stroke="white" stroke-width="1.5" fill="{fill_color}" />'
}

# Define colors for each drum
drum_colors = {
    'Okonkolo': 'rgb(200, 0, 0)',   # Red
    'Itotele': 'rgb(255, 200, 0)',  # Yellow
    'Iya': 'rgb(0, 0, 150)'        # Blue
}

def parse_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    toque_name = ""
    time_signature = ""
    parts = {'Okonkolo': '', 'Itotele': '', 'Iya': ''}
    current = None

    for line in lines:
        line = line.strip()
        if line.startswith("Toque:"):
            toque_name = line.replace("Toque:", "").strip()
        elif line.startswith("Time:"):
            time_signature = line.replace("Time:", "").strip()
        elif line in parts:
            current = line
        elif current:
            parts[current] += line
            
    return toque_name, time_signature, parts

def generate_html(toque_name, time_signature, parts):
    # beats_per_bar will be 4 for 4/4 and 6 for 6/8
    beats_per_bar = int(time_signature.split('/')[0]) # Get the numerator of time signature
    
    # Assuming each TUBS symbol is a sixteenth note for consistency
    # This means 4 symbols per quarter in 4/4.
    # In 6/8, if it's counting "every 6", then it's 6 symbols per "beat" unit for the top row.
    # The bottom row (sedicesimi) should count up to that "beat" unit.
    
    # Determine the "grouping unit" for the top count row
    # For 4/4, it's 4 sixteenths per quarter
    # For 6/8, it's 6 symbols per new "top count" number
    top_count_unit = 4 
    if time_signature == '6/8':
        top_count_unit = 6 # Count the top line every 6 symbols (sedicesimi)
        
    max_len = max(len(seq) for seq in parts.values())

    html = ['<html>', '<head>', '<style>']
    html.append("""
        body {
            background-color: rgb(100, 100, 100);
            color: white;
            font-family: sans-serif;
        }
        table { border-collapse: collapse; margin-top: 20px;}
        td {
            width: 30px;
            height: 30px;
            text-align: center;
            border: 1px solid #aaa;
            background-color: rgb(100, 100, 100);
            vertical-align: middle;
        }
        .bar-line { border-right: 3px solid white !important; }
        svg { width: 30px; height: 30px; }
        .legend-item { display: flex; align-items: center; margin-bottom: 5px; }
        .legend-symbol { margin-right: 10px; }
        h2, h3 { color: white; }
        .count-row td {
            font-size: 0.8em;
            font-weight: bold;
            color: #eee;
            border: none;
            background-color: transparent;
        }
        .count-row.quarter td {
            border-bottom: 1px solid #777;
        }
        .count-label {
            width: 80px;
            text-align: left;
            padding-left: 5px;
            font-weight: bold;
        }
    """)
    html.append('</style></head><body>')
    html.append(f'<h2>{toque_name} in {time_signature}</h2>')
    html.append('<table>')

    # Add Top count row (Quarti for 4/4, "gruppi di 6" for 6/8)
    html.append('<tr class="count-row quarter">')
    html.append(f'<td class="count-label">{"Quarti" if time_signature == "4/4" else "Gruppi"}</td>')
    for i in range(max_len):
        current_count = (i // top_count_unit) + 1
        display_count = ""
        if i % top_count_unit == 0: # Only print the number on the first symbol of each group
            display_count = str(current_count)
        
        bar_class = 'bar-line' if (i + 1) % beats_per_bar == 0 else ''
        html.append(f'<td class="{bar_class}">{display_count}</td>')
    html.append('</tr>')

    # Add Bottom count row (Sedicesimi for 4/4, "Suddivisioni" for 6/8)
    html.append('<tr class="count-row sixteenth">')
    html.append(f'<td class="count-label">{"Sedicesimi" if time_signature == "4/4" else "Suddivisioni"}</td>')
    for i in range(max_len):
        bottom_beat = (i % top_count_unit) + 1 # Count 1 to `top_count_unit` for each group
        bar_class = 'bar-line' if (i + 1) % beats_per_bar == 0 else ''
        html.append(f'<td class="{bar_class}">{bottom_beat}</td>')
    html.append('</tr>')


    for drum in ['Okonkolo', 'Itotele', 'Iya']:
        html.append(f'<tr><td><b>{drum}</b></td>')
        sequence = parts[drum].ljust(max_len, '-')
        current_fill_color = drum_colors[drum]
        for i, symbol in enumerate(sequence):
            bar_class = 'bar-line' if (i + 1) % beats_per_bar == 0 else ''
            svg = symbol_map.get(symbol, '').format(fill_color=current_fill_color)
            cell = f'<td class="{bar_class}"><svg>{svg}</svg></td>'
            html.append(cell)
        html.append('</tr>')

    html.append('</table>')

    # Add Legend
    html.append('<h3>Legenda dei simboli:</h3>')
    html.append('<div class="legend-container">')

    legend_fill_color = drum_colors['Okonkolo']

    html.append('<div class="legend-item">')
    html.append(f'<div class="legend-symbol"><svg>{symbol_map["A"].format(fill_color=legend_fill_color)}</svg></div>')
    html.append('<span>A: Suono aperto</span>')
    html.append('</div>')

    html.append('<div class="legend-item">')
    html.append(f'<div class="legend-symbol"><svg>{symbol_map["P"].format(fill_color=legend_fill_color)}</svg></div>')
    html.append('<span>P: Suono pressionato</span>')
    html.append('</div>')

    html.append('<div class="legend-item">')
    html.append(f'<div class="legend-symbol"><svg>{symbol_map["S"].format(fill_color=legend_fill_color)}</svg></div>')
    html.append('<span>S: Slap sulla culatta</span>')
    html.append('</div>')

    html.append('<div class="legend-item">')
    html.append(f'<div class="legend-symbol"><svg>{symbol_map["I"].format(fill_color=legend_fill_color)}</svg></div>')
    html.append('<span>I: Insieme - mordito</span>')
    html.append('</div>')

    html.append('</div>') # end legend-container

    html.append('</body></html>')
    return '\n'.join(html)

def main():
    if len(sys.argv) != 3:
        print("Usage: python tubs_gen.py input.txt output.html")
        return

    toque_name, time_sig, parts = parse_input(sys.argv[1])
    html = generate_html(toque_name, time_sig, parts)
    with open(sys.argv[2], 'w') as f:
        f.write(html)

if __name__ == '__main__':
    main()