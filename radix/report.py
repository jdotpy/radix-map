def as_sorted_dict(d):
    return dict(sorted(d.items()))

def get_line_display(entity):
    if not hasattr(entity, 'line_count'):
        return ''
    return f' :{entity.starting_line} | {entity.line_count} lines'

def display_txt(reports_by_file, output):
    for file_path, report in as_sorted_dict(reports_by_file).items():
        output.write(f"\033[1m#{file_path}\033[0m\n")
        
        # Collect all top-level items to manage "Last Child" logic
        functions = sorted(report.get('functions', []), key=lambda x: x.name)
        definitions = sorted(report.get('definitions', []), key=lambda x: x.name)
        all_top_level = [(f, 'func') for f in functions] + [(d, 'def') for d in definitions]
        
        for i, (item, kind) in enumerate(all_top_level):
            is_last_top = (i == len(all_top_level) - 1)
            marker = "└── " if is_last_top else "├── "
            pipe = "    " if is_last_top else "│   "
            
            if kind == 'func':
                output.write(f"{marker}{item}{get_line_display(item)}\n")
                
                # Render Calls (Tier 3)
                for j, call in enumerate(sorted(item.calls)):
                    is_last_call = (j == len(item.calls) - 1)
                    c_marker = "└── ➜ " if is_last_call else "├── ➜ "
                    output.write(f"{pipe}{c_marker}{call}\n")

            elif kind == 'def':
                # Class or Struct
                output.write(f"{marker}○ {item}\n")
                
                # Methods inside the definition
                methods = item.methods
                for j, method in enumerate(methods):
                    is_last_method = (j == len(methods) - 1)
                    m_marker = "└── " if is_last_method else "├── "
                    m_pipe = "    " if is_last_method else "│   "
                    

                    output.write(f"{pipe}{m_marker}{method}\n")
                    
                    # Calls inside methods
                    for k, call in enumerate(sorted(method.calls)):
                        is_last_m_call = (k == len(method.calls) - 1)
                        mc_marker = "└── ➜ " if is_last_m_call else "├── ➜ "
                        output.write(f"{pipe}{m_pipe}{mc_marker}{call}\n")
        output.write('\n')