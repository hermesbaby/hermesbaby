def format_copyright(year: str, current_year: int, author: str) -> str:
    year = int(year)
    if year == 0:
        return author

    if year < current_year:
        year = f"{year}-{current_year}"

    return f"{year}, {author}"
