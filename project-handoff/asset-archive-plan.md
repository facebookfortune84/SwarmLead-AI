# Asset Archive Plan

**Date:** 2026-07-26

---

## Active Assets (KEEP)

| Path | Size | Purpose | Referenced By |
|---|---|---|---|
| `assets/raw/archetype_registry.json` | — | Registry mapping archetypes→DNA files | `AssetOptimizer` |
| `assets/raw/archetype_classification_report.json` | — | Classification scores per archetype | `AssetOptimizer` |
| `assets/raw/agent_registry.json` | — | Agent identity registry | `AssetOptimizer` |
| `assets/optimized/optimized_archetypes.json` | — | Processed archetype data for runtime | `AssetLoader` |
| `assets/optimized/archetype_weights.json` | — | Weight configuration | Unknown |
| `asset_processor/output/archetypes/` | 58 files, 112KB | DNA prompt files (source for asset optimizer) | `assets/raw/archetype_registry.json` references these |

## Asset Pipeline

```
asset_processor/output/archetypes/*.json   (source DNA prompt files)
    ↓
AssetOptimizer reads via archetype_registry.json
    ↓
assets/optimized/optimized_archetypes.json  (runtime consumable)
    ↓
AssetLoader loads at runtime
```

## Recommendation

**KEEP all assets.** The `asset_processor/` directory is a build-time dependency for the asset optimization pipeline. Although it's not directly referenced at runtime, it's the source of truth for agent prompt definitions. The 58 files (112KB) are small enough to keep without impact.

**Do not archive to D:\**. The archive would break the asset pipeline because `archetype_registry.json` references `asset_processor/output/archetypes/` using relative paths. Moving these files would require updating the registry.
