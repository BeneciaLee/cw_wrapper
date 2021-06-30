import numpy as np
from tqdm.autonotebook import tqdm
from scope import CWScope
from simpleserial_target import SSTargetBase
from utils import make_random_hex

# Connecting ChipWhisperer scope and target
scope = CWScope()
scope.connect(ss_version="1.1")

# Programming target
# scope.program_target("./test-CW303.hex", "XMEGA", reset_target_after_programming=True)

# Getting SimpleSerial object and printing commands
dut: SSTargetBase = scope.get_simple_serial_target()
scope.reset_target_nRST()
dut.print_simpleserial_commsnds()

# Key setting
fixed_key = "2AEF4FBF1020489FFD01F8369D353698"
dut.ss_write("k", fixed_key, ack=True)

# Initializing measurement parameters
total_trace = 100
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
    dut.ss_write('p', p, ack=False)
    c = dut.ss_read('r', 16)
    t = scope.get_waveform()
    if t is None:
        continue
    if c is None:
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
