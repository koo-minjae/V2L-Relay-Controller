# V2L Relay Controller — Design Review & PCB Layout Guidelines

**Date:** July 14, 2026  
**Project:** V2L-Relay-Controller  
**Reviewer:** AI-assisted design review (Kiro)  
**Target:** Intern implementing PCB trace layout

---

## 1. Executive Summary

**Is this doable on a 2-layer PCB? Yes — but with important caveats.**

This board routes only **12V DC relay coil current** and **3.3V logic signals** on the PCB copper itself. The 120/240V AC passes through the relay contacts and exits via screw terminals — the high-voltage path is external wiring connected to the terminal blocks, not PCB traces. This makes the design fundamentally a **low-voltage (12V/3.3V) relay driver board**, which is well-suited to 2 layers.

The challenges are:
- **Large component count** (~120 parts) over a wide footprint
- **16 relay coils drawing ~40mA each** (total ~640mA on +12V bus)
- **Adequate GND return path** on a 2-layer board with many through-hole parts
- **Creepage/clearance** around the screw terminals where external 120/240V wires connect

---

## 2. Critical Design Rule Corrections (Do This First)

The current design rules have **0mm clearance** — this is invalid and will cause manufacturing failures.

| Parameter | Current Value | Required Minimum | Recommended |
|-----------|:---:|:---:|:---:|
| Copper clearance | 0 mm | 0.15 mm | **0.25 mm** |
| Min track width | 0.2 mm | 0.15 mm | 0.25 mm (signals), 0.5-1.0 mm (power) |
| Via diameter | 0.6 mm | 0.5 mm | 0.6 mm ✓ |
| Via drill | 0.3 mm | 0.25 mm | 0.3 mm ✓ |

**For screw terminal pads** (where external AC wires connect): Enforce **2.5 mm clearance** between the terminal pads and any adjacent low-voltage copper. This provides basic creepage for the external 120/240V connection points, per IPC-2221B for ≤250V working voltage.

**Action in KiCAD:**
1. Set global clearance to 0.25 mm
2. Create a net class "HV_Terminals" with 2.5 mm clearance and assign the screw terminal nets
3. Create a net class "Power_12V" with 0.5 mm track width for +12V and GND bus traces

---

## 3. Track Width Guidelines

| Net / Purpose | Current (max) | Recommended Width | Notes |
|---|:---:|:---:|---|
| AC power (screw terminal to relay contact) | **10 A** | **3.0-5.0 mm** | Highest current path! No vias, no layer changes |
| +12V bus (main spine) | ~640 mA total | **1.0 mm** | Sum of all 16 relay coils + LEDs |
| +12V branches (per relay) | ~40 mA | **0.5 mm** | Individual relay coil feed |
| GND bus (main spine) | ~640 mA return | **1.0 mm** | Use copper pour where possible |
| /SW_12V (switched 12V) | ~40 mA per switch | **0.5 mm** | Manual override supply |
| 3.3V (LDO output) | <50 mA total | **0.4 mm** | Optocoupler pull-ups + STM32 |
| Signal traces (PA/PB to MOSFETs) | <1 mA | **0.25 mm** | Logic signals, noise-tolerant |
| LED current-limiting paths | ~15 mA | **0.3 mm** | Between resistor and LED |

**Temperature Rise Rule of Thumb:** On outer copper layer (1 oz/ft²), 1mm width handles ~1A with <10°C rise. Your maximum bus current of ~640mA is well within 1mm trace capability.

---

## 4. Board Outline & Size Recommendation

Current component placement spans roughly **455mm x 165mm** — that's very large. With careful rearrangement:

**Recommended board size: 250mm x 120mm** (approximately 10" x 5")

This is achievable because:
- The 16 relay channels are repetitive subcircuits that can be packed in a regular grid
- The G5Q-1A relay footprint is ~10.7mm x 21.6mm — 16 relays in two rows of 8 takes ~180mm x 55mm
- Driver circuits (BJT + MOSFET + opto + diode + switch + LED) fit in ~15mm x 25mm per channel

If cost/size is not a concern, the current spread-out placement is fine for prototyping — just add an Edge.Cuts rectangle around the placed components with 3-5mm margin.

---

## 5. Component Placement Strategy

### Zone Layout (recommended arrangement)

