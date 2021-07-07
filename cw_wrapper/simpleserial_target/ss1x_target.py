import sys
import numpy as np
import binascii
from typing import Union, Optional
from .ss_target_base import SSTargetBase


class SS1xTarget(SSTargetBase):
    """
    ChipWhisperer SimpleSerial v1.1 target
    """
    def ss_wait_ack(self, timeout: int = 500) -> bool:
        ack_payload = self._serial_raw_read(4)
        if ack_payload is None:
            print(f"[SS_ACK] Target did not ack.", file=sys.stderr)
            return False
        if ack_payload[0] != 'z' or not ack_payload.endswith("\n") or len(ack_payload) < 4:
            print(f"[SS_ACK] Invalid ACK packet format detected. (received: " + ack_payload.replace("\n", "\\n") + ")",
                  file=sys.stderr)
            return False
        try:
            ret = int(ack_payload[1:3], 16)
        except ValueError:
            print(f"[SS_ACK] Invalid ACK packet format detected. (received: " + ack_payload.replace("\n", "\\n") + ")",
                  file=sys.stderr)
            return False
        if ret != 0:
            print(f"[SS_ACK] The error code was passed through an ACK packet. (0x{ret:02X})", file=sys.stderr)
            return False
        return True

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
        cmd += binascii.hexlify(data).decode().upper()
        cmd += "\n"
        if self._serial_raw_write(cmd) is False:
            return False
        if following_ack:
            if self.ss_wait_ack(timeout) is False:
                return False
        return True

    def ss_read(self,
                cmd: str,
                length: int,
                following_ack: bool = True,
                timeout: int = 500
                ) -> Optional[str]:
        assert len(cmd) == 1, "The length of 'cmd' must be 1."
        assert 1 <= length <= 64
        buf = self._serial_raw_read(length * 2 + 1 + 1)
        if buf is None:
            return None
        if not buf.endswith("\n"):
            print(f"[SS_READ] Invalid SimpleSerial response packet format detected. (received: " +
                  buf.replace("\n", "\\n") + ")", file=sys.stderr)
            return None
        if buf[0] != cmd:
            print(f"[SS_READ] Unexpected response command detected. (expected: '{cmd}', received: '{buf[0]}')",
                  file=sys.stderr)
            return None
        try:
            for i in range(1, length * 2 + 1, 2):
                _ = int(buf[i:i+2], 16)
        except ValueError:
            print(f"[SS_READ] Invalid hexadecimal str was detected in the SimpleSerial response packet.",
                  file=sys.stderr)
            return None
        if following_ack:
            if not self.ss_wait_ack(timeout):
                print(f"[SS_READ] Response '{buf}' received. But target did not ack.", file=sys.stderr)
                return None
        return buf[1:2*length+1]
    pass
