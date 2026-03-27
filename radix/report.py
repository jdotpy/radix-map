def as_sorted_dict(d):
    return dict(sorted(d.items()))

def line_count_pad_size(source):
    m = 0
    for report in source.values():
        m = max(m, report['lines'])
    return (len(str(m)) * 2) + len('[:]')

def get_line_range_str(item=None, size=None, default=''):
    if size == 0:
        lines = (0, 0)
    elif size is not None:
        lines = (1, size)
    elif hasattr(item, 'source_lines'):
        lines = (item.source_lines[0], item.source_lines[1])
    else:
        return default

    range_text = f"[{lines[0]}:{lines[1]}]"
    return f"{range_text}"


def display_txt(reports_by_file, output, lines=False):
    if lines:
        max_gutter = line_count_pad_size(reports_by_file) + 1 # for padding
        gutter_spacing = " " * max_gutter
    else:
        max_gutter = 0
        gutter_spacing = ''
        line_range = ''

    for file_path, report in as_sorted_dict(reports_by_file).items():
        if lines:
            file_lines = get_line_range_str(size=report['lines']).ljust(max_gutter)
        else:
            file_lines = ''
        output.write(f"\n{file_lines}\033[1m # {file_path}\033[0m\n")
        
        all_top_level = ([(f, 'func') for f in sorted(report.get('functions', []), key=lambda x: x.name)] + 
                         [(d, 'def') for d in sorted(report.get('definitions', []), key=lambda x: x.name)])
        
        for i, (item, kind) in enumerate(all_top_level):
            is_last_top = (i == len(all_top_level) - 1)
            marker = "└── " if is_last_top else "├── "
            pipe = "    " if is_last_top else "│   "
            
            if lines:
                line_range = get_line_range_str(item, default=gutter_spacing).ljust(max_gutter)
            
            if kind == 'func':
                output.write(f"{line_range} {marker} {item}\n")
                # Render Calls
                for j, call in enumerate(sorted(item.calls)):
                    is_last_call = (j == len(item.calls) - 1)
                    c_marker = "└── ➜ " if is_last_call else "├── ➜ "
                    output.write(f"{gutter_spacing} {pipe}{c_marker}{call}\n")

            elif kind == 'def':
                output.write(f"{line_range} {marker}○ {item}\n")
                # Render Methods
                methods = item.methods
                for j, method in enumerate(methods):
                    is_last_method = (j == len(methods) - 1)
                    m_marker = "└── " if is_last_method else "├── "
                    m_pipe = "    " if is_last_method else "│   "
                    
                    if lines:
                        m_line_range = get_line_range_str(method, default=gutter_spacing).ljust(max_gutter)
                    else:
                        m_line_range = ''
                    output.write(f"{m_line_range} {pipe}{m_marker}{method}\n")