from fractions import Fraction

from ._sanitisation import sanitise as san


class _InitialAstNode:
    def handle_next_char(self, char):
        if char == ' ':
            return self
        elif 'A' <= char <= 'Z':
            return _NameInProgressAstNode(char)
        elif '0' <= char <= '9' or char == '.':
            return _OuterAstNode(_NameAstNode("ZERO"), 1, _TimeAstNode(char)
            )
        elif char == '-':
            return _OuterAstNode(_NameAstNode("ZERO"), -1, _TimeAstNode(""))
        elif char in "_+()/":
            raise ValueError(f"invalid first character for 's': {char!r}")
        else:
            raise ValueError(f"invalid character in 's': {char!r}")

    def evaluate(self):
        raise ValueError("'s' is empty")


class _NameInProgressAstNode:
    def __init__(self, name):
        self.name = name

    def handle_next_char(self, char):
        if char == ' ':
            return _NameAstNode(self.name)
        elif 'A' <= char <= 'Z' or char == '_':
            self.name += char

            return self
        elif char == '+':
            return _OuterAstNode(_NameAstNode(self.name), 1, _TimeAstNode(""))
        elif char == '-':
            return _OuterAstNode(
                _NameAstNode(self.name), -1, _TimeAstNode("")
            )
        elif '0' <= char <= '9' or char in ".()/":
            raise ValueError(
                f"invalid character following name in 's': {char}"
            )
        else:
            raise ValueError(f"invalid character in 's': {char!r}")

    def evaluate(self):
        return _OuterAstNode(
            _NameAstNode(self.name), 1, _TimeAstNode("0")
        ).evaluate()


class _NameAstNode:
    def __init__(self, name):
        self.name = name

    def handle_next_char(self, char):
        if char == ' ':
            return self
        elif char == '+':
            return _OuterAstNode(self, 1, _TimeAstNode(""))
        elif char == '-':
            return _OuterAstNode(self, -1, _TimeAstNode(""))
        elif 'A' <= char <= 'Z' or char == '_':
            raise ValueError(
                f"name character after completed name in 's': {char!r}"
            )
        elif '0' <= char <= '9' or char in ".()/":
            raise ValueError(
                f"invalid character after completed name in 's': {char!r}"
            )
        else:
            raise ValueError(f"invalid character in 's': {char!r}")

    def evaluate(self):
        return _OuterAstNode(
            self, 1, _TimeAstNode("0")
        ).evaluate()


class _TimeAstNode:
    def __init__(self, time):
        self.time = time

    def _parse_seconds(self, s):
        s = s.strip()

        parts = s.split('+')
        if len(parts) == 2:
            return (
                self._parse_seconds(parts[0])
                + self._parse_seconds(parts[1])
            )
        elif len(parts) > 2:
            raise ValueError(
                f"too many pluses in seconds substring ({s!r}) in 's'"
            )

        parts = s.split('/')
        if len(parts) == 2:
            return (
                self._parse_seconds(parts[0])
                / self._parse_seconds(parts[1])
            )
        elif len(parts) > 2:
            raise ValueError(
                f"too many divides in seconds substring {s!r} in 's'"
            )

        if ' ' in s:
            raise ValueError(
                f"inappropriately-placed space in seconds substring {s!r} in "
                "'s'"
            )

        for char in s:
            if not '0' <= char <= '9' and char not in "_.":
                raise ValueError(
                    f"invalid character in seconds substring {s!r} in 's': "
                    f"{char!r}"
                )

        return Fraction(s)

    def _parse_units(self, s="0", m="0", h="0"):
        try:
            h = int(h)
        except Exception:
            raise ValueError(f"hours substring ({h!r}) in 's' is invalid")

        try:
            m = int(m)
        except Exception:
            raise ValueError(f"hours substring ({m!r}) in 's' is invalid")

        return h*3600 + m*60 + self._parse_seconds(s)

    def _parse_hms_time(self):
        if ':' in self.time:
            raise ValueError("offset in 's' should not use both : and h/m/s")

        h, *rest = self.time.split('h')

        if len(rest) == 0:
            h, rest = "0", (h,)
        elif len(rest) > 1:
            raise ValueError("there should not be more than 1 'h' in 's'")

        m, *rest = rest[0].split('m')

        if len(rest) == 0:
            m, rest = "0", (m,)
        elif len(rest) > 1:
            raise ValueError("there should not be more than 1 'm' in 's'")

        s, *rest = rest[0].split('s')

        if len(rest) == 1:
            if rest[0]:
                if rest[0] == ')':
                    raise ValueError(
                        "offset in 's' ends with more brackets than it "
                        "starts with"
                    )
                else:
                    raise ValueError(
                        "there should not be anything after the 's' in 's'"
                    )
        elif len(rest) > 1:
            raise ValueError("there should not be more than 1 's' in 's'")

        return self._parse_units(h=h, m=m, s=s)

    def _parse_colon_time(self):
        units = self.time.split(':')

        if len(units) > 3:
            raise ValueError("there should not be more than 3 colons in 's'")

        return self._parse_units(*reversed(units))

    def handle_next_char(self, char):
        self.time += char

        return self

    def evaluate(self):
        return _OuterAstNode(
            _NameAstNode("ZERO"), 1, self
        ).evaluate()

    def get_fraction(self):
        while True:
            if not self.time:
                return Fraction(0)

            if self.time[0] == '(':
                if self.time[-1] == ')':
                    self.time = self.time[1:-1]
                else:
                    raise ValueError(
                        "offset in 's' starts with more brackets than it "
                        "ends with"
                    )
            else:
                break

        for char in "hms":
            if char in self.time:
                return self._parse_hms_time()

        if ':' in self.time:
            return self._parse_colon_time()
        else:
            return self._parse_seconds(self.time)


