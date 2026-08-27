# Adapter boundary

The SDK provides high-level adapters for CM5-MCU and URTC integration. Their
layers are transport, framing, protocol, and service interface. The adapter
reports capabilities, state, alarms, and typed errors; it never lets a UI
write raw CAN, SPI, or UART frames.

The MCU remains authoritative for physical limits, watchdogs, and safe stop.
Before a hardware adapter changes, test handshake, timeout, invalid sequence,
duplicate command, safety-state rejection, and recovery using a simulator and
hardware-in-the-loop where applicable.
