import json
import svgwrite
import os

def render_heatmap():
    json_path = 'data/contributions.json'
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found! Run fetch_contributions.py first.")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    dwg = svgwrite.Drawing('contrib-heatmap.svg', size=('100%', '180px'))
    
    # Outer Terminal Frame
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=8, ry=8, fill='#0d1117', stroke='#30363d', stroke_width=1))
    
    # Chrome controls
    dwg.add(dwg.circle(center=(20, 20), r=5, fill='#ff5f56'))
    dwg.add(dwg.circle(center=(35, 20), r=5, fill='#ffbd2e'))
    dwg.add(dwg.circle(center=(50, 20), r=5, fill='#27c93f'))
    dwg.add(dwg.text("$ ./contributions.sh", insert=(70, 24), fill='#8b949e', font_family='monospace', font_size='12px'))

    # Dark Mode Heatmap Palette
    colors = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
    contributions = data.get('contributions', [])[-364:]  # Last 52 weeks

    x_start = 30
    y_start = 55
    box_size = 10
    gap = 3

    col = 0
    row = 0
    total_commits = 0

    for day in contributions:
        count = day.get('count', 0)
        total_commits += count
        c_idx = 0 if count == 0 else (1 if count <= 2 else (2 if count <= 5 else (3 if count <= 8 else 4)))
        
        x = x_start + (col * (box_size + gap))
        y = y_start + (row * (box_size + gap))

        dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), rx=2, ry=2, fill=colors[c_idx]))

        row += 1
        if row >= 7:
            row = 0
            col += 1

    # Stats Footer
    footer_text = f"Total Contributions: {total_commits} in the last year"
    dwg.add(dwg.text(footer_text, insert=(30, 162), fill='#8b949e', font_family='monospace', font_size='11px'))

    dwg.save()
    print("contrib-heatmap.svg generated successfully.")

if __name__ == "__main__":
    render_heatmap()