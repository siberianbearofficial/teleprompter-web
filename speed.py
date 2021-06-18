def toSpeedValue (speedGot):
  return int(((100 - speedGot) / 100) * 49 + 1)

def toPercentValue (speedGot):
  return 100 - int((speedGot - 1) / 49 * 100)