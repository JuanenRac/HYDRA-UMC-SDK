# Adapter boundary

This page describes the boundary a CM5-MCU or URTC adapter must respect; the SDK
itself ships no such adapter yet. An adapter's layers are transport, framing,
protocol, and service interface. The adapter
reports capabilities, state, alarms, and typed errors; it never lets a UI
write raw CAN, SPI, or UART frames.

The MCU is meant to remain authoritative for physical limits, watchdogs, and safe stop. That is a design rule: no firmware enforces limits or a safe stop yet.
Before a hardware adapter changes, test handshake, timeout, invalid sequence,
duplicate command, safety-state rejection, and recovery using a simulator and
hardware-in-the-loop where applicable.
