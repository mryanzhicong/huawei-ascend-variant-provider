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
import sys
from typing import Optional

logger = logging.getLogger(__name__)


def _extract_cann_version_triplet(content: str) -> Optional[str]:
    for line in content.splitlines():
        text = line.strip()
        if not text.lower().startswith("version="):
            continue

        raw_version = text.split("=", 1)[1].strip()
        parts = raw_version.split(".")
        if len(parts) < 3:
            return None
        return ".".join(parts[:3])
    return None


def get_cann_version() -> Optional[str]:
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

    version = _extract_cann_version_triplet(content)
    if version is None:
        logger.warning("unable to parse CANN version from version file")
        return None
    return version


def _main() -> int:
    del sys.argv
    version = get_cann_version()
    if version is None:
        return 1
    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
