import numpy as np
import binascii
from .ss_target_base import SSTargetBase
from typing import Union, Optional


class SS1xTarget(SSTargetBase):
    """
    ChipWhisperer SimpleSerial v1.1 target
    """
    def ss_write(self,
                 cmd: str,
                 data: Optional[Union[bytearray, str, np.str_]],
                 following_ack: bool = True,
                 timeout: int = 500
                 ) -> bool:
        assert len(cmd) == 1, "The length of 'cmd' must be 1."
        if data is None:
            data = bytearray()
        if type(data) is not bytearray:
            data = bytearray.fromhex(data.strip())
        cmd += binascii.hexlify(data).decode()
        cmd += "\n"
        return self._serial_raw_write(cmd, following_ack, timeout)

    def ss_read(self,
                cmd: str,
                length: int,
                following_ack: bool = True,
                timeout: int = 500
                ) -> Optional[str]:
        assert len(cmd) == 1, "The length of 'cmd' must be 1."
        assert 1 <= length <= 64
        buf: bytearray = self._target.simpleserial_read(cmd, length, ack=following_ack, timeout=timeout)
        if buf is None:
            return None
        buf_str = buf.hex().upper().strip()
        self._update_rx_history(f"{cmd}{buf_str}\n")
        return buf_str
    pass
