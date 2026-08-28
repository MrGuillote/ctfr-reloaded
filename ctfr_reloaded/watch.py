import time

from ctfr_reloaded.output import emit_results, names_from_results


def run_watch_loop(domains, options, args, console, history, scan_fn):
    interval = args.interval
    console.info("Modo watch activo cada {s}s. Ctrl+C para detener.".format(s=interval))

    try:
        while True:
            for domain in domains:
                previous = history.get_last_names(domain) if history and history.enabled else set()
                results = scan_fn([domain], options, console, history)
                current = set(names_from_results(results))
                new_names = sorted(current - previous) if previous else []

                if new_names:
                    console.warn(
                        "[NUEVOS] {d}: {n} subdominios".format(d=domain, n=len(new_names))
                    )
                    for name in new_names:
                        console.subdomain(name, "(nuevo)")
                else:
                    console.success(
                        "{d}: sin cambios ({n} total)".format(d=domain, n=len(current))
                    )

            if not args.quiet and not args.json:
                emit_results(results, args, console)

            console.info("Proximo scan en {s}s...".format(s=interval))
            time.sleep(interval)
    except KeyboardInterrupt:
        console.warn("Watch detenido por el usuario.")
        return 0
