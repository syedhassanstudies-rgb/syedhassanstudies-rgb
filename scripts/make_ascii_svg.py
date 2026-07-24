import cv2
import svgwrite
import os

def generate_ascii_svg():
    input_file = 'source-prepped.png'
    output_file = 'avi-ascii.svg'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run prep_photo.py first!")
        return

    img = cv2.imread(input_file, cv2.IMREAD_GRAYSCALE)
    cols = 64
    rows = 48
    img_small = cv2.resize(img, (cols, rows), interpolation=cv2.INTER_AREA)

    RAMP = " .:-=+*#%@"
    ramp_len = len(RAMP)

    dwg = svgwrite.Drawing(output_file, size=('100%', '340px'))
    
    # Terminal Window Container
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=8, ry=8, fill='#0d1117', stroke='#30363d', stroke_width=1))
    
    # Traffic Lights & Title Bar
    dwg.add(dwg.circle(center=(20, 20), r=5, fill='#ff5f56'))
    dwg.add(dwg.circle(center=(35, 20), r=5, fill='#ffbd2e'))
    dwg.add(dwg.circle(center=(50, 20), r=5, fill='#27c93f'))
    dwg.add(dwg.text("$ ./ascii-portrait.sh", insert=(70, 24), fill='#8b949e', font_family='monospace', font_size='12px'))

    # CSS Typing Animation Styles
    style_content = """
    .ascii-line {
        font-family: 'Courier New', Courier, monospace;
        font-size: 5.5px;
        fill: #3fb950;
        white-space: pre;
    }
    @keyframes wipe {
        0% { clip-path: inset(0 100% 0 0); }
        100% { clip-path: inset(0 0 0 0); }
    }
    .animated-wipe {
        animation: wipe 2.5s ease-out forwards;
    }
    """
    dwg.defs.add(dwg.style(style_content))

    group = dwg.g(class_='animated-wipe')
    y_start = 45
    line_height = 5.8
    
    for r in range(rows):
        line_chars = ""
        for c in range(cols):
            val = img_small[r, c]
            idx = int((val / 255.0) * (ramp_len - 1))
            line_chars += RAMP[idx]
            
        group.add(dwg.text(
            line_chars, 
            insert=(18, y_start + (r * line_height)), 
            class_='ascii-line'
        ))

    dwg.add(group)
    dwg.save()
    print("avi-ascii.svg generated with typing wipe animation.")

if __name__ == "__main__":
    generate_ascii_svg()