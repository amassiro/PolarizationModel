from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization signal strengths model, TL and TT merged into TX
#
#   POI: mu_LL, mu_TX
#
# Processes are assigned to a polarization state from their name suffix:
#
#     <anything>_LL                          ->  scaled by mu_LL
#     <anything>_TL (or _LT), <anything>_TT  ->  scaled by mu_TX
#     anything else                          ->  not scaled (background)
#
# mu_TX = sigma_TX / sigma_TX^SM: no SM fractions needed.
# NB: TL and TT are scaled by the same factor, i.e. their SM ratio is assumed.
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationSignalStrengthsTX:polarizationSignalStrengthsTX -o model.root
#


def getPolarization(process):
  if process.endswith("_LL"):
    return "LL"
  for pol in ["TL", "LT", "TT"]:
    if process.endswith("_" + pol):
      return "TX"
  return None


class PolarizationSignalStrengthsTX(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)

  def doParametersOfInterest(self):
    self.modelBuilder.doVar("mu_LL[1,0,20]")
    self.modelBuilder.doVar("mu_TX[1,0,20]")
    self.modelBuilder.doSet("POI", "mu_LL,mu_TX")

  def getYieldScale(self, bin, process):
    pol = getPolarization(process)
    if pol is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> mu_" + pol)
    return "mu_" + pol


polarizationSignalStrengthsTX = PolarizationSignalStrengthsTX()
