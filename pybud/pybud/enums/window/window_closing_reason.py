from enum import Enum


class WindowClosingReason(Enum):
    Unknown = -1
    KeyboardInterrupt = 0
    ApplicationExit = 1
    InteractionFinish = 2