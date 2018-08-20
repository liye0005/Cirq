# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool to benchmark the xmon_simulator."""

import timeit
from typing import Any, Dict, List, Tuple  # pylint: disable=unused-import

import numpy as np
from absl import app
from absl import flags

from cirq import Circuit
from cirq.google import ExpZGate, ExpWGate, Exp11Gate

FLAGS = flags.FLAGS

flags.DEFINE_integer('min_num_qubits', 4,
                     'Lower range (inclusive) of number of qubits that will '
                     'be benchmarked.')
flags.DEFINE_integer('max_num_qubits', 26,
                     'Upper range (inclusive) of number of qubits that will '
                     'be benchmarked.')
flags.DEFINE_integer('num_gates', 100, 'The number of gates in the benchmark.')
flags.DEFINE_integer('num_repetitions', 10,
                     'The number of times to average the benchmark over.')


def simulate(num_qubits: int, num_gates: int) -> None:
    """"Runs the xmon_simulator."""
    circuit = Circuit()
    for _ in range(num_gates):
        which = np.random.choice(['expz', 'expw', 'exp11'])

        if which == 'expw':
            circuit.insert(ExpWGate(axis_half_turns=np.random.random(),
                                    half_turns=np.random.random()).on(
                np.random.randint(num_qubits)))
        elif which == 'expz':
            ops.append(('expz',
                        np.random.randint(num_qubits),
                        np.random.random()))
        elif which == 'exp11':
            ops.append(('exp11', np.random.randint(num_qubits),
                        np.random.randint(num_qubits),
                        np.random.random()))

    current_moment = num_qubits * [0]
    moments = [[]]  # type: List[List[Any]]

    for op in ops:
        if op[0] == 'expw' or op[0] == 'expz':
            index = op[1]
            new_moment = current_moment[index]
            if len(moments) == new_moment:
                moments.append([])
            moments[new_moment].append(op)
            current_moment[index] = new_moment + 1
        elif op[0] == 'exp11':
            index0 = op[1]
            index1 = op[2]
            new_moment = max(current_moment[index0], current_moment[index1])
            if len(moments) == new_moment:
                moments.append([])
            moments[new_moment].append(op)
            current_moment[index0] = new_moment + 1
            current_moment[index1] = new_moment + 1

    circuit = Circuit(moments)
    circuit.apply_unitary_effect_to_state()

def main(argv):
    setup = argv[1] if len(argv) == 2 else 'from __main__ import simulate'
    print('num_qubits,seconds per gate')
    for num_qubits in range(FLAGS.min_num_qubits, FLAGS.max_num_qubits + 1):
        command = 'simulate(%s, %s)' % (num_qubits, FLAGS.num_gates)
        time = timeit.timeit(command, setup, number=FLAGS.num_repetitions)
        print('{},{}'.format(num_qubits,
                             time / (FLAGS.num_repetitions * FLAGS.num_gates)))


if __name__ == '__main__':
    app.run(main)
