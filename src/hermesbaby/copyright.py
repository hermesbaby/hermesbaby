def format_copyright(year: str, current_year: int, author: str) -> str:
    year = year.strip()
    if not year:
        return author

    if int(year) < current_year:
        year = f"{year}-{current_year}"

    return f"{year}, {author}"
