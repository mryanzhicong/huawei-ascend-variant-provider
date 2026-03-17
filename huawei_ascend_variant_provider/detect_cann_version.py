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
import os
import platform
import re
import sys
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

_CANN_VERSION_REGEX = re.compile(r"version="
                                 r"(?P<major>\d+)"
                                 r"\.(?P<minor>\d+)"
                                 r"(?:\.(?P<patch>\d+))?"
                                 r"(?:\.RC(?P<rc>\d+))?"
                                 r"(?:\.(?P<stage>alpha|beta)(?P<stage_ver>\d+))?", re.MULTILINE)


@dataclass(frozen=True)
class CannVersion:
    major: int = 0
    minor: int = 0
    patch: Optional[int] = None
    rc: Optional[int] = None


def get_cann_version() -> Optional[CannVersion]:
    cann_path = os.environ.get("ASCEND_TOOLKIT_HOME")
    if cann_path is None:
        logger.warning("ASCEND_TOOLKIT_HOME environment variable not set")
        return None

    arch = platform.machine() or "x86_64"
    version_file = os.path.join(cann_path, f"{arch}-linux", "ascend_toolkit_install.info")
    if not os.path.isfile(version_file):
        logger.warning("CANN version file not found: %s", version_file)
        return None

    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = _CANN_VERSION_REGEX.search(content)
    if not match:
        logger.warning("unable to parse CANN version from version file")
        return None

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch")) if match.group("patch") is not None else None
    rc = int(match.group("rc")) if match.group("rc") is not None else None
    return CannVersion(major=major, minor=minor, patch=patch, rc=rc)


def _format_cann_version(version: CannVersion) -> str:
    text = f"{version.major}.{version.minor}"
    if version.patch is not None:
        text += f".{version.patch}"
    if version.rc is not None:
        text += f".RC{version.rc}"
    return text


def _main() -> int:
    del sys.argv
    version = get_cann_version()
    if version is None:
        return 1
    print(_format_cann_version(version))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
