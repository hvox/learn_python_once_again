import std/strformat

proc f(p1: ptr uint8, p2: ptr UncheckedArray[uint8]): int {.exportc, cdecl, dynlib.} =
  echo fmt"addr: 0x{cast[uint64](p2):x}"
  let delta = cast[uint64](p2) - cast[uint64](p1)
  echo fmt"delta: 0x{delta:x}"
  for i in 0..4:
    echo fmt"array[{i}] = {p2[i]}"
    p2[i] += 1
