# Roadmap

## Phase 1: Companion App

Objective:

- package the existing web-based experience into a local Windows-friendly companion app

Planning detail:

- see `docs/implementation-plan.md`

Initial milestones:

1. define packaging target and runtime behavior
2. define how shared data will be sourced from the main app repo
3. build a launcher/runtime proof of concept
4. create a repeatable Windows build flow
5. prepare Nexus-friendly packaging and documentation

Success criteria:

- a Skyrim PC user can launch the tool locally without manually setting up Python
- the app keeps the same core discovery and inventory behavior as the source app
- the output can be packaged cleanly for Nexus release

## Phase 2: In-Game Mod

Objective:

- add a narrow Skyrim-side integration layer without rewriting the whole app into Skyrim UI

Initial milestones:

1. define the smallest useful in-game feature
2. decide whether SkyUI / MCM is required
3. decide whether SKSE is required
4. document the data boundary between the companion app and the in-game layer
5. implement inventory export from a real Skyrim save
6. package the bridge with explicit dependency notes

Success criteria:

- the in-game feature has clear user value
- the implementation does not fork the domain rules silently
- the in-game scope remains maintainable
