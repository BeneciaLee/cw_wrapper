import sys
import time
import chipwhisperer as cw
import numpy as np
from typing import Union, Optional
from chipwhisperer.capture import scopes


class SSTargetBase:
    def __init__(self, scope, target):
        self._scope: cw.capture.scopes.OpenADC = scope
        self._target: Union[cw.targets.SimpleSerial, cw.targets.SimpleSerial2] = target
        self.rx_history = list()
        self.tx_history = list()
        self.__history_size = 10
        pass

    def print_simpleserial_commsnds(self) -> None:
        cmd_list = self.get_simpleserial_commands()
        for i in cmd_list:
            print(f"cmd: {i['cmd'].decode('ascii')}, len: {i['len']:>3}, flags: {i['flags']}")
        pass

    def get_simpleserial_commands(self) -> list:
        return self._target.get_simpleserial_commands()

    def get_in_waiting(self) -> dict:
        return {"rx": self._target.in_waiting(), "tx": self._target.in_waiting_tx()}

    def _update_rx_history(self, x: str) -> None:
        if len(self.rx_history) >= self.__history_size:
            self.rx_history.pop(-1)
        self.rx_history.insert(0, x)
        pass

    def _update_tx_history(self, x: str) -> None:
        if len(self.tx_history) >= self.__history_size:
            self.tx_history.pop(-1)
        self.tx_history.insert(0, x)
        pass

    def reset_via_UFO_nRST(self,
                           duration=0.1,
                           wait_for_ready: float = 0.1
                           ) -> None:
        """
        This method is used to reset the UFO target board mounted on the CW308 via nRST pin.
        When using nRST pin, unlike using VCC pin, the power supplied to the CW308 is maintained
        and only the power supply of the UFO target board is cut off.

        :param duration: Power-down period
        :param wait_for_ready: Time to wait for target to be ready after reset
        :return: None
        """
        assert 0.05 <= duration <= 10
        assert 0 <= wait_for_ready <= 10
        self._scope.advancedSettings.cwEXTRA.setGPIOStatenrst(0)
        time.sleep(duration)
        self._scope.advancedSettings.cwEXTRA.setGPIOStatenrst(None)
        if wait_for_ready > 0:
            time.sleep(wait_for_ready)
        pass

    def reset_via_VCC(self,
                      duration=0.1,
                      wait_for_ready: float = 0.1
                      ) -> None:
        """
        This method is used to reset the target board via VCC pin.
        When using VCC pin, unlike using nRST pin, the power supplied from the capture board
        to the target board is cut off.

        :param duration: Power-down period
        :param wait_for_ready: Time to wait for target to be ready after reset
        :return: None
        """
        assert 0.05 <= duration <= 10
        assert 0 <= wait_for_ready <= 10
        self._scope.advancedSettings.cwEXTRA.setTargetPowerState(False)
        time.sleep(duration)
        self._scope.advancedSettings.cwEXTRA.setTargetPowerState(True)
        if wait_for_ready > 0:
            time.sleep(wait_for_ready)
        pass

    def set_clock_freq(self,
                       freq: int = 7.37e6,
                       wait_for_ready: float = 0.1,
                       verbose: bool = True
                       ) -> None:
        assert 3.2e6 <= freq <= 25.0e6
        self._scope.clock.clkgen_freq = freq
        self._target.baud = round(38400 * (freq / 7.37e6))
        self.reset_via_VCC(wait_for_ready=wait_for_ready)
        if verbose:
            print(f"Adjusted clock frequency: {int(self._scope.clock.clkgen_freq) * 1e-6:.4f}MHz")
        pass

    def flush_recv_buf(self):
        self._target.flush()
        pass

    def _serial_raw_write(self,
                          data: str,
                          flush: bool = True
                          ) -> bool:
        if not data.endswith("\n"):
            data = data + "\n"
        try:
            if flush:
                self.flush_recv_buf()
            self._target.write(data)
        except:
            return False
        self._update_tx_history(data)
        return True

    def _serial_raw_read(self,
                         payload_len: int,
                         print_warning_msg: bool = True,
                         timeout: int = 500
                         ) -> Optional[str]:
        payload = self._target.read(payload_len, timeout)
        if payload == "":
            if print_warning_msg:
                print("There is no data to receive from Target.", file=sys.stderr)
            return None
        if len(payload) < payload_len and print_warning_msg:
            print(f"The data read from the target is less than expected. "
                  f"(expected: {payload_len}, received: {len(payload)})",
                  file=sys.stderr)
            self._update_rx_history(payload)
            return None
        self._update_rx_history(payload)
        return payload

    def ss_wait_ack(self,
                    timeout: int = 500
                    ):
        raise NotImplementedError()
        pass

    def ss_write(self,
                 cmd: str,
                 data: Optional[Union[bytearray, str, np.str_]],
                 following_ack: bool = True,
                 timeout: int = 500
                 ):
        raise NotImplementedError()
        pass

    def ss_read(self,
                cmd: str,
                length: int,
                following_ack: bool = True,
                timeout: int = 500
                ):
        raise NotImplementedError()
        pass
    pass
