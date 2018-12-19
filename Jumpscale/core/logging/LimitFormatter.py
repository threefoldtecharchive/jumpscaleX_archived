from colorlog import ColoredFormatter

class LimitFormatter(ColoredFormatter):

    def __init__(self, fmt, datefmt, reset, log_colors,
                       secondary_log_colors, style, length):
        super(LimitFormatter, self).__init__(
            fmt=fmt,
            datefmt=datefmt,
            reset=reset,
            log_colors=log_colors,
            secondary_log_colors=secondary_log_colors,
            style=style)
        self.length = length

    def format(self, record):
        if len(record.pathname) > self.length:
            record.pathname = "..." + record.pathname[-self.length:]
        # if len(record.name) > 12:
        #     record.name = "..." + record.name[-12:]

        return super(LimitFormatter, self).format(record)
