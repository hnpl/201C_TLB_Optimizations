# TLB Optimizations

## Clone this repo

```sh
git clone https://github.com/takekoputa/201C_TLB_Optimizations --recursive
cd 201C_TLB_Optimizations
```

## Compile Benchmarks

### Installing Dependencies

```sh
apt-get install gcc-riscv64-linux-gnu g++-riscv64-linux-gnu
```

### Compile m5

From the project directory,

```sh
cd gem5/util/m5
scons riscv.CROSS_COMPILE=riscv64-linux-gnu- build/riscv/out/m5
```

### Compile Benchmarks

From the project directory,

```sh
./scripts/compile_benchmarks.sh
```