class _OuterAstNode:
    def __init__(self, name, sign, time):
        self.name, self.sign, self.time = name, sign, time

    def handle_next_char(self, char):
        self.time.time += char

        return self

    def evaluate(self):
        self.time.time = self.time.time.strip()

        if self.sign == -1:
            if '+' in self.time.time:
                if self.time.time[0] != '(':
                    raise ValueError(
                        "after a '-', if there is a '+' in the offset in "
                        "'s', the offset should be enclosed in brackets"
                    )

        self.time.get_fraction()

        return self.name.name, self.sign * self.time.get_fraction()


class Timestamp:
    __slots__ = ["reference_point", "total_seconds"]

    def __init__(self, *, _reference_point, _total_seconds):
        self.reference_point = san("_reference_point", "reference_point")
        self.total_seconds = san("_total_seconds", "total_seconds")

    def __repr__(self):
        if self.reference_point == "ZERO":
            return f"Timestamp.from_total_seconds({self.total_seconds!r})"
        else:
            return (
                f"Timestamp.from_total_seconds({self.total_seconds!r}, "
                f"reference_point={self.reference_point!r})"
            )

    def __str__(self):
        match divmod(self.seconds, 1):
            case 0, 0:
                s = ""
            case 0, fractional_part:
                s = f"{fractional_part}s"
            case whole_part, 0:
                s = f"{whole_part}s"
            case whole_part, fractional_part:
                s = f"{whole_part}+{fractional_part}s"

        if self.minutes:
            s = f"{self.minutes}m{s}"

        if self.hours:
            s = f"{self.hours}h{s}"

        if not s:
            s = "0s"

        if self.sign == -1:
            if '+' in s:
                s = f"-({s})"
            else:
                s = f"-{s}"

        if self.reference_point != "ZERO":
            if s == "0s":
                s = self.reference_point
            elif self.sign == 1:
                s = f"{self.reference_point}+{s}"
            else:
                s = f"{self.reference_point}{s}"

        return s

    @property
    def sign(self):
        return 1 if self.total_seconds >= 0 else -1

    @property
    def hours(self):
        return abs(self.total_seconds) // 3600

    @property
    def minutes(self):
        return abs(self.total_seconds) // 60 % 60

    @property
    def seconds(self):
        return abs(self.total_seconds) % 60

    @classmethod
    def from_total_seconds(cls, total_seconds, *, reference_point="ZERO"):
        return cls(
            _reference_point=san("reference_point"),
            _total_seconds=san("total_seconds")
        )

    @classmethod
    def from_samples(cls, samples, *, sample_rate, reference_point="ZERO"):
        samples, sample_rate = san("samples"), san("sample_rate")

        return cls(
            _reference_point=san("reference_point"),
            _total_seconds=samples / sample_rate
        )

    @classmethod
    def from_str(cls, s):
        san("s")

        ast_node = _InitialAstNode()

        for char in s:
            ast_node = ast_node.handle_next_char(char)

        reference_point, total_seconds = ast_node.evaluate()

        return cls(
            _reference_point=reference_point,
            _total_seconds=total_seconds
        )
