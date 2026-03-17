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
from typing import List, Optional

from huawei_ascend_variant_provider.detect_cann_version import CannVersion, get_cann_version
from huawei_ascend_variant_provider.detect_driver_version import DriverVersion, get_driver_version
from huawei_ascend_variant_provider.detect_npu_type import get_npu_types
from huawei_ascend_variant_provider.feature_control import is_feature_disabled

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AscendEnvironment:
    driver_version: Optional[DriverVersion]
    cann_version: Optional[CannVersion]
    npu_types: List[tuple[int, str]]

    @classmethod
    @lru_cache(maxsize=1)
    def from_system(cls) -> AscendEnvironment | None:
        npu_types: List[tuple[int, str]] = []
        driver_version: Optional[DriverVersion] = None
        cann_version: Optional[CannVersion] = None

        if not is_feature_disabled("npu_type"):
            try:
                npu_types = get_npu_types()
            except Exception as e:
                logger.warning("failed to detect NPU types: %s", e)

        if not is_feature_disabled("driver_version"):
            try:
                driver_version = get_driver_version()
            except Exception as e:
                logger.warning("failed to detect driver version: %s", e)

        if not is_feature_disabled("cann_version"):
            try:
                cann_version = get_cann_version()
            except Exception as e:
                logger.warning("failed to detect CANN version: %s", e)

        if not npu_types and driver_version is None and cann_version is None:
            return None

        return cls(
            driver_version=driver_version,
            cann_version=cann_version,
            npu_types=npu_types
        )


if __name__ == "__main__":
    print(f"{AscendEnvironment.from_system()=}")