```
┌─────────────────────────────────────────────────────────────┐
│  SCREW TERMINALS (top edge)                                  │
│  ─────────────────────────────────────────────────────────── │
│  RELAY ROW 1 (K19-K30, 8 relays + flyback diodes)           │
│  ─────────────────────────────────────────────────────────── │
│  DRIVER ROW 1 (BC337 + 2N7000 + opto + switch + LED x 8)    │
│  ═══════════════════════════════════════════════════════════  │
│  RELAY ROW 2 (K31-K34 + K20-K22, 8 relays + flyback diodes) │
│  ─────────────────────────────────────────────────────────── │
│  DRIVER ROW 2 (BC337 + 2N7000 + opto + switch + LED x 8)    │
│  ─────────────────────────────────────────────────────────── │
│  SCREW TERMINALS (bottom edge)                               │
│                                                              │
│  [STM32 BluePill]  [LDO + caps]  [Input connector J12/COM]  │
│  (center/right)                                              │
└─────────────────────────────────────────────────────────────┘
```

### Placement Rules

1. **Keep each relay's driver subcircuit together** — the BC337, 2N7000, optocoupler, flyback diode, switch, and LED for one relay should form a tight cluster adjacent to that relay.

2. **Screw terminals at board edges** — these carry external AC wires and need easy access for the user. Place them along the top or bottom edge with at least **5mm clearance** to any other copper.

3. **STM32 BluePill module in a central/protected location** — away from the relay coils (which generate EMI when switching). At least 15-20mm separation from the nearest relay.

4. **LDO and decoupling caps (IC1, C1, C2, C7-C10)** — place physically close to the STM32 module, with the 0.1uF caps within 5mm of the 3.3V pin.

5. **Align repetitive subcircuits** — identical relay driver circuits should have identical relative placement. This makes routing much faster (route one channel, then replicate the pattern).

6. **Switches and LEDs** — place near the board edge for user access. The slide switches (manual override) and status LEDs should face the operator.

---

## 6. Grounding Strategy (Critical for 2-Layer)

On a 2-layer board, you don't have a dedicated ground plane. This requires deliberate grounding:

1. **Use a B.Cu (back copper) ground pour** — Fill the entire back layer with a GND copper zone. This acts as a pseudo-ground-plane and provides excellent return paths.

2. **Star-ground topology for front copper:**
   - Run a thick (1.5mm) GND bus spine along the length of the board
   - Branch to each relay driver subcircuit with individual 0.5mm GND traces
   - Keep the STM32/LDO ground connected to the main bus via a short, wide trace

3. **Stitching vias** — Place GND vias every 15-20mm connecting F.Cu ground traces to the B.Cu pour. This keeps the ground return path short.

4. **Do NOT route signal traces on B.Cu if possible** — Reserve the back layer primarily for the ground pour. Only use B.Cu traces for short jumpers where absolutely necessary to avoid congestion.

5. **Separate analog/digital ground connection** — The optocoupler emitters connect to local ground. Ensure these return currents don't flow through the STM32's ground path. The star topology handles this naturally.

---

## 7. Routing Priority Order

Route in this order (highest priority first):

1. **GND connections** — tie all ground pads, then pour B.Cu ground zone
2. **+12V bus** — thick trace spine with branches to each relay coil and driver
3. **/SW_12V** — switched 12V to the manual override switches
4. **3.3V power (LDO to STM32, pull-up resistors)** — short traces near the controller
5. **Relay coil connections** — relay pin to flyback diode to BC337 collector
6. **Driver signal chain** — STM32 pin to 2N7000 gate to BC337 base / optocoupler paths
7. **LED indicator paths** — lowest priority, can tolerate longer routes
8. **Screw terminal connections** — relay contact pins to terminals (keep short and direct)

---

## 8. Specific Design Concerns & Recommendations

### A. AC Power Traces (Screw Terminal to Relay Contact)
- These traces carry **up to 10A at 120/240V AC** — they are the highest-current, highest-voltage paths on the board
- Minimum trace width: **3.0 mm** (prefer 4-5mm where space allows)
- Route **entirely on F.Cu** — no vias, no layer transitions in the AC current path
- Use **45-degree angles only** — no sharp 90° corners (current crowding + potential arc point)
- Maintain **2.5 mm clearance** to all adjacent copper (IPC-2221B creepage for 240V)
- Keep these traces as **short and direct** as possible — place each screw terminal immediately adjacent to its relay
- Consider using **copper fills/zones** instead of traces for these connections — a filled polygon between the terminal pad and relay pad handles current and heat better than a narrow trace
- Do NOT route any low-voltage signal traces between or parallel to these AC traces

