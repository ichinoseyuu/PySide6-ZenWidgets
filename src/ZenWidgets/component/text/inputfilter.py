from collections.abc import Callable, Iterable

TextFilter = Callable[[str, int, int, str], str]


class ZTextFilter:
    """可组合的文本转换策略，供输入控件过滤用户输入。"""

    @classmethod
    def printableOnly(cls) -> TextFilter:
        return lambda current, start, end, text: ''.join(
            char for char in text if char.isprintable()
        )

    @classmethod
    def digitsOnly(cls) -> TextFilter:
        return lambda current, start, end, text: ''.join(
            char for char in text if char.isdigit()
        )

    @classmethod
    def allowCharacters(cls, characters: Iterable[str]) -> TextFilter:
        allowed = frozenset(characters)
        return lambda current, start, end, text: ''.join(
            char for char in text if char in allowed
        )

    @classmethod
    def maxLength(cls, length: int) -> TextFilter:
        if length < 0:
            raise ValueError('length must be non-negative')

        def filter_length(current: str, start: int, end: int, text: str) -> str:
            replaced_length = max(0, end - start)
            available = max(0, length - (len(current) - replaced_length))
            return text[:available]

        return filter_length

    @classmethod
    def compose(cls, *filters: TextFilter) -> TextFilter:
        def apply(current: str, start: int, end: int, text: str) -> str:
            for text_filter in filters:
                text = text_filter(current, start, end, text)
            return text

        return apply


# Usage examples:
#
# Account: digits only, with a 20-character limit.
# account_filter = ZTextFilter.compose(
#     ZTextFilter.digitsOnly(),
#     ZTextFilter.maxLength(20),
# )
# account_edit = ZLineEdit(parent, input_filter=account_filter)
#
# Password: ZPasswordEdit already filters non-printable characters.
# password_edit = ZPasswordEdit(
#     parent,
#     input_filter=ZTextFilter.maxLength(32),
# )
#
# Numeric: keep decimal and sign characters; ZNumericEdit applies its own
# decimal-place and negative-number rules. Do not use digitsOnly() here.
# number_edit = ZNumericEdit(
#     parent,
#     allow_decimal=True,
#     allow_negative=True,
#     input_filter=ZTextFilter.allowCharacters("0123456789.-"),
# )