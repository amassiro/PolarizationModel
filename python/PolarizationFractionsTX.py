from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization fractions model, TL and TT merged into TX
#
#   POI: mu, f_LL       (f_TX = f_TL + f_TT = 1 - f_LL)
#
# Processes are assigned to a polarization state from their name suffix:
#
#     <anything>_LL                          ->  LL
#     <anything>_TL (or _LT), <anything>_TT  ->  TX (at least one transverse boson)
#     anything else                          ->  not scaled (background)
#
# The templates in the datacard are the SM predictions. Each one is scaled as
#
#     N_LL    = mu * f_LL / f_LL^SM * N_LL^SM
#     N_TL,TT = mu * (1 - f_LL) / (1 - f_LL^SM) * N_TL,TT^SM
#
# where mu = sigma / sigma^SM and f_LL^SM is the SM fraction (where the fraction
# is measured, e.g. fiducial/gen level, NOT the reco yields fraction):
#
#     --PO fLL_SM=0.06
#
# NB: TL and TT are scaled by the same factor, i.e. their SM ratio is assumed.
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationFractionsTX:polarizationFractionsTX \
#                       --PO fLL_SM=0.06 -o model.root
#


def getPolarization(process):
  if process.endswith("_LL"):
    return "LL"
  for pol in ["TL", "LT", "TT"]:
    if process.endswith("_" + pol):
      return "TX"
  return None


class PolarizationFractionsTX(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)
    self.fLL_SM = None

  def setPhysicsOptions(self, physOptions):
    for po in physOptions:
      if po.startswith("fLL_SM="):
        self.fLL_SM = float(po.replace("fLL_SM=", ""))

  def doParametersOfInterest(self):

    if self.fLL_SM is None:
      raise RuntimeError("PolarizationFractionsTX: SM fraction required, use --PO fLL_SM=x")
    if self.fLL_SM <= 0 or self.fLL_SM >= 1:
      raise RuntimeError("PolarizationFractionsTX: fLL_SM must be in (0,1)")

    fTX_SM = 1. - self.fLL_SM
    print (" SM fractions: f_LL = ", self.fLL_SM, " f_TX = ", fTX_SM)

    self.modelBuilder.doVar("mu[1,0,10]")
    self.modelBuilder.doVar(f"f_LL[{self.fLL_SM},0,1]")

    self.modelBuilder.factory_(f'expr::scale_LL("@0*@1/{self.fLL_SM}", mu, f_LL)')
    self.modelBuilder.factory_(f'expr::scale_TX("@0*(1-@1)/{fTX_SM}", mu, f_LL)')

    self.modelBuilder.doSet("POI", "mu,f_LL")

  def getYieldScale(self, bin, process):
    pol = getPolarization(process)
    if pol is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> scale_" + pol)
    return "scale_" + pol


polarizationFractionsTX = PolarizationFractionsTX()
