#!/bin/sh

mkdir -p benchmarks/bin/

# Compiling GUPS
docker run -u $UID:$GID --volume $PWD:/workdir -w /workdir --rm docker.io/hnpl/gcc-rvv bash -c "cd benchmarks/gups; make -f Makefile-rvv clean; make -f Makefile-rvv M5OPS_HEADER_PATH=../../gem5/include M5_BUILD_PATH=../../gem5/util/m5/build/riscv/"
cp benchmarks/gups/gups.rvv.m5 benchmarks/bin/gups.rvv.m5

# Compiling spatter
git clone https://github.com/nlohmann/json benchmarks/json
docker run -u $UID:$GID --volume $PWD:/workdir -w /workdir --rm docker.io/hnpl/gcc-rvv bash -c "cd benchmarks/spatter; make -f Makefile-rvv clean; make -f Makefile-rvv M5OPS_HEADER_PATH=../../gem5/include M5_BUILD_PATH=../../gem5/util/m5/build/riscv/"
cp benchmarks/spatter/spatter.rvv.m5 benchmarks/bin/spatter.rvv.m5

# Compiling STREAM
docker run -u $UID:$GID --volume $PWD:/workdir -w /workdir --rm docker.io/hnpl/gcc-rvv bash -c "cd benchmarks/stream; make -f Makefile-rvv clean; make -f Makefile-rvv M5OPS_HEADER_PATH=../../gem5/include M5_BUILD_PATH=../../gem5/util/m5/build/riscv/"
cp benchmarks/stream/stream.rvv.m5 benchmarks/bin/stream.rvv.m5
