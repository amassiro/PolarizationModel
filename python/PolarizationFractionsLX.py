from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization fractions model, LL and TL merged into LX
#
#   POI: mu, f_LX       (f_LX = f_LL + f_TL, f_TT = 1 - f_LX)
#
# Processes are assigned to a polarization state from their name suffix:
#
#     <anything>_LL, <anything>_TL (or _LT)  ->  LX (at least one longitudinal boson)
#     <anything>_TT                          ->  TT
#     anything else                          ->  not scaled (background)
#
# The templates in the datacard are the SM predictions. Each one is scaled as
#
#     N_LL,TL = mu * f_LX / f_LX^SM * N_LL,TL^SM
#     N_TT    = mu * (1 - f_LX) / (1 - f_LX^SM) * N_TT^SM
#
# where mu = sigma / sigma^SM and f_LX^SM is the SM fraction (where the fraction
# is measured, e.g. fiducial/gen level, NOT the reco yields fraction):
#
#     --PO fLX_SM=0.33
#
# NB: LL and TL are scaled by the same factor, i.e. their SM ratio is assumed.
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationFractionsLX:polarizationFractionsLX \
#                       --PO fLX_SM=0.33 -o model.root
#


def getPolarization(process):
  for pol in ["LL", "TL", "LT"]:
    if process.endswith("_" + pol):
      return "LX"
  if process.endswith("_TT"):
    return "TT"
  return None


class PolarizationFractionsLX(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)
    self.fLX_SM = None

  def setPhysicsOptions(self, physOptions):
    for po in physOptions:
      if po.startswith("fLX_SM="):
        self.fLX_SM = float(po.replace("fLX_SM=", ""))

  def doParametersOfInterest(self):

    if self.fLX_SM is None:
      raise RuntimeError("PolarizationFractionsLX: SM fraction required, use --PO fLX_SM=x")
    if self.fLX_SM <= 0 or self.fLX_SM >= 1:
      raise RuntimeError("PolarizationFractionsLX: fLX_SM must be in (0,1)")

    fTT_SM = 1. - self.fLX_SM
    print (" SM fractions: f_LX = ", self.fLX_SM, " f_TT = ", fTT_SM)

    self.modelBuilder.doVar("mu[1,0,10]")
    self.modelBuilder.doVar(f"f_LX[{self.fLX_SM},0,1]")

    self.modelBuilder.factory_(f'expr::scale_LX("@0*@1/{self.fLX_SM}", mu, f_LX)')
    self.modelBuilder.factory_(f'expr::scale_TT("@0*(1-@1)/{fTT_SM}", mu, f_LX)')

    self.modelBuilder.doSet("POI", "mu,f_LX")

  def getYieldScale(self, bin, process):
    pol = getPolarization(process)
    if pol is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> scale_" + pol)
    return "scale_" + pol


polarizationFractionsLX = PolarizationFractionsLX()
