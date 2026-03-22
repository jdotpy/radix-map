

# Radix: Configurable SourceCode summarizer

Quickly summarize project structure with multiple verbosity levels (ok, so maybe there's only one option right now lol). More soon.


## Installation
---

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/jdotpy/radix-map.git](https://github.com/jdotpy/radix-map.git)
   cd radix-map
   pip install .
   ```


2. **Install Dependencies based on code you plan on using:**
   ```bash
   pip install tree-sitter-python
   pip install tree-sitter-go
   pip install tree-sitter-javascript
   ```


## Use
---

```bash
radix map .
```

Example output:
```bash
#tests/test_integration.py
└── ƒ get_test_pairs()

#tests/snapshots/python_ex1.py
├── ƒ global_helper()
└── ○ class DataProcessor
    ├── ƒ __init__(self, source: str)
    ├── ƒ process(self)
    └── ƒ _validate(self)

#radix/scanner.py
└── ○ class ProjectScanner
    ├── ƒ __init__(self, registry, max_bytes: int = 200_000, extra_ignored_dirs: Optional[Set[str]] = None)
    ├── ƒ is_visible(self, path: Path)
    └── ƒ scan(self, target: str)
```

## Supported Languages


| Language | Status | Package Requirement |
|---|---|---|
| Python	| ✅ functions & classes | tree-sitter-python | 
| Go	| 🚧 | tree-sitter-go | 
| JavaScript | 🚧 | tree-sitter-javascript | 

```