### B. Flyback Diodes (D4-D28, 1N4007)
- Place each diode **directly across its relay coil pins** — within 5mm
- Route cathode to +12V and anode to relay coil with short, wide (0.5mm) traces
- The 1N4007 is through-hole (DO-41 package) — orient all diodes consistently for easy inspection

### C. Optocoupler Input/Output Isolation
- The LTV-817C provides galvanic isolation between external control signals and the relay drivers
- Keep the input side (pins 1-2, anode/cathode) traces separate from output side (pins 3-4, emitter/collector)
- Do NOT run input and output traces in parallel — maintain >=1mm separation

### D. 2N7000 MOSFET Gate Drive
- These are logic-level MOSFETs driven by the STM32 (3.3V)
- The gate traces carry essentially zero current — 0.25mm is fine
- The 10k pull-down resistors (R8-R11) should be placed close to each MOSFET gate
- Keep gate traces short to minimize noise pickup

### E. Decoupling Capacitors
- C7, C8, C9, C10 (0.1uF) and C1 (2.2uF), C2 (1uF) are for the LDO
- Place 0.1uF caps within **3-5mm** of the power pins they protect
- Route directly from cap pad to power pin, not through a via if possible

### F. Screw Terminal Clearance
- The 1729128 screw terminals handle external 120/240V AC wiring
- On the PCB, enforce **2.5mm minimum clearance** between terminal pads and adjacent copper
- Consider adding **milled slots** (cutouts in the PCB) between the terminal area and the rest of the board for enhanced creepage — though this is optional for a prototype
- Add silkscreen warnings: "DANGER: HIGH VOLTAGE" near terminals

---

## 9. Manufacturing Notes

| Parameter | Recommendation |
|---|---|
| Copper weight | 1 oz/ft² (35um) — sufficient for 640mA max |
| Board thickness | 1.6mm standard |
| Minimum hole size | 0.3mm (for vias) — already set correctly |
| Solder mask | Both sides — essential for preventing shorts |
| Silkscreen | Front side minimum; both sides recommended |
| Surface finish | HASL (leaded or lead-free) — cheapest, fine for THT |
| Panelization | Not needed for single prototype |

---

## 10. Checklist Before Routing

- [ ] Set global clearance to 0.25mm
- [ ] Create net class "Power" (track 1.0mm) and assign +12V, GND
- [ ] Create net class "HV_Terminal" (clearance 2.5mm) and assign screw terminal nets
- [ ] Draw board outline on Edge.Cuts layer
- [ ] Add 4 mounting holes (M3, corner positions)
- [ ] Verify all component footprints match physical parts
- [ ] Run DRC after placing outline (fix 0mm clearance violations)
- [ ] Place B.Cu ground pour covering full board area
- [ ] Route power bus first, then signals
- [ ] Add GND stitching vias (every 15-20mm grid)
- [ ] Run final DRC — zero errors before ordering

---

## 11. Verdict

**2-layer PCB: FEASIBLE and appropriate for this design.**

Rationale:
- No high-speed signals (relay switching is <1kHz, STM32 signals are GPIO only)
- No sensitive analog circuits
- Maximum current per trace is modest (~640mA bus, ~40mA branches)
- The AC high-voltage path is external — it passes through the relay contacts and screw terminals, not through PCB traces
- The repetitive nature of 16 identical channels makes routing systematic

The only scenario where 4 layers would be justified is if you needed much tighter board dimensions or EMC certification. For a prototype control board, 2 layers is the right choice.

---

## Component Reference Quick-Lookup

| Component Group | References | Quantity |
|---|---|:---:|
| Relays (G5Q-1A-DC12) | K19-K34 | 16 |
| Flyback diodes (1N4007) | D4-D28 | 16 |
| Relay drivers (BC337) | Q8, Q13-Q14, Q23, Q25, Q27-Q28, Q52-Q60 | 16 |
| Level shifters (2N7000) | Q6-Q7, Q9-Q10, Q15-Q18, Q26, Q29-Q31, Q40-Q43 | 16 |
| Optocouplers (LTV-817C) | Q3, Q5, Q11-Q12, Q19-Q22, Q32-Q35, Q44-Q47 | 16 |
| Screw terminals (1729128) | J5-J12, J19-J29 | 16+ |
| Slide switches (JS102011CQN) | S1, S3-S18 | 18 |
| LEDs (SML-D12M8WT86) | LED1-LED18 | 18 |
| STM32 BluePill | U1 | 1 |
| 3.3V LDO (TLV76133) | IC1 | 1 |
| Mode switch (100SP1T1B4M2QE) | S2 | 1 |
