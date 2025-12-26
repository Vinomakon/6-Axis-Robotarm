def n_th(j : int) -> str:
    i = j % 10
    if i == 1:
        return f"{j}st"
    if i == 2:
        return f"{j}nd"
    if i == 3:
        return f"{j}rd"
    else:
        return f"{j}th"