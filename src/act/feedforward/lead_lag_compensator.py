# Copyright 2024 Traxton Chen
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
#
# Authors:
#   Traxton Chen <Traxton.GPG@proton.me>

from dataclasses import dataclass
from math import exp


@dataclass
class Range:
    min: float
    max: float


@dataclass
class LeadLagParam:
    gain: float
    lead: float
    lag: float


@dataclass
class NominalCondition:
    # Time
    t: float
    # Disterbance
    d: float
    # Manipulated Variable
    u: float


class LeadLag:
    def __init__(
        self,
        acceptable_d_range: tuple[float, float],
        output_u_limit: tuple[float, float],
        current_d: float,
        current_u: float,
    ):
        self.__accept_d_range = Range(*acceptable_d_range)
        self.__output_limit = Range(*output_u_limit)

        self.__param = LeadLagParam(0.0, 0.0, 0.0)
        self.__nominal_condition = NominalCondition(0.0, current_d, current_u)

    @property
    def param(self) -> tuple[float, float, float]:
        return self.__param.gain, self.__param.lead, self.__param.lag

    @param.setter
    def param(self, parameter: tuple[float, float, float]) -> None:
        self.__param.gain, self.__param.lead, self.__param.lag = parameter

    def __clip(self, value: float, upper_limit: float, lower_limit: float) -> float:
        upper_limit, lower_limit = (
            (upper_limit, lower_limit) if upper_limit >= lower_limit else (lower_limit, upper_limit)
        )
        return max(min(value, upper_limit), lower_limit)

    def __call__(
        self,
        manipulated_variable: float,
        disterbance: float,
        current_time: float,
    ) -> float:
        condition = self.__nominal_condition
        if self.__accept_d_range.min < disterbance < self.__accept_d_range.max:
            condition.t = current_time
            condition.d = disterbance
            condition.u = manipulated_variable
            return condition.u

        gain, lead, lag = self.__param.gain, self.__param.lead, self.__param.lag

        delta_d = disterbance - condition.d
        delta_t = current_time - condition.t
        lead_lag = (lead - lag) / lag * exp(-delta_t / lag)
        delta_u = gain * delta_d * (1 + lead_lag)

        return self.__clip(condition.u + delta_u, self.__output_limit.max, self.__output_limit.min)
