import svgwrite

def build_info_card():
    dwg = svgwrite.Drawing('info-card.svg', size=('100%', '340px'))
    
    # Window Frame
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=8, ry=8, fill='#0d1117', stroke='#30363d', stroke_width=1))
    
    # Top Bar
    dwg.add(dwg.circle(center=(20, 20), r=5, fill='#ff5f56'))
    dwg.add(dwg.circle(center=(35, 20), r=5, fill='#ffbd2e'))
    dwg.add(dwg.circle(center=(50, 20), r=5, fill='#27c93f'))
    dwg.add(dwg.text("$ whoami", insert=(70, 24), fill='#8b949e', font_family='monospace', font_size='12px'))

    # User rows matching Avi's exact key-value formatting
    lines = [
        ("User", "syedhassanstudies-rgb@github"),
        ("Role", "IT Undergraduate @ QUEST Nawabshah"),
        ("Focus", "Backend Developer | LLM Engineer | Game Dev"),
        ("Stack", "Python · FastAPI · RAG · React · AWS"),
        ("Project", "UniMind AI (Dual-LLM RAG System)"),
        ("Edu", "BSIT @ Quaid-e-Awam University (QUEST)"),
    ]

    y_offset = 62
    for label, val in lines:
        dwg.add(dwg.text(f"{label}:", insert=(20, y_offset), fill='#d29922', font_family='monospace', font_size='12px', font_weight='bold'))
        dwg.add(dwg.text(val, insert=(95, y_offset), fill='#c9d1d9', font_family='monospace', font_size='12px'))
        y_offset += 42

    dwg.save()
    print("info-card.svg generated successfully.")

if __name__ == "__main__":
    build_info_card()