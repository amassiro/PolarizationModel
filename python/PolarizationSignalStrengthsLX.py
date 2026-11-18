from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization signal strengths model, LL and TL merged into LX
#
#   POI: mu_LX, mu_TT
#
# Processes are assigned to a polarization state from their name suffix:
#
#     <anything>_LL, <anything>_TL (or _LT)  ->  scaled by mu_LX
#     <anything>_TT                          ->  scaled by mu_TT
#     anything else                          ->  not scaled (background)
#
# mu_LX = sigma_LX / sigma_LX^SM: no SM fractions needed.
# NB: LL and TL are scaled by the same factor, i.e. their SM ratio is assumed.
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationSignalStrengthsLX:polarizationSignalStrengthsLX -o model.root
#


def getPolarization(process):
  for pol in ["LL", "TL", "LT"]:
    if process.endswith("_" + pol):
      return "LX"
  if process.endswith("_TT"):
    return "TT"
  return None


class PolarizationSignalStrengthsLX(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)

  def doParametersOfInterest(self):
    self.modelBuilder.doVar("mu_LX[1,0,20]")
    self.modelBuilder.doVar("mu_TT[1,0,20]")
    self.modelBuilder.doSet("POI", "mu_LX,mu_TT")

  def getYieldScale(self, bin, process):
    pol = getPolarization(process)
    if pol is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> mu_" + pol)
    return "mu_" + pol


polarizationSignalStrengthsLX = PolarizationSignalStrengthsLX()
