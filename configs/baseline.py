# Copyright (c) 2023 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from gem5.resources.resource import Resource, CustomResource
from gem5.simulate.simulator import Simulator
from gem5.components.boards.simple_board import SimpleBoard
from gem5.isas import ISA
from gem5.utils.requires import requires
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.simple_switchable_processor import SimpleSwitchableProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.resources.workload import CustomWorkload
from gem5.simulate.exit_event import ExitEvent
import m5

import argparse
parser = argparse.ArgumentParser("Configuration for the baseline system.")
parser.add_argument("--binary-path", type=str, required=True, help="Binary to run.")
parser.add_argument("--binary-args", type=str, required=True, nargs="+", help="Arguments to be supplied to the binary.")
args = parser.parse_args()
binary_path = args.binary_path
binary_args = args.binary_args

requires(isa_required=ISA.RISCV)

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32KiB", l1i_size="32KiB", l2_size="512KiB"
)

memory = DualChannelDDR4_2400(size="16GiB")

processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.ATOMIC,
    switch_core_type=CPUTypes.TIMING,
    isa=ISA.RISCV,
    num_cores=1
)

board = SimpleBoard(
    clk_freq = "4GHz",
    processor = processor,
    memory = memory,
    cache_hierarchy = cache_hierarchy
)

board.set_workload(CustomWorkload(
    function = "set_se_binary_workload",
    parameters = {
        "binary" : CustomResource(binary_path),
        "arguments" : binary_args
    }
))

def print_info(message):
    bold = '\033[1m'
    color = '\033[32m'
    nocolor = '\033[0m'
    print(f"{color}{bold}info: {message} {nocolor}")

def handle_work_begin():
    print_info("Exit due to m5_work_begin()")
    print_info("Resetting stats")
    m5.stats.reset()
    print_info("Switching CPU")
    processor.switch()
    yield False

def handle_work_end():
    print_info("Exit due to m5_work_end()")
    print_info("Dumping stats")
    m5.stats.dump()
    yield False

def handle_exit():
    print_info("Exit due to m5_exit()")
    yield True

# run the simulation with the RISCV Matched board
simulator = Simulator(
    board=board, full_system=False,
    on_exit_event={
        ExitEvent.WORKBEGIN: handle_work_begin(),
        ExitEvent.WORKEND: handle_work_end(),
        ExitEvent.EXIT: handle_exit()
    }
)
simulator.run()
