def get_setPos1(x: float) -> str:
    data = f"10{x}"
    return data


def getPos1():
    return "18"


def get_setPos2(x: float) -> str:
    data = f"20{x}"
    return data


def getPos2():
    return "28"


def get_stepPS1(x: float) -> str:
    data = f"11{x}"
    return data


def get_stepPS2(x: int) -> str:
    data = f"21{x}"
    return data


def get_global_stepsPS(x: int) -> str:
    data = f"01{x}"
    return data


def get_accel1(x: int) -> str:
    data = f"12{x}"
    return data


def get_accel2(x: int) -> str:
    data = f"22{x}"
    return data


def get_global_accel(x: int) -> str:
    data = f"01{x}"
    return data


def getInitTMC() -> str:
    return "99"
