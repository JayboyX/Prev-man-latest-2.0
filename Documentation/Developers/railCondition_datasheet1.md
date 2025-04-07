**Railway Track Condition Data Sheet**

| Factor Name | Description | Units | Range (Approximate) | Notes |
|---|---|---|---|---|
| `crw_l` | Left Rail Corrugation Wear | Units related to weight (e.g., kN or a normalized unit) | 1.0 to 2.0 * (total weight / 100) | Indicates the level of wear or roughness on the left rail surface. Higher values suggest more significant corrugation. |
| `crw_r` | Right Rail Corrugation Wear | Units related to weight (e.g., kN or a normalized unit) | 1.0 to 2.0 * (total weight / 100) | Indicates the level of wear or roughness on the right rail surface. Higher values suggest more significant corrugation. |
| `side_l` | Left Rail Side Wear | Units related to weight (e.g., kN or a normalized unit) | 0.5 to 1.5 * (total weight / 100) | Measures the wear on the side of the left rail. Higher values indicate more lateral wear. |
| `side_r` | Right Rail Side Wear | Units related to weight (e.g., kN or a normalized unit) | 0.5 to 1.5 * (total weight / 100) | Measures the wear on the side of the right rail. Higher values indicate more lateral wear. |
| `remlife_l` | Remaining Left Rail Lifespan | Units inversely related to weight (e.g., cycles/kN or a normalized unit) | 100.0 to 200.0 / (total weight / 100) | Represents the estimated remaining lifespan of the left rail before needing replacement. Lower values indicate less remaining life. |
| `remlife_r` | Remaining Right Rail Lifespan | Units inversely related to weight (e.g., cycles/kN or a normalized unit) | 100.0 to 200.0 / (total weight / 100) | Represents the estimated remaining lifespan of the right rail before needing replacement. Lower values indicate less remaining life. |
| `wid_l` | Left Rail Head Width | Millimeters (mm) | 50.0 to 60.0 | Measures the width of the left rail's head. Reduction in width indicates wear. |
| `wid_r` | Right Rail Head Width | Millimeters (mm) | 50.0 to 60.0 | Measures the width of the right rail's head. Reduction in width indicates wear. |
| `tiltdiff_l` | Left Rail Tilt Difference | Units related to speed (e.g., degrees/100km/h) | 0.1 to 0.5 * (base speed / 100) | Indicates the difference in tilt or cant of the left rail. Higher values suggest more significant misalignment. |
| `tiltdiff_r` | Right Rail Tilt Difference | Units related to speed (e.g., degrees/100km/h) | 0.1 to 0.5 * (base speed / 100) | Indicates the difference in tilt or cant of the right rail. Higher values suggest more significant misalignment. |
| `type_l` | Left Rail Type/Material Hardness | Hardness scale or arbitrary units | 40.0 to 60.0 | Represents the material type or hardness of the left rail. Higher values might indicate harder materials. |
| `type_r` | Right Rail Type/Material Hardness | Hardness scale or arbitrary units | 40.0 to 60.0 | Represents the material type or hardness of the right rail. Higher values might indicate harder materials. |
| `gaugediff` | Gauge Difference | Units related to weight (e.g., mm/kN or a normalized unit) | 0.0 to 1.0 * (total weight / 100) | Measures the variation in the track gauge (distance between rails). Higher values indicate greater deviation from the standard gauge. |
