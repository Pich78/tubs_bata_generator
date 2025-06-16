import sys
import re

# Mappa dei simboli TUBS ai simboli SVG
symbol_map = {
    '-': '',
    'A': '<circle cx="15" cy="15" r="10" stroke="black" stroke-width="2" fill="white" />',
    'P': '<circle cx="15" cy="15" r="10" stroke="black" stroke-width="2" fill="white" stroke-dasharray="4" />',
    'S': '<polygon points="15,5 25,25 5,25" stroke="black" stroke-width="2" fill="white" />',
}

def parse_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    time_signature = lines[0].strip()
    parts = {'Okonkolo': '', 'Itotele': '', 'Iya': ''}
    current = None
    for line in lines[1:]:
        line = line.strip()
        if line in parts:
            current = line
        elif current:
            parts[current] += line
    return time_signature, parts

def generate_html(time_signature, parts):
    beats_per_bar = 4 if time_signature == '4/4' else 6 if time_signature == '6/8' else 4
    max_len = max(len(seq) for seq in parts.values())

    html = ['<html>', '<head>', '<style>']
    html.append("""
        table { border-collapse: collapse; }
        td { width: 30px; height: 30px; text-align: center; border: 1px solid #aaa; }
        .bar-line { border-right: 3px solid black !important; }
        svg { width: 30px; height: 30px; }
    """)
    html.append('</style></head><body>')
    html.append(f'<h2>Spartito Batà in {time_signature}</h2>')
    html.append('<table>')

    for drum in ['Okonkolo', 'Itotele', 'Iya']:
        html.append(f'<tr><td><b>{drum}</b></td>')
        sequence = parts[drum].ljust(max_len, '-')
        for i, symbol in enumerate(sequence):
            bar_class = 'bar-line' if (i + 1) % beats_per_bar == 0 else ''
            svg = symbol_map.get(symbol, '')
            cell = f'<td class="{bar_class}"><svg>{svg}</svg></td>'
            html.append(cell)
        html.append('</tr>')

    html.append('</table></body></html>')
    return '\n'.join(html)

def main():
    if len(sys.argv) != 3:
        print("Uso: python generate_tubs_html.py input.txt output.html")
        return
    
    time_sig, parts = parse_input(sys.argv[1])
    html = generate_html(time_sig, parts)
    with open(sys.argv[2], 'w') as f:
        f.write(html)

if __name__ == '__main__':
    main()
