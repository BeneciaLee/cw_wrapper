import os
import chipwhisperer as cw
from .. import SSTargetBase, SS1xTarget, SS2xTarget


class SSTargetStandAlone(SSTargetBase):
    def __init__(self):
        super().__init__(None, None)
        pass

    def connect(self) -> None:
        self._scope = cw.scope(scope_type=cw.scopes.OpenADC)
        self._scope.default_setup()
        self._target = cw.target(self._scope, target_type=cw.targets.SimpleSerial)
        pass

    def disconnect(self) -> None:
        assert self._scope is not None
        self._scope.dis()
        self._scope = None
        self._target = None
        pass

    def program_target(self,
                       dot_hex_path: str,
                       programmer_type: str,
                       reset_target_after_programming: bool = True
                       ) -> None:
        assert programmer_type.lower() in ('xmega', 'stm32f'), \
            f"'{dot_hex_path}' is unsupported programmer type. (Available: xmega, stm32f)"
        assert os.path.exists(dot_hex_path), "The .hex file does not exist."
        if programmer_type.lower() == "xmega":
            programmer = cw.programmers.XMEGAProgrammer
        else:
            programmer = cw.programmers.STM32FProgrammer
        cw.program_target(self._scope, programmer, dot_hex_path)
        if reset_target_after_programming:
            self.reset_using_nRST_pin()
        pass
    pass


class SS1xTargetStandAlone(SSTargetStandAlone, SS1xTarget):
    pass


class SS2xTargetStandAlone(SSTargetStandAlone, SS2xTarget):
    pass
