# Incomplete milestone

## INPUT

The Lark device-sync project has an approved delivery criterion: the service must launch with a real local runtime configuration, and its selected network port must not collide with the companion relay. Structural checks have passed: nine tests covering configuration parsing, command construction, and service wiring are green. A worker’s receipt says the implementation is ready after those tests and names the edited launch files.

The project board also records that neither approved delivery criterion has been verified. No one has launched the service with the local runtime configuration, and no collision check has been run while the companion relay is present. These checks are executable from the current workspace and do not need product decisions. One unassigned work package owns the launch verification script and its focused test; another owns the port-selection configuration and collision-check test. Their paths are disjoint, their contracts are already approved, and both are ready to assign.

The token ledger has capacity for both packages. The goal remains active. The user has not accepted a release or waived either delivery criterion. The project manager has the worker receipt, the nine-test result, and the two ready assignments on the board.
