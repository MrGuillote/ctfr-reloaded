class ProgressTracker:
    def __init__(self, total, console, enabled=True):
        self.total = total
        self.console = console
        self.enabled = enabled and total > 1
        self.completed = 0

    def start(self, label):
        if self.enabled:
            self.console.info("{label} (0/{total})".format(label=label, total=self.total))

    def step(self, label):
        self.completed += 1
        if self.enabled:
            self.console.info(
                "{label} ({done}/{total})".format(
                    label=label, done=self.completed, total=self.total
                )
            )
