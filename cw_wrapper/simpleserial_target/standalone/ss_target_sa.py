import chipwhisperer as cw
from .. import SSTargetBase, SS1xTarget, SS2xTarget
from ...scope.common import programming_target


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

    def programming_target(self,
                           dot_hex_path: str,
                           programmer_type: str,
                           reset_target_after_programming: bool = True
                           ) -> None:
        programming_target(self._scope, dot_hex_path, programmer_type, reset_target_after_programming)
        pass
    pass


class SS1xTargetStandAlone(SSTargetStandAlone, SS1xTarget):
    pass


class SS2xTargetStandAlone(SSTargetStandAlone, SS2xTarget):
    pass
