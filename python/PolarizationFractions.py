from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization fractions model
#
#   POI: mu, f_LL, f_TL       (f_TT = 1 - f_LL - f_TL)
#
# Processes are assigned to a polarization state from their name suffix:
#
#     <anything>_LL  ->  longitudinal - longitudinal
#     <anything>_TL  ->  transverse   - longitudinal  (also "_LT" is accepted)
#     <anything>_TT  ->  transverse   - transverse
#     anything else  ->  not scaled (background)
#
# The templates in the datacard are the SM predictions. Each one is scaled as
#
#     N_AA = mu * f_AA / f_AA^SM * N_AA^SM
#
# where mu = sigma / sigma^SM and f_AA^SM are the SM polarization fractions
# (defined where the fractions are measured, e.g. fiducial/gen level, NOT the
# fractions of the reco yields in the datacard: efficiencies differ for the
# three states). They must be provided:
#
#     --PO fLL_SM=0.06  --PO fTL_SM=0.27
#
# With mu = 1 and f_AA = f_AA^SM the SM prediction is recovered.
#
# NB: f_LL and f_TL are in [0,1], but f_LL + f_TL > 1 gives negative TT yields:
#     restrict the ranges if needed (--setParameterRanges)
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationFractions:polarizationFractions \
#                       --PO fLL_SM=0.06 --PO fTL_SM=0.27 -o model.root
#


def getPolarization(process):
  for pol in ["LL", "TL", "TT"]:
    if process.endswith("_" + pol):
      return pol
  if process.endswith("_LT"):
    return "TL"
  return None


class PolarizationFractions(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)
    self.fLL_SM = None
    self.fTL_SM = None

  def setPhysicsOptions(self, physOptions):
    for po in physOptions:
      if po.startswith("fLL_SM="):
        self.fLL_SM = float(po.replace("fLL_SM=", ""))
      if po.startswith("fTL_SM="):
        self.fTL_SM = float(po.replace("fTL_SM=", ""))

  def doParametersOfInterest(self):

    if self.fLL_SM is None or self.fTL_SM is None:
      raise RuntimeError("PolarizationFractions: SM fractions required, use --PO fLL_SM=x --PO fTL_SM=y")

    fTT_SM = 1. - self.fLL_SM - self.fTL_SM
    if self.fLL_SM <= 0 or self.fTL_SM <= 0 or fTT_SM <= 0:
      raise RuntimeError("PolarizationFractions: SM fractions must be > 0 and sum < 1")

    print (" SM fractions: f_LL = ", self.fLL_SM, " f_TL = ", self.fTL_SM, " f_TT = ", fTT_SM)

    self.modelBuilder.doVar("mu[1,0,10]")
    self.modelBuilder.doVar(f"f_LL[{self.fLL_SM},0,1]")
    self.modelBuilder.doVar(f"f_TL[{self.fTL_SM},0,1]")

    self.modelBuilder.factory_(f'expr::scale_LL("@0*@1/{self.fLL_SM}", mu, f_LL)')
    self.modelBuilder.factory_(f'expr::scale_TL("@0*@1/{self.fTL_SM}", mu, f_TL)')
    self.modelBuilder.factory_(f'expr::scale_TT("@0*(1-@1-@2)/{fTT_SM}", mu, f_LL, f_TL)')

    self.modelBuilder.doSet("POI", "mu,f_LL,f_TL")

  def getYieldScale(self, bin, process):
    pol = getPolarization(process)
    if pol is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> scale_" + pol)
    return "scale_" + pol


polarizationFractions = PolarizationFractions()
