def read_file(name):
    try:
        with open(name, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"ERROR reading {name}: {str(e)}"
