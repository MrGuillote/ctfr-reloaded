def run_tui(results, console):
    """TUI interactivo simple para explorar resultados."""
    items = []
    for domain, entries in results.items():
        for entry in entries:
            items.append((domain, entry))

    if not items:
        console.warn("No hay resultados para mostrar.")
        return

    index = 0
    filter_text = ""

    console.info("TUI: [n]ext [p]rev [f]ilter [c]lear [q]uit")

    while True:
        filtered = _filter_items(items, filter_text)
        if not filtered:
            console.warn("Sin coincidencias para filtro: {f}".format(f=filter_text))
            index = 0
        else:
            index = max(0, min(index, len(filtered) - 1))
            domain, entry = filtered[index]
            extra = _format_entry(entry)
            console.info(
                "[{i}/{t}] {d} -> {n} {extra}".format(
                    i=index + 1, t=len(filtered), d=domain, n=entry["name"], extra=extra
                )
            )

        choice = input("> ").strip().lower()
        if choice in ("q", "quit", "exit"):
            break
        if choice in ("n", "next", ""):
            index = min(index + 1, max(0, len(filtered) - 1))
        elif choice in ("p", "prev"):
            index = max(index - 1, 0)
        elif choice.startswith("f "):
            filter_text = choice[2:].strip().lower()
            index = 0
        elif choice == "c":
            filter_text = ""
            index = 0
        elif choice.isdigit():
            num = int(choice) - 1
            if 0 <= num < len(filtered):
                index = num


def _filter_items(items, filter_text):
    if not filter_text:
        return items
    return [
        (domain, entry)
        for domain, entry in items
        if filter_text in entry["name"].lower() or filter_text in domain.lower()
    ]


def _format_entry(entry):
    parts = []
    if entry.get("score") is not None:
        parts.append("score={s}".format(s=entry["score"]))
    if entry.get("vulnerable"):
        parts.append("TAKEOVER")
    if entry.get("cdn"):
        parts.append("cdn={c}".format(c=entry["cdn"]))
    return "({p})".format(p=", ".join(parts)) if parts else ""
