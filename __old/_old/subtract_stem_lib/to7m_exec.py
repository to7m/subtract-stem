import inspect
import re


ALL_CODE = False  # optionally set to True when troubleshooting

INDENT_A = INDENT_B = INDENT_C = NUM_LINE_SEP = '  '


class To7mExecError(Exception):
    """
    Should not occur; please report.
    """


class Container:
    def __init__(self, str_, additional_frames=0, all_code=None):
        self.str_ = self._unindent(str_)
        self.additional_frames = additional_frames
        self.all_code = ALL_CODE if all_code is None else all_code

        self.lineno, self.filename = self._frame_info()
        self.code_obj = self._code_obj()

    def _unindent(self, str_):
        lines = str_.split('\n')

        first_line = None
        for line in (lines_iter := iter(lines)):
            if line:
                first_line = line
                break

        if first_line is None:
            return str_

        indent = 0
        for char in first_line:
            if char == ' ':
                indent += 1
            else:
                break

        if indent == 0:
            return str_

        return '\n'.join(line[indent:] for line in lines)

    def _frame_info(self):
        frame = inspect.stack()[self.additional_frames + 2]
        return frame.lineno, frame.filename

    def _file_lines(self):
        yield '<'

        indent = f'{INDENT_A}{INDENT_B}'
        yield f"{indent}compiled at line {self.lineno}, in {self.filename}"
        yield f"{indent}source code:"

        indent += INDENT_C
        lines = self.str_.split('\n')
        rjust_format = '{' f":>{len(str(len(lines)))}" '}'
        for line_num, line in enumerate(lines, 1):
            line_num_str = rjust_format.format(line_num)
            yield f"{indent}{line_num_str}{NUM_LINE_SEP}{line}"

        yield f'{INDENT_A}>'

    def _code_obj(self):
        if self.all_code:
            file_str = '\n'.join(self._file_lines())
        else:
            file_str = f"<compiled at line {self.lineno}, in {self.filename}>"

        return compile(self.str_, file_str, "exec")

    def exec_(self, globals_=None, locals_=None):
        if globals_ is None:
            globals_ = {}

        if locals_ is None:
            exec(self.code_obj, globals_)
            return globals_
        else:
            exec(self.code_obj, globals_, locals_)
            return locals_


class FuncContainer(Container):
    def __init__(self, str_, name=None, additional_frames=0, all_code=None):
        super().__init__(str_, additional_frames + 1, all_code)

        if name is None:
            try:
                names = re.findall("^def *(.*?)\(", self.str_, re.MULTILINE)
                name = names[-1]
            except IndexError:
                raise ValueError("no global def statements") from None
        self.name = name

    def exec_(self, globals_=None, locals_=None):
        scope = super().exec_(globals_, locals_)
        try:
            func = scope[self.name]
        except KeyError:
            err_str = f"missing function {repr(self.name)} in scope"
            raise To7mExecError(err_str) from None

        return func


def func_from_str(
    str_,
    globals_=None, locals_=None,
    name=None, additional_frames=0, all_code=None
):
    func_container = FuncContainer(
        str_, name, additional_frames + 1, all_code
    )
    return func_container.exec_(globals_, locals_)
