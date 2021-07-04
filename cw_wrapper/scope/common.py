import os
import time
import chipwhisperer as cw


def programming_target(scope,
                       dot_hex_path: str,
                       programmer_type: str,
                       reset_target_after_programming: bool = True
                       ) -> None:
    assert scope is not None and scope.getStatus() is True
    assert programmer_type.lower() in ('xmega', 'stm32f'), \
        f"'{dot_hex_path}' is unsupported programmer type. (Available: xmega, stm32f)"
    assert os.path.exists(dot_hex_path), "The .hex file does not exist."
    if programmer_type.lower() == "xmega":
        programmer = cw.programmers.XMEGAProgrammer
    else:
        programmer = cw.programmers.STM32FProgrammer
    cw.program_target(scope, programmer, dot_hex_path)
    if reset_target_after_programming:
        scope.reset_target_via_VCC()
    pass


def reset_target_via_UFO_nRST(scope, duration=0.1) -> None:
    """
    This method is used to reset the UFO target board mounted on the CW308 via nRST pin.
    When using nRST pin, unlike using VCC pin, the power supplied to the CW308 is maintained
    and only the power supply of the UFO target board is cut off.

    :param duration: Power-down period
    :return: None
    """
    assert 0.05 <= duration <= 10
    scope.advancedSettings.cwEXTRA.setGPIOStatenrst(0)
    time.sleep(duration)
    scope.advancedSettings.cwEXTRA.setGPIOStatenrst(None)
    pass


def reset_target_via_VCC(scope, duration=0.1) -> None:
    """
    This method is used to reset the target board via VCC pin.
    When using VCC pin, unlike using nRST pin, the power supplied from the capture board
    to the target board is cut off.

    :param duration: Power-down period
    :return: None
    """
    assert 0.05 <= duration <= 10
    scope.advancedSettings.cwEXTRA.setTargetPowerState(False)
    time.sleep(duration)
    scope.advancedSettings.cwEXTRA.setTargetPowerState(True)
    pass
