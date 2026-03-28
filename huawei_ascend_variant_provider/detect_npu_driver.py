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
import shutil
import subprocess
import sys
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _get_npu_smi_version_output() -> str:
    npu_smi_path = shutil.which("npu-smi")
    if npu_smi_path is None:
        raise RuntimeError("npu-smi command not found in PATH")

    result = subprocess.run(
        ["npu-smi", "-v"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return result.stdout


def _extract_version_triplet(output: str) -> Optional[str]:
    for line in output.splitlines():
        text = line.strip()
        if not text.lower().startswith("npu-smi version:"):
            continue

        raw_version = text.split(":", 1)[1].strip()
        parts = raw_version.split(".")
        if len(parts) < 3:
            return None

        return ".".join(parts[:3])
    return None


def get_npu_driver() -> Optional[str]:
    try:
        output = _get_npu_smi_version_output()
    except Exception as e:
        logger.warning("failed to get npu-smi -v output for driver version: %s", e)
        return None

    version = _extract_version_triplet(output)
    if version is None:
        logger.warning("unable to parse driver version from npu-smi -v output")
        return None
    return version


def _main() -> int:
    del sys.argv
    version = get_npu_driver()
    if version is None:
        return 1
    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
