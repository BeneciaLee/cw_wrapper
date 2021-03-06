import time
import numpy as np
from tqdm.autonotebook import tqdm
from cw_wrapper import CWScope, SS1xTarget, make_random_hex

# Connecting ChipWhisperer scope and target
scope = CWScope()
scope.connect(ss_version="1.1")

# Programming target
# scope.programming_target("./test-CW303.hex", "XMEGA", reset_target_after_programming=True)

# Getting SimpleSerial object and printing commands
dut: SS1xTarget = scope.get_simple_serial_target()
scope.reset_target_via_VCC()   # scope.reset_target_via_UFO_nRST()
time.sleep(1)  # Wait for the target device to be ready
dut.print_simpleserial_commsnds()

# Key setting
fixed_key = "2AEF4FBF1020489FFD01F8369D353698"
dut.ss_write("k", 16, fixed_key, following_ack=True)

# Initializing measurement parameters
total_trace = 500
samples = scope.get_status(verbose=False)["samples"]

# Allocating placeholders
traces = np.empty(shape=(total_trace, samples), dtype=np.float64)
plains, ciphers = [], []

# Measuring power traces
cnt = 0
tqdm_progress = tqdm(range(total_trace))
while cnt < total_trace:
    p = make_random_hex(16)
    scope.arm()
    dut.ss_write('p', 16, p, following_ack=False)
    c = dut.ss_read('r', 16, following_ack=True)
    t = scope.get_waveform()
    if t is None or c is None:
        continue
    plains.append(p)
    ciphers.append(c)
    traces[cnt] = t
    tqdm_progress.update(1)
    cnt += 1
    pass

plains = np.array(plains)
ciphers = np.array(ciphers)

# Saving power traces and metadata
np.save("./traces.npy", traces)
np.save("./plains.npy", plains)
np.save("./ciphers.npy", ciphers)
