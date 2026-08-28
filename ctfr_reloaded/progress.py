try:
    from tqdm import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class ProgressTracker:
    def __init__(self, total, console, enabled=True, use_tqdm=False, desc="Progreso"):
        self.total = total
        self.console = console
        self.enabled = enabled and total > 0
        self.use_tqdm = use_tqdm and TQDM_AVAILABLE and self.enabled
        self.desc = desc
        self.completed = 0
        self._bar = None

    def start(self, label=None):
        if not self.enabled:
            return
        if self.use_tqdm:
            self._bar = tqdm(total=self.total, desc=label or self.desc, unit="item")
        elif self.total > 1:
            self.console.info(
                "{label} (0/{total})".format(label=label or self.desc, total=self.total)
            )

    def step(self, label=None):
        self.completed += 1
        if not self.enabled:
            return
        if self.use_tqdm and self._bar:
            self._bar.set_postfix_str(str(label or ""))
            self._bar.update(1)
        elif self.total > 1:
            self.console.info(
                "{label} ({done}/{total})".format(
                    label=label or self.desc, done=self.completed, total=self.total
                )
            )

    def close(self):
        if self._bar:
            self._bar.close()
            self._bar = None
