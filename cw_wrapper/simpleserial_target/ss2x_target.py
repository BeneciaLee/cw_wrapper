import numpy as np
from typing import Union, Optional
from .ss_target_base import SSTargetBase


class SS2xTarget(SSTargetBase):
    """
    ChipWhisperer SimpleSerial v2.0 target
    """
    def __init__(self, scope, target):
        super().__init__(scope, target)
        self._crc_poly = 0xA6
        pass

    def set_crc_poly(self, crc_poly: int = 0xA6):
        assert 0x01 <= crc_poly <= 0xFF
        self._crc_poly = crc_poly
        pass

    def ss_wait_ack(self, timeout: int = 500) -> bool:
        raise NotImplementedError()
        pass

    def ss_write(self,
                 cmd: Union[str, int],
                 scmd: int,
                 payload_len: int,
                 payload: Optional[Union[bytearray, str, np.str_]],
                 following_ack: bool = True,
                 timeout: int = 500
                 ) -> bool:
        raise NotImplementedError()
        pass

    def ss_read(self,
                cmd: Union[str, int],
                payload_len: int,
                following_ack: bool = True,
                timeout: int = 500
                ) -> Optional[str]:
        raise NotImplementedError()
        pass
    pass
