### Fixed: a push straight to main is checked too

On a push, the action now compares against the commit the branch pointed at before the push (`github.event.before`). Before, it compared `main` with itself and passed without checking anything. Add `push: { branches: [main] }` to your workflow to use it.
