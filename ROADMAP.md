# Roadmap

Where mainboard is headed. mainboard tells Python what compute is on the current machine —
modelling CPUs, GPUs, and NPUs as `Unit`s, keeping vendor-specific probing behind providers, and
returning the whole board in one serializable snapshot. This document tracks what works today and
what each milestone needs. It is a direction, not a contract, so order and scope can shift.

## Today (0.0.x)

The core probe works end to end.

- [x] One neutral `Unit` contract. `CPU`, `GPU`, and `NPU` share `kind`, `vendor`, and a
  `snapshot()` of clocks, memory, utilization, energy, and thermal.
- [x] Registry-based discovery. Providers self-register on import, so new silicon is new files —
  never edits to the core.
- [x] Apple and NVIDIA providers. Apple GPU + Neural Engine via `system_profiler`; NVIDIA GPU via
  CUDA/NVML telemetry.
- [x] Host probes. CPU (psutil + `sysctl`/`/proc/cpuinfo`), memory and DIMMs (dmidecode),
  motherboard + BIOS (DMI / `system_profiler`), storage, and environment.
- [x] Cross-platform identity. User, primary group, and all groups from the POSIX group database
  or Windows `whoami`, plus the job scheduler on `PATH`.
- [x] One call out. `Machine().model_dump_json()` serializes the whole machine, and `mainboard`
  renders a Rich schematic of the board.
- [x] Trustworthy. 100% statement+branch coverage (property-based with Hypothesis), CI across
  Linux, macOS, and Windows plus a self-hosted GPU runner, published to PyPI, with i18n docs and a
  generated API reference.

## v0.1.0

Make the probe complete and trustworthy across the vendors and platforms it advertises.

- [ ] **Real AMD provider.** Detect Radeon/Instinct GPUs and telemetry via ROCm/`amd-smi` — today
  AMD is an import-safe stub.
- [ ] **Real Intel provider.** Arc and integrated GPUs plus NPU via Level Zero / `xpu-smi`.
- [ ] **Real Qualcomm provider.** Adreno GPU and Hexagon NPU detection.
- [ ] **Full Windows hardware probe.** Windows reports identity today; add WMI/registry-backed CPU,
  GPU, motherboard, and DIMM detection so the snapshot matches Linux and macOS.
- [ ] **Telemetry parity.** Utilization, power/energy, and thermal for non-NVIDIA units where the
  OS exposes them (Apple via `powermetrics`/IOReport, Linux via sysfs `hwmon`).
- [ ] **Topology.** PCIe links and NUMA locality — which accelerator sits near which CPU and memory
  node.
- [ ] **Documented snapshot schema.** A field-by-field reference for `MachineSnapshot`, kept in
  sync with the models.
- [ ] **Clean LLM docs.** Fix the `llms.txt` / `llms-full.txt` generation under i18n (currently
  warns) and link them from the README.

## v1.0.0

Freeze the surface and make mainboard safe to depend on.

- [ ] **Stable snapshot schema.** A versioned JSON Schema for `MachineSnapshot`, with a written
  migration and deprecation policy.
- [ ] **Full tested parity.** CPU plus Apple, NVIDIA, AMD, Intel, and Qualcomm, on every supported
  platform.
- [ ] **Public provider API.** Promote the `Registry` so third parties add a vendor without
  touching core, documented and stable.
- [ ] **Compatibility guarantees.** Semantic versioning and a 1.x promise for the public API and
  the CLI.
- [ ] **Live telemetry.** Sample units over time, not just a point-in-time snapshot.
- [ ] **Complete reference docs** in every supported language.

## Later

Ideas worth doing once the milestones above land.

- [ ] More accelerators — Google TPU, Tenstorrent, Groq, and FPGAs.
- [ ] Remote probing — describe a machine over SSH (delegating to a dispatcher's machine clients).
- [ ] Topology export — a Graphviz/Mermaid diagram of the board.
- [ ] Exporter mode — Prometheus metrics for multi-host monitoring.
- [ ] Container awareness — what a process can actually see (cgroup/quota limits) versus the host.
