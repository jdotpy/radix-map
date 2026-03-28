class Theme:
    def __init__(self, use_color=False):
        # ANSI Escape Codes
        self.BOLD = "\033[1m" if use_color else ""
        self.DIM = "\033[2m" if use_color else ""
        self.GREEN = "\033[32m" if use_color else ""
        self.BLUE = "\033[34m" if use_color else ""
        self.CYAN = "\033[36m" if use_color else ""
        self.YELLOW = "\033[33m" if use_color else ""
        self.RESET = "\033[0m" if use_color else ""

    def file(self, text):
        return f"{self.BOLD}# {text}{self.RESET}"
    def gutter(self, text):
        return f"{self.DIM}{text}{self.RESET}"
    def func(self, text):
        return f"{self.CYAN}ƒ {text}{self.RESET}"
    def class_obj(self, text):
        return f"{self.YELLOW}{text}{self.RESET}"
    def call(self, text):
        return f"{self.GREEN}{text}{self.RESET}"

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


def display_txt(reports_by_file, output, lines=False, theme=None):
    t = theme or Theme(use_color=False)
    if lines:
        max_gutter = line_count_pad_size(reports_by_file) + 1 # for padding
        gutter_spacing = " " * max_gutter
    else:
        max_gutter = 0
        gutter_spacing = ''
        line_range = ''

    for file_path, report in as_sorted_dict(reports_by_file).items():
        if lines:
            file_lines = t.gutter(get_line_range_str(size=report['lines']).ljust(max_gutter))
        else:
            file_lines = ''
        output.write(f"\n{file_lines}{t.file(file_path)}\n")
        
        all_top_level = ([(f, 'func') for f in report.get('functions', [])] + 
                         [(d, 'def') for d in report.get('definitions', [])])
        all_top_level.sort(key=lambda item: item[0].source_lines[0])

        for i, (item, kind) in enumerate(all_top_level):
            is_last_top = (i == len(all_top_level) - 1)
            marker = "└── " if is_last_top else "├── "
            pipe = "    " if is_last_top else "│   "
            
            if lines:
                raw_range = get_line_range_str(item, default=gutter_spacing).ljust(max_gutter)
                line_range = t.gutter(raw_range)
            
            if kind == 'func':
                output.write(f"{line_range}{marker}{t.func(item)}\n")

            elif kind == 'def':
                output.write(f"{line_range}{marker}○ {t.class_obj(item)}\n")
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
                    output.write(f"{t.gutter(m_line_range)}{pipe}{m_marker}{t.func(method)}\n")