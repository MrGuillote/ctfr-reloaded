import shutil
import subprocess


def tool_available(name):
    return shutil.which(name) is not None


def run_httpx(names, console, extra_args=None):
    if not tool_available("httpx"):
        raise RuntimeError("httpx no esta instalado o no esta en PATH.")

    args = ["httpx", "-silent", "-status-code", "-title"]
    if extra_args:
        args.extend(extra_args)

    console.info("Ejecutando httpx sobre {n} subdominios...".format(n=len(names)))
    process = subprocess.run(
        args,
        input="\n".join(names),
        text=True,
        capture_output=False,
    )
    return process.returncode


def run_nuclei(names, console, extra_args=None):
    if not tool_available("nuclei"):
        raise RuntimeError("nuclei no esta instalado o no esta en PATH.")

    args = ["nuclei", "-silent"]
    if extra_args:
        args.extend(extra_args)

    console.info("Ejecutando nuclei sobre {n} subdominios...".format(n=len(names)))
    process = subprocess.run(
        args,
        input="\n".join(names),
        text=True,
        capture_output=False,
    )
    return process.returncode


def run_subfinder_merge(domain, console):
    if not tool_available("subfinder"):
        raise RuntimeError("subfinder no esta instalado o no esta en PATH.")

    console.info("Ejecutando subfinder para {d}...".format(d=domain))
    process = subprocess.run(
        ["subfinder", "-d", domain, "-silent"],
        text=True,
        capture_output=True,
    )
    if process.returncode != 0:
        raise RuntimeError("subfinder fallo: {e}".format(e=process.stderr.strip()))
    return [line.strip() for line in process.stdout.splitlines() if line.strip()]


def run_amass_merge(domain, console):
    if not tool_available("amass"):
        raise RuntimeError("amass no esta instalado o no esta en PATH.")

    console.info("Ejecutando amass (passive) para {d}...".format(d=domain))
    process = subprocess.run(
        ["amass", "enum", "-passive", "-d", domain],
        text=True,
        capture_output=True,
    )
    if process.returncode != 0:
        raise RuntimeError("amass fallo: {e}".format(e=process.stderr.strip()))
    return [line.strip() for line in process.stdout.splitlines() if line.strip()]


def run_assetfinder_merge(domain, console):
    if not tool_available("assetfinder"):
        raise RuntimeError("assetfinder no esta instalado o no esta en PATH.")

    console.info("Ejecutando assetfinder para {d}...".format(d=domain))
    process = subprocess.run(
        ["assetfinder", "--subs-only", domain],
        text=True,
        capture_output=True,
    )
    if process.returncode != 0:
        raise RuntimeError("assetfinder fallo: {e}".format(e=process.stderr.strip()))
    return [line.strip() for line in process.stdout.splitlines() if line.strip()]


def run_integration(tool, names, console, domain=None, extra_args=None):
    if tool == "httpx":
        return run_httpx(names, console, extra_args=extra_args)
    if tool == "nuclei":
        return run_nuclei(names, console, extra_args=extra_args)
    if tool == "subfinder":
        if not domain:
            raise RuntimeError("subfinder requiere un unico dominio (-d).")
        return run_subfinder_merge(domain, console)
    if tool == "amass":
        if not domain:
            raise RuntimeError("amass requiere un unico dominio (-d).")
        return run_amass_merge(domain, console)
    if tool == "assetfinder":
        if not domain:
            raise RuntimeError("assetfinder requiere un unico dominio (-d).")
        return run_assetfinder_merge(domain, console)
    raise ValueError("Integracion desconocida: {t}".format(t=tool))
