# BotMonth is defined as 30 days of exactly 24 hours, expressed in seconds.
BotMonth = 60 * 60 * 24 * 30
CompactTimestampAccuracyInSeconds = 60
MaxBotPrepaidMonths = 24


class TFChainTime:
    def extend(self, timestamp, months):
        timestamp -= timestamp % CompactTimestampAccuracyInSeconds
        return timestamp + (months * BotMonth)

    def months_diff(self, from_time, to_time):
        from_time -= from_time % CompactTimestampAccuracyInSeconds

        return (to_time - from_time) / BotMonth
