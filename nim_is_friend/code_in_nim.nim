import nimpy

proc f(msg: string): void {.exportpy.} =
  echo msg
