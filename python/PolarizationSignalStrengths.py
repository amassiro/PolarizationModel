from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization signal strengths model
#
#   POI: mu_LL, mu_TL, mu_TT
#
# Processes are assigned to a polarization state from their name suffix:
#
#     <anything>_LL  ->  scaled by mu_LL
#     <anything>_TL  ->  scaled by mu_TL  (also "_LT" is accepted)
#     <anything>_TT  ->  scaled by mu_TT
#     anything else  ->  not scaled (background)
#
# mu_AA = sigma_AA / sigma_AA^SM: no SM fractions needed.
# Equivalent to PolarizationFractions with mu_AA = mu * f_AA / f_AA^SM.
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationSignalStrengths:polarizationSignalStrengths -o model.root
#


def getPolarization(process):
  for pol in ["LL", "TL", "TT"]:
    if process.endswith("_" + pol):
      return pol
  if process.endswith("_LT"):
    return "TL"
  return None


class PolarizationSignalStrengths(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)

  def doParametersOfInterest(self):
    self.modelBuilder.doVar("mu_LL[1,0,20]")
    self.modelBuilder.doVar("mu_TL[1,0,20]")
    self.modelBuilder.doVar("mu_TT[1,0,20]")
    self.modelBuilder.doSet("POI", "mu_LL,mu_TL,mu_TT")

  def getYieldScale(self, bin, process):
    pol = getPolarization(process)
    if pol is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> mu_" + pol)
    return "mu_" + pol


polarizationSignalStrengths = PolarizationSignalStrengths()
