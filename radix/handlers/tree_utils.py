try:
    from tree_sitter import QueryCursor, Query
except (ImportError, AttributeError):
    QueryCursor = None
    Query = None

def ts_line_info(node):
    if isinstance(node, list) and len(node) == 1:
        node = node[0]
    return {'source_lines': (node.start_point[0] + 1, node.end_point[0] + 1)}

def ts_get_captures(query, root_node):
    """
    A cross-version generator for tree-sitter captures.
    """
    # Version A: Modern API (0.21.0+) 
    if QueryCursor is not None:
        cursor = QueryCursor(query)
        for index, captures in cursor.matches(root_node):
            yield index, captures
        return

    # Version B: Older versions dont have cursor and allow query.captures(root_node) which returns a list
    if hasattr(query, 'captures'):
        results = query.matches(root_node)
        for index, captures in results:
            yield index, captures
    else:
        raise RuntimeError("No compatible tree-sitter capture method found.")

def one(source):
    """ helper that extracts the first element or child for a tree node or None """
    if source is None:
        return None
    if hasattr(source, "children"):
        source = source.children
    if isinstance(source, list):
        if len(source) >= 1:
            return source[0]
        else:
            return None
    raise ValueError("Unsupported type sent to one()")

def q(lang, text):
    if Query is not None:
        return Query(lang, text)
    return lang.query(text)
    