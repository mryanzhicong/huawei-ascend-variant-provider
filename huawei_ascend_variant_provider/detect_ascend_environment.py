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
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from huawei_ascend_variant_provider.detect_cann_version import get_cann_version
from huawei_ascend_variant_provider.detect_npu_driver import get_npu_driver
from huawei_ascend_variant_provider.detect_npu_type import get_npu_type

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AscendEnvironment:
    npu_driver: Optional[str]
    cann_version: Optional[str]
    npu_type: Optional[str]

    @classmethod
    @lru_cache(maxsize=1)
    def from_system(cls) -> AscendEnvironment | None:
        npu_type: Optional[str] = None
        npu_driver: Optional[str] = None
        cann_version: Optional[str] = None

        try:
            npu_type = get_npu_type()
        except Exception as e:
            logger.warning("failed to detect NPU type: %s", e)

        try:
            npu_driver = get_npu_driver()
        except Exception as e:
            logger.warning("failed to detect NPU driver version: %s", e)

        try:
            cann_version = get_cann_version()
        except Exception as e:
            logger.warning("failed to detect CANN version: %s", e)

        if npu_type is None and npu_driver is None and cann_version is None:
            return None

        return cls(
            npu_driver=npu_driver,
            cann_version=cann_version,
            npu_type=npu_type
        )


if __name__ == "__main__":
    print(f"{AscendEnvironment.from_system()=}")
