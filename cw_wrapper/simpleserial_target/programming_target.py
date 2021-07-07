import os
import chipwhisperer as cw


def programming_target(scope,
                       dot_hex_path: str,
                       programmer_type: str,
                       is_STM32F1: bool = False
                       ) -> None:
    assert scope is not None and scope.getStatus() is True
    assert programmer_type.lower() in ('xmega', 'stm32f', 'avr')
    assert os.path.exists(dot_hex_path), "The .hex file does not exist."
    assert 7.37 <= round(scope.clock.clkgen_freq * 1e-6, 2) <= (8.01 if is_STM32F1 else 7.38)
    if programmer_type.lower() == "xmega":
        programmer = cw.programmers.XMEGAProgrammer
    elif programmer_type.lower() == "stm32f":
        programmer = cw.programmers.STM32FProgrammer
    else:
        programmer = cw.programmers.AVRProgrammer
    cw.program_target(scope, programmer, dot_hex_path)
    pass
