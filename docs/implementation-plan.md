# Implementation Plan

## Current Reading

The repo is intentionally a delivery repo, not the domain source of truth. The first implementation target is a packaged Windows companion app for Skyrim PC players. The Skyrim-side mod comes later and should start as a narrow integration layer, not a full rewrite of the browser app in Papyrus or SkyUI.

Authoritative domain behavior still lives in the source app repo until this repo has a shared export or shared core package.

## Guiding Constraints

- preserve ingredient, effect, source, rarity, inventory, known-effect, and discovery-scoring semantics
- do not manually recreate the ingredient dataset
- do not redefine rarity or discovery priority without documenting an explicit divergence
- isolate Skyrim-specific integration from shared domain behavior
- keep Nexus packaging practical for users who do not want to set up Python manually

## Phase 0: Baseline Import And Audit

Goal: establish a repeatable way to consume the source app baseline before building new behavior.

Status: started. The repo now has an importer, imported baseline assets, a source manifest, and a validation script.

Tasks:

1. Identify the source app repo location and commit/tag that this delivery repo targets.
2. Copy or export the authoritative baseline into `shared/` using a documented process.
3. Add a manifest that records:
   - source repo name or path
   - source commit/tag
   - files imported
   - import date
   - known divergences, if any
4. Add validation checks that compare imported data shape against expected fields.
5. Create an initial divergence log, even if it starts empty.

Deliverables:

- `shared/` contains imported domain data and source handoff docs.
- `shared/manifests/source-baseline.json` records the imported source repo, commit, source dirty state, file list, sizes, and hashes.
- `docs/source-of-truth.md` names the exact import strategy.
- `tools/import_source_baseline.py` refreshes shared assets from the source app repo.
- `tools/validate_shared_baseline.py` validates the manifest, ingredient data shape, effect ordering expectations, unique ingredient names, and rarity tier consistency.

Open decisions:

- whether this repo should vendor exported JSON files, consume a source package, or pull from a git submodule/subtree
- whether source-app Python logic can be packaged directly or must be exported into data-only artifacts

## Phase 1: Companion App

Goal: package the existing Skyrim Potion Cocktails experience into a local Windows-friendly app suitable for Nexus distribution.

Status: started. The repo now has a synced source-app runtime, local launcher, dependency metadata, initial PyInstaller packaging notes, and a maintainer build command.

### Milestone 1: Runtime Shape

Choose the companion-app delivery shape:

- local bundled web app with an embedded backend
- desktop shell around the existing app
- static/exported frontend plus local data files, if the app can function without server behavior

Preferred starting assumption: bundle the existing app with a small launcher so users do not manually install Python.

Tasks:

1. Inspect the source app runtime requirements.
2. Decide whether to reuse FastAPI directly, wrap it, or export static assets.
3. Define the local port, startup behavior, shutdown behavior, and browser-opening behavior.
4. Document where user state is stored, such as inventory and known effects.

Deliverables:

- `companion_app/` contains a launcher proof of concept and runtime notes.
- Runtime behavior is documented for development and packaged builds.

### Milestone 2: Shared Data Boundary

Define what crosses from the authoritative source app into this repo.

Tasks:

1. Import or reference ingredient data.
2. Import or reference rarity behavior.
3. Import or reference discovery-scoring behavior.
4. Add smoke tests or validation scripts for the imported baseline.
5. Document any companion-app-specific state storage format.

Deliverables:

- shared assets are not rebuilt by hand
- discovery and rarity semantics can be verified after import
- companion app state is separated from source baseline data

### Milestone 3: Windows Build

Create a repeatable build flow for users.

Tasks:

1. Choose packaging tooling, likely PyInstaller, Briefcase, Tauri, Electron, or a zip-based local runtime depending on source app shape.
2. Produce a first Windows build artifact.
3. Verify launch from a clean machine or VM-like environment.
4. Add release packaging notes for Nexus.

Deliverables:

- one-command build path for maintainers
- distributable zip or installer candidate
- user-facing launch instructions

### Milestone 4: Nexus Readiness

Prepare release material without expanding scope.

Tasks:

1. Add installation instructions.
2. Add uninstall and data-location notes.
3. Add compatibility notes for Skyrim editions, even if the companion app is edition-independent.
4. Add troubleshooting for blocked ports, antivirus warnings, and local state reset.

Deliverables:

- Nexus-ready archive structure
- README section aimed at players rather than developers

## Phase 2: Narrow Skyrim Mod Integration

Goal: provide a small in-game feature that complements the companion app without forking domain rules.

Initial candidate features, from smallest to largest:

1. In-game book or note that points users to the companion app and explains the workflow.
2. MCM page with companion-app status/help and configurable export/import paths.
3. Lightweight inventory export from Skyrim to companion app.
4. Known-effects export/import bridge.
5. In-game notification or lookup helper for selected ingredient combinations.

Recommended first useful feature: inventory export or known-effects export, because it gives practical value while keeping the heavy discovery logic in the companion app.

Tasks:

1. Decide whether the first feature needs SkyUI/MCM.
2. Decide whether SKSE is required for file I/O or integration.
3. Define the data exchange format between Skyrim and the companion app.
4. Keep Papyrus scripts thin and data-oriented.
5. Document every divergence caused by Creation Kit, Papyrus, SkyUI, or SKSE limits.

Deliverables:

- `skyrim_mod/` contains source assets or documented Creation Kit project structure.
- Data boundary is explicit and does not duplicate discovery scoring in Papyrus.
- The mod can be packaged independently from the companion app if needed.

## Proposed Repository Structure

```text
companion_app/
  launcher/
  packaging/
  README.md
shared/
  data/
  manifests/
  validation/
skyrim_mod/
  scripts/
  source/
  packaging/
docs/
  implementation-plan.md
  roadmap.md
  source-of-truth.md
  divergences.md
```

## Immediate Next Steps

1. Decide whether the current copied-file import strategy is sufficient, or whether the source app should provide an explicit export package later.
2. Keep `docs/divergences.md` updated as soon as any source-app behavior changes for packaging, UX, or Skyrim engine reasons.
3. Produce and test the first Windows PyInstaller build.
4. Add release archive hashes and versioning once a Windows artifact exists.
