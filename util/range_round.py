
def range_round(value, minimum=None, maximum=None):
    """
    与えられた値を、最小値から最大値までに丸めます。
    非破壊処理です。
    :param value: 値
    :param minimum: 最小値
    :param maximum: 最大値
    :return: 丸められた値
    """
    if minimum is not None and value < minimum:
        return minimum
    if maximum is not None and value > maximum:
        return maximum
    return value
