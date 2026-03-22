
def display_txt(reports_by_file):
    for file_path, report in reports_by_file.items():
        print(f"\033[1m#{file_path}\033[0m")
        
        # Collect all top-level items to manage "Last Child" logic
        functions = report.get('functions', [])
        definitions = report.get('definitions', [])
        all_top_level = [(f, 'func') for f in functions] + [(d, 'def') for d in definitions]
        
        for i, (item, kind) in enumerate(all_top_level):
            is_last_top = (i == len(all_top_level) - 1)
            marker = "└── " if is_last_top else "├── "
            pipe = "    " if is_last_top else "│   "
            
            if kind == 'func':
                print(f"{marker}{item}")
                
                # Render Calls (Tier 3)
                for j, call in enumerate(item.calls):
                    is_last_call = (j == len(item.calls) - 1)
                    c_marker = "└── ➜ " if is_last_call else "├── ➜ "
                    print(f"{pipe}{c_marker}{call}")

            elif kind == 'def':
                # Class or Struct
                print(f"{marker}○ {item}")
                
                # Methods inside the definition
                methods = item.methods
                for j, method in enumerate(methods):
                    is_last_method = (j == len(methods) - 1)
                    m_marker = "└── " if is_last_method else "├── "
                    m_pipe = "    " if is_last_method else "│   "
                    

                    print(f"{pipe}{m_marker}{method}")
                    
                    # Calls inside methods
                    for k, call in enumerate(method.calls):
                        is_last_m_call = (k == len(method.calls) - 1)
                        mc_marker = "└── ➜ " if is_last_m_call else "├── ➜ "
                        print(f"{pipe}{m_pipe}{mc_marker}{call}")
        print() # Space between files