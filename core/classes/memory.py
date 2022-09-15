from core.classes.exceptions import InvalidProcessError
from psutil import AccessDenied, NoSuchProcess, ZombieProcess, process_iter
from pymem import Pymem
from pymem.pattern import pattern_scan_module
from pymem.process import base_module, module_from_name


def _open_process(process_name: str) -> Pymem:
    for proc in process_iter():
        try:
            proc_name = proc.name()

            if proc_name == process_name:
                return Pymem(proc_name)
        except (NoSuchProcess, AccessDenied, ZombieProcess):
            pass
    raise InvalidProcessError


def _convert_pattern(pattern: str) -> bytes:
    return b''.join([b'\\x%b' % byte.encode() if byte != '?' else b'.' for byte in pattern.split()])


class Memory:
    def __init__(self, process_name: str, module_name: str | None = None) -> None:
        self.proc = _open_process(process_name)
        self.modu = base_module(self.proc.process_handle) if module_name is None else module_from_name(self.proc.process_handle, module_name)

        self.save_addr = 0
        self.reset()

    def reset(self) -> None:
        self.addr = 0
        self.prev_addr = 0
        self.prev_offs = 0

        if self.save_addr != 0:
            self.addr = self.save_addr

    def pattern_scan(self, pattern: str) -> None:
        self.addr = pattern_scan_module(self.proc.process_handle, self.modu, _convert_pattern(pattern))
        self.save_addr = self.addr

    def add(self, offs: int) -> None:
        self.prev_addr = self.addr
        self.prev_offs = offs
        self.addr += offs

    def sub(self, offs: int) -> None:
        self.prev_addr = self.addr
        self.prev_offs = -offs
        self.addr -= offs

    def rip(self) -> None:
        self.addr += self.proc.read_int(self.prev_addr + self.prev_offs) + 4

    def read(self, type: str, *args) -> bool | int | float | str | bytes | None:
        try:
            return getattr(self.proc, f'read_{type}')(self.addr, *args)
        except AttributeError:
            pass
