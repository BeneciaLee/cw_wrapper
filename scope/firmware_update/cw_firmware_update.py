import chipwhisperer as cw


def cw_firmware_auto_update():
    scope = cw.scope()
    _ = cw.target(scope)
    programmer = cw.SAMFWLoader(scope=scope)
    programmer.auto_program()
    pass
