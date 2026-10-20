# Cryogenic DRAM Model Comparison — Preliminary Results

## Scope
These results are outputs from CryoModel/CryoMEM and its CryoMOSFET parameter generator. They are model estimates, not measurements from a physical DIMM. The 1T/3T SPICE circuits in the companion work use a generic transistor model at room temperature and are a functional circuit demonstration, not cryogenic validation.

## CryoMEM estimates

| Metric | 77 K | 4 K |
|---|---:|---:|
| t_RCD (ns) | 3.53964 | 3.51226 |
| t_RAS (ns) | 5.64935 | 5.72901 |
| t_RC (ns) | 7.74234 | 7.84487 |
| t_CAS (ns) | 6.86159 | 7.06046 |
| t_RP (ns) | 2.09299 | 2.11585 |
| t_RRD (ns) | 1.66303 | 1.72080 |
| Activation energy (nJ) | 0.507796 | 0.514117 |
| Read energy (nJ) | 1.80089 | 1.83331 |
| Write energy (nJ) | 1.80094 | 1.83336 |
| Precharge energy (nJ) | 0.221989 | 0.221990 |
| Standby leakage per bank (mW) | 2.33572 | 0.444796 |
| DRAM core area (mm²) | 134.000 | 135.945 |
| DRAM area per die (mm²) | 172.593 | 174.538 |
| Area efficiency (%) | 34.4009 | 34.0176 |

## Key interpretation
- Standby leakage per bank is approximately 80.95% lower in the 4 K run than in the 77 K run.
- Read energy is approximately 1.80% higher at 4 K.
- Timing is mixed: t_RCD is about 0.77% lower at 4 K, while t_RAS is about 1.41% higher, t_RC about 1.33% higher, and t_CAS about 2.90% higher.
- The CryoMOSFET generator reports target NMOS drive current of 3832.680 µA/µm at 77 K and 3418.772 µA/µm at 4 K; target PMOS current is 2822.540 and 2508.649 µA/µm respectively. The corresponding 300 K reference current values are 1668.144 µA/µm (NMOS) and 1233.393 µA/µm (PMOS).
- Voltage caveat: the MOSFET generator's reference uses Vdd = 0.9 V while cryogenic target runs use Vdd = 1.2 V. The drive-current ratios therefore cannot be attributed to temperature alone.
- The generator reports wire resistivity of 0.2192 µΩ·cm at 77 K and 0.2036 µΩ·cm at 4 K. Each run also emits its own 300 K reference (1.7728 and 1.7673 µΩ·cm respectively), so comparisons should be described as model outputs, not physical measurements.

## Important limitations
1. The output is model-generated, not experimental DIMM data.
2. CryoMEM passes temperature-dependent device and wire parameters into CACTI, but CACTI's own temperature handling remains configured at 300 K in this code path. Therefore avoid describing this as a fully temperature-aware physical DIMM simulation.
3. The reference and target transistor runs use different supply voltages (0.9 V vs 1.2 V), confounding a simple temperature-only interpretation.
4. The project's 1T/3T SPICE demo uses a generic Level-1 MOSFET model at room temperature; it demonstrates circuit operation only and should not be used as evidence for cryogenic behavior.
5. Authors recommend using relative comparisons rather than treating absolute values as guaranteed physical predictions.

## Suggested conclusion
Within this model configuration, cooling from 77 K to 4 K strongly reduces estimated standby leakage per bank, while timing and active energy show small mixed changes. The results suggest a potential leakage-power benefit, but the model's assumptions and validation status mean the numbers should be treated as comparative estimates, not predictions of a real DIMM's exact performance.
