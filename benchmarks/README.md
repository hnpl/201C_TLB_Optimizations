# Benchmarks

Modified from
[https://github.com/darchr/simple-vectorizable-benchmarks](https://github.com/darchr/simple-vectorizable-benchmarks).

# Compile Benchmarks

## Installing Dependencies

```sh
apt-get install gcc-riscv64-linux-gnu g++-riscv64-linux-gnu
```

## Compile m5

From the project directory,

```sh
cd gem5/util/m5
scons riscv.CROSS_COMPILE=riscv64-linux-gnu- build/riscv/out/m5
```

## Compile Benchmarks

From the project directory,

```sh
./compile_benchmarks.sh
```
