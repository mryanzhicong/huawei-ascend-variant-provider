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


from __future__ import annotations

import logging
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

_DRIVER_VERSION_REGEX = re.compile(r"Version:"
                                   r"\s*(?P<major>\d+)"
                                   r"\.(?P<minor>\d+)"
                                   r"(?:\.(?P<patch>\d+))?"
                                   r"(?:\.rc(?P<rc>\d+))?", re.MULTILINE)


@dataclass(frozen=True)
class DriverVersion:
    major: int = 0
    minor: int = 0
    patch: Optional[int] = None
    rc: Optional[int] = None
    stage: Optional[str] = None
    stage_ver: Optional[int] = None


@lru_cache(maxsize=1)
def _get_npu_smi_info_output() -> str:
    npu_smi_path = shutil.which("npu-smi")
    if npu_smi_path is None:
        raise RuntimeError("npu-smi command not found in PATH")

    result = subprocess.run(
        ["npu-smi", "info"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return result.stdout


def get_driver_version() -> Optional[DriverVersion]:
    try:
        output = _get_npu_smi_info_output()
    except Exception as e:
        logger.warning("failed to get npu-smi info for driver version: %s", e)
        return None

    match = _DRIVER_VERSION_REGEX.search(output)
    if not match:
        logger.warning("unable to parse driver version from npu-smi output")
        return None

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch")) if match.group("patch") is not None else None
    rc = int(match.group("rc")) if match.group("rc") is not None else None
    return DriverVersion(major=major, minor=minor, patch=patch, rc=rc)


def _format_driver_version(version: DriverVersion) -> str:
    text = f"{version.major}.{version.minor}"
    if version.patch is not None:
        text += f".{version.patch}"
    if version.rc is not None:
        text += f".rc{version.rc}"
    return text


def _main() -> int:
    del sys.argv
    version = get_driver_version()
    if version is None:
        return 1
    print(_format_driver_version(version))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
