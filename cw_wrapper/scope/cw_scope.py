import sys
import time

import chipwhisperer as cw
import numpy as np
from typing import Optional, Dict, Union
from chipwhisperer.capture import scopes
from ..simpleserial_target import SS1xTarget, SS2xTarget, programming_target


class CWScope:
    def __init__(self):
        self._scope: Optional[cw.capture.scopes.OpenADC] = None
        self._target: Optional[cw.targets.SimpleSerial] = None
        self._ss_version: Optional[str] = None
        self._ss_target: Optional[Union[SS1xTarget, SS2xTarget]] = None
        self._prev_setting: dict = {}
        pass

    def reset(self,
              preserve_scope_setting: bool = True
              ) -> None:
        self.disconnect()
        self._scope = None
        self._target = None
        self._ss_version = None
        self._ss_target = None
        if not preserve_scope_setting:
            self._prev_setting = {}
        pass

    def connect(self,
                verbose: bool = True,
                ss_version: str = "1.1"
                ) -> None:
        assert ss_version in ("1.0", "1.1", "2.0")
        self._scope = cw.scope(scope_type=scopes.OpenADC)
        self._scope.default_setup()
        if ss_version == "2.0":
            self._target = cw.target(self._scope, target_type=cw.targets.SimpleSerial2)
            self._ss_target = SS2xTarget(self._scope, self._target)
        else:  # SimpleSerial 1.x
            self._target = cw.target(self._scope, target_type=cw.targets.SimpleSerial)
            self._ss_target = SS1xTarget(self._scope, self._target)
        if verbose:
            print(f"{self._scope.get_name()} Connected!")
        self._ss_version = ss_version
        pass

    def disconnect(self,
                   verbose: bool = True
                   ) -> None:
        if self._scope is not None:
            self._scope.dis()
            if verbose:
                print("Disconnected!")
        else:
            if verbose:
                print("scope object is None.", file=sys.stderr)
        self.reset(preserve_scope_setting=False)
        pass

    def reconnect(self,
                  verbose: bool = True,
                  preserve_scope_setting: bool = True
                  ) -> None:
        self.disconnect(verbose=verbose)
        self.connect(verbose, self._ss_version)
        if preserve_scope_setting:
            self.set_scope_detail(samples=self._prev_setting["samples"] if "samples" in self._prev_setting else None,
                                  trigger_mode=self._prev_setting["trigger_mode"] if "trigger_mode"
                                                                                     in self._prev_setting else None,
                                  offset=self._prev_setting["offset"] if "offset" in self._prev_setting else None,
                                  pre_samples=self._prev_setting["pre_samples"] if "pre_samples"
                                                                                   in self._prev_setting else None,
                                  scale=self._prev_setting["scale"] if "scale" in self._prev_setting else None)
        if verbose:
            print("Reconnected!")
        pass

    def set_scope_detail(self,
                         samples: Optional[int] = None,
                         trigger_mode: Optional[str] = None,
                         offset: Optional[int] = None,
                         pre_samples: Optional[int] = None,
                         scale: Optional[str] = None
                         ) -> None:
        if samples is not None:
            assert 0 <= samples <= 24400
            self._scope.adc.samples = samples
            self._prev_setting["samples"] = samples
        if trigger_mode is not None:
            assert trigger_mode in ("rising_edge", "falling_edge")
            self._scope.adc.basic_mode = trigger_mode
            self._prev_setting["trigger_mode"] = trigger_mode
        if offset is not None:
            assert offset >= 0
            self._scope.adc.offset = offset
            self._prev_setting["offset"] = offset
        if pre_samples is not None:
            assert pre_samples >= 0
            self._scope.adc.presamples = pre_samples
            self._prev_setting["pre_samples"] = pre_samples
        if scale is not None:
            assert scale in ("clkgen_x1", "clkgen_x4")
            self._scope.clock.adc_src = scale
            self._prev_setting["scale"] = scale
        pass

    def get_status(self,
                   verbose: bool = True
                   ) -> Dict:
        result = {
            "connected": self._scope.getStatus(),
            "name": self._scope.get_name(),
            "samples": self._scope.adc.samples,
            "trig_mode": self._scope.adc.basic_mode,
            "offset": self._scope.adc.offset,
            "pre_samples": self._scope.adc.presamples,
            "scale": self._scope.clock.adc_src,
            "last_trig_cnt": f"{self._scope.adc.trig_count}"
            if self._scope.adc.basic_mode == "rising_edge" else "unknown",
        }
        if verbose:
            print(f"-------------------------------- INFO --------------------------------\n",
                  f"Connected    : {result.get('connected')}\n",
                  f"Name         : {result.get('name')}\n",
                  f"samples      : {result.get('samples')}\n",
                  f"trig_mode    : {result.get('trig_mode')}\n",
                  f"offset       : {result.get('offset')}\n",
                  f"PreSamples   : {result.get('pre_samples')}\n",
                  f"Scale        : {result.get('scale')}\n",
                  f"LastTrigCnt  : {result.get('last_trig_cnt')}\n",
                  f"----------------------------------------------------------------------\n",
                  sep="")
        return result

    def get_last_trig_cnt(self) -> int:
        return self._scope.adc.trig_count

    def print_scope_status(self) -> None:
        print(self._scope)
        pass

    def print_target_status(self) -> None:
        print(self._target)
        pass

    def get_simple_serial_target(self) -> Union[SS1xTarget, SS2xTarget]:
        return self._ss_target

    def arm(self) -> None:
        self._scope.arm()
        pass

    def get_waveform(self) -> Optional[np.ndarray]:
        ret = self._scope.capture()
        if ret:
            print("Timeout happened during capture", file=sys.stderr)
            return None
        return self._scope.get_last_trace()

    def programming_target(self,
                           dot_hex_path: str,
                           programmer_type: str,
                           reset_target_after_programming: bool = True
                           ) -> None:
        programming_target(self._scope, dot_hex_path, programmer_type)
        if reset_target_after_programming:
            self._ss_target.reset_via_VCC()
        pass

    def reset_target_via_UFO_nRST(self, duration=0.1) -> None:
        self._ss_target.reset_via_UFO_nRST(duration)
        pass

    def reset_target_via_VCC(self, duration=0.1) -> None:
        self._ss_target.reset_via_VCC(duration)
        pass

    def set_target_clock_freq(self,
                              freq: int = 7.37e6,
                              wait_for_ready: float = 0.3,
                              verbose: bool = True
                              ) -> None:
        assert 0 <= wait_for_ready <= 10
        saved_adc_src = self._scope.clock.adc_src
        self._ss_target.set_clock_freq(freq, wait_for_ready=0)
        self._scope.clock.adc_src = saved_adc_src
        if wait_for_ready:
            time.sleep(wait_for_ready)
        if verbose:
            print(f"Adjusted sampling rate: {int(self._scope.clock.adc_freq) * 1e-6:.4f}MS/s ({saved_adc_src})")
        pass
    pass
