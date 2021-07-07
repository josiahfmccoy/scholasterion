
__all__ = ['int2roman']


def int2roman(integer, lower=False):
    result = []
    for (arabic, roman) in ROMAN_BASE:
        (factor, integer) = divmod(integer, arabic)
        result.append(roman * factor)
        if integer == 0:
            break
    if lower:
        return ''.join(result).lower()
    else:
        return ''.join(result).upper()


ROMAN_BASE = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I'),
]
