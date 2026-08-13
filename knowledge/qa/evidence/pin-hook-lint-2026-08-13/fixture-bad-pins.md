# Fixture: bad pins for C1 warn-first verification

**Type:** Executable
**Project:** bellows
**dispatch_mode:** bellows
**pause_for_verdict:** always
**cycle_tier:** T0

---

## Body

M2 exercise — wrong sha256 for a real file:

`shasum -a 256 /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py`
0000000000000000000000000000000000000000000000000000000000000000

M1 exercise — unresolvable git object in plain prose:

Verify via git -C /Users/marklehn/Developer/GitHub/bellows cat-file -e ffffffffffffffffffffffffffffffffffffffff — this object does not exist.
