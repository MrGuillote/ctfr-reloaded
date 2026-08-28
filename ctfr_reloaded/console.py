import sys

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False

    class _NoColor:
        def __getattr__(self, _):
            return ""

    Fore = Style = _NoColor()


class Console:
    def __init__(self, verbose=False, use_colors=True):
        self.verbose = verbose
        self.use_colors = use_colors and COLORS_ENABLED

    def _c(self, text, color):
        if self.use_colors:
            return "{color}{text}{reset}".format(color=color, text=text, reset=Style.RESET_ALL)
        return text

    def info(self, message):
        print(self._c("[*] {m}".format(m=message), Fore.CYAN))

    def success(self, message):
        print(self._c("[+] {m}".format(m=message), Fore.GREEN))

    def warn(self, message):
        print(self._c("[!] {m}".format(m=message), Fore.YELLOW))

    def error(self, message):
        print(self._c("[X] {m}".format(m=message), Fore.RED), file=sys.stderr)

    def debug(self, message):
        if self.verbose:
            print(self._c("[~] {m}".format(m=message), Fore.BLUE))

    def subdomain(self, name, extra=""):
        line = "[-]  {n}".format(n=name)
        if extra:
            line = "{line} {extra}".format(line=line, extra=extra)
        print(line)

    def banner(self, version):
        print(
            r"""
          ____ _____ _____ ____  
         / ___|_   _|  ___|  _ \ 
        | |     | | | |_  | |_) |
        | |___  | | |  _| |  _ < 
         \____| |_| |_|   |_| \_\

     CTFR-Reloaded v{v}
     100% Free — by MrGuillote
    """.format(v=version)
        )
