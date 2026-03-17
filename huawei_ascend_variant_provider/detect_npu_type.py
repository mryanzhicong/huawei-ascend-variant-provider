# Copyright (c) 2025 Huawei Technologies Co., Ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/usr/bin/env python3


import ctypes
import sys
from enum import Enum, IntEnum
from functools import lru_cache
from typing import Dict, List, Tuple


class SocVersion(IntEnum):
    UnsupportedSocVersion = -1
    Ascend910PremiumA = 100
    Ascend910ProA = 101
    Ascend910A = 102
    Ascend910ProB = 103
    Ascend910B = 104
    Ascend310P1 = 200
    Ascend310P2 = 201
    Ascend310P3 = 202
    Ascend310P4 = 203
    Ascend310P5 = 204
    Ascend310P7 = 205
    Ascend910B1 = 220
    Ascend910B2 = 221
    Ascend910B2C = 222
    Ascend910B3 = 223
    Ascend910B4 = 224
    Ascend910B4_1 = 225
    Ascend310B1 = 240
    Ascend310B2 = 241
    Ascend310B3 = 242
    Ascend310B4 = 243
    Ascend910_9391 = 250
    Ascend910_9392 = 251
    Ascend910_9381 = 252
    Ascend910_9382 = 253
    Ascend910_9372 = 254
    Ascend910_9362 = 255
    Ascend950 = 260


class AscendDeviceType(Enum):
    A2 = "a2"
    A3 = "a3"
    _310P = "310p"
    A5 = "a5"


SOC_NAME_TO_VERSION: Dict[str, SocVersion] = {
    "Ascend910PremiumA": SocVersion.Ascend910PremiumA,
    "Ascend910ProA": SocVersion.Ascend910ProA,
    "Ascend910A": SocVersion.Ascend910A,
    "Ascend910ProB": SocVersion.Ascend910ProB,
    "Ascend910B": SocVersion.Ascend910B,
    "Ascend310P1": SocVersion.Ascend310P1,
    "Ascend310P2": SocVersion.Ascend310P2,
    "Ascend310P3": SocVersion.Ascend310P3,
    "Ascend310P4": SocVersion.Ascend310P4,
    "Ascend310P5": SocVersion.Ascend310P5,
    "Ascend310P7": SocVersion.Ascend310P7,
    "Ascend910B1": SocVersion.Ascend910B1,
    "Ascend910B2": SocVersion.Ascend910B2,
    "Ascend910B2C": SocVersion.Ascend910B2C,
    "Ascend910B3": SocVersion.Ascend910B3,
    "Ascend910B4": SocVersion.Ascend910B4,
    "Ascend910B4-1": SocVersion.Ascend910B4_1,
    "Ascend310B1": SocVersion.Ascend310B1,
    "Ascend310B2": SocVersion.Ascend310B2,
    "Ascend310B3": SocVersion.Ascend310B3,
    "Ascend310B4": SocVersion.Ascend310B4,
    "Ascend910_9391": SocVersion.Ascend910_9391,
    "Ascend910_9392": SocVersion.Ascend910_9392,
    "Ascend910_9381": SocVersion.Ascend910_9381,
    "Ascend910_9382": SocVersion.Ascend910_9382,
    "Ascend910_9372": SocVersion.Ascend910_9372,
    "Ascend910_9362": SocVersion.Ascend910_9362,
    "Ascend950": SocVersion.Ascend950,
}

# (min_soc_version, max_soc_version, device_type)
SOC_VERSION_RANGES_TO_DEVICE_TYPE: List[Tuple[int, int, str]] = [
    (220, 225, AscendDeviceType.A2.value),      # [220, 225] -> "a2"
    (250, 255, AscendDeviceType.A3.value),      # [250, 255] -> "a3"
    (200, 205, AscendDeviceType._310P.value),   # [200, 205] -> "310p"
    (260, 260, AscendDeviceType.A5.value),      # [260, 260] -> "a5"
]


def _load_acl_lib() -> ctypes.CDLL:
    try:
        return ctypes.CDLL("libascendcl.so")
    except OSError as exc:
        raise RuntimeError("ACL runtime library not found") from exc


@lru_cache(maxsize=1)
def _get_aclrt_get_soc_name():
    lib = _load_acl_lib()
    try:
        get_soc_name = lib.aclrtGetSocName
    except AttributeError as exc:
        raise RuntimeError("aclrtGetSocName symbol not found in ACL runtime library") from exc

    get_soc_name.restype = ctypes.c_char_p
    get_soc_name.argtypes = []
    return get_soc_name


def detect_soc_name() -> str:
    get_soc_name = _get_aclrt_get_soc_name()
    result = get_soc_name()
    if not result:
        raise RuntimeError("aclrtGetSocName returned empty/null")
    return result.decode("utf-8")


def get_soc_version() -> int:
    soc_name = detect_soc_name()
    return int(SOC_NAME_TO_VERSION.get(soc_name, SocVersion.UnsupportedSocVersion))


def _map_soc_version_to_device_type(soc_version: int) -> str:
    for min_version, max_version, device_type in SOC_VERSION_RANGES_TO_DEVICE_TYPE:
        if min_version <= soc_version <= max_version:
            return device_type
    return ""


def get_ascend_device_type() -> str:
    soc_version = get_soc_version()
    device_type = _map_soc_version_to_device_type(soc_version)
    if device_type:
        return device_type
    raise RuntimeError(f"Can not support soc_version: {soc_version}.")


@lru_cache(maxsize=1)
def probe_soc_name() -> str:
    """Lightweight probe API for plugin use. Returns empty string on failure."""
    try:
        return detect_soc_name()
    except Exception:
        return ""


@lru_cache(maxsize=1)
def probe_soc_version(default: int = int(SocVersion.UnsupportedSocVersion)) -> int:
    """Lightweight probe API for plugin use. Returns default on failure."""
    soc_name = probe_soc_name()
    if not soc_name:
        return int(default)
    return int(SOC_NAME_TO_VERSION.get(soc_name, default))


@lru_cache(maxsize=1)
def probe_ascend_device_type(default: str = "") -> str:
    """Lightweight probe API for plugin use. Returns default on failure."""
    soc_version = probe_soc_version()
    device_type = _map_soc_version_to_device_type(soc_version)
    return device_type or default


@lru_cache(maxsize=1)
def get_npu_types() -> List[tuple[int, str]]:
    """Unified NPU type API used by environment detection."""
    npu_type = probe_ascend_device_type(default="")
    if not npu_type:
        return []
    return [(0, npu_type)]


def _main() -> int:
    del sys.argv
    device_type = probe_ascend_device_type(default="")
    if not device_type:
        return 1
    print(device_type)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
