import re
from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization fractions model, in gen-level bins
#
#   POI, for each gen bin N:  mu_N, f_LL_N, f_TL_N     (f_TT_N = 1 - f_LL_N - f_TL_N)
#
# Processes are assigned to a gen bin and a polarization state from their name suffix:
#
#     <anything>_binN_LL  ->  gen bin N, longitudinal - longitudinal
#     <anything>_binN_TL  ->  gen bin N, transverse   - longitudinal  (also "_LT" is accepted)
#     <anything>_binN_TT  ->  gen bin N, transverse   - transverse
#     anything else       ->  not scaled (background)
#
# Gen bins are found automatically in the datacard and must be N = 0, 1, ..., nGenBins-1.
#
# The templates in the datacard are the SM predictions. Each one is scaled as
#
#     N_AA_N = mu_N * f_AA_N / f_AA_N^SM * N_AA_N^SM
#
# where mu_N = sigma_N / sigma_N^SM and f_AA_N^SM are the SM polarization fractions
# in gen bin N (gen level, NOT the reco yields fractions). They must be provided,
# as comma separated lists ordered by gen bin:
#
#     --PO fLL_SM=0.05,0.06,0.08  --PO fTL_SM=0.25,0.27,0.30
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationFractionsGenBin:polarizationFractionsGenBin \
#                       --PO fLL_SM=0.05,0.06,0.08 --PO fTL_SM=0.25,0.27,0.30 -o model.root
#


def getGenBinPolarization(process):
  match = re.search(r"_bin(\d+)_(LL|TL|LT|TT)$", process)
  if match is None:
    if re.search(r"_(LL|TL|LT|TT)$", process):
      raise RuntimeError("process " + process + " has a polarization suffix but no _binN_: fix the name")
    return None, None
  pol = match.group(2)
  if pol == "LT":
    pol = "TL"
  return int(match.group(1)), pol


class PolarizationFractionsGenBin(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)
    self.fLL_SM = None
    self.fTL_SM = None

  def setPhysicsOptions(self, physOptions):
    for po in physOptions:
      if po.startswith("fLL_SM="):
        self.fLL_SM = [float(x) for x in po.replace("fLL_SM=", "").split(",")]
      if po.startswith("fTL_SM="):
        self.fTL_SM = [float(x) for x in po.replace("fTL_SM=", "").split(",")]

  def doParametersOfInterest(self):

    #
    # find the gen bins in the datacard
    #
    genBins = set()
    for process in self.DC.processes:
      genBin, pol = getGenBinPolarization(process)
      if genBin is not None:
        genBins.add(genBin)
    nGenBins = len(genBins)
    if sorted(genBins) != list(range(nGenBins)):
      raise RuntimeError("PolarizationFractionsGenBin: gen bins must be 0, ..., N-1, found " + str(sorted(genBins)))
    print (" nGenBins = ", nGenBins)

    if self.fLL_SM is None or self.fTL_SM is None:
      raise RuntimeError("PolarizationFractionsGenBin: SM fractions required, use --PO fLL_SM=x0,x1,... --PO fTL_SM=y0,y1,...")
    if len(self.fLL_SM) != nGenBins or len(self.fTL_SM) != nGenBins:
      raise RuntimeError("PolarizationFractionsGenBin: need " + str(nGenBins) + " values in fLL_SM and fTL_SM")

    pois = []
    for iBin in range(nGenBins):
      fLL_SM = self.fLL_SM[iBin]
      fTL_SM = self.fTL_SM[iBin]
      fTT_SM = 1. - fLL_SM - fTL_SM
      if fLL_SM <= 0 or fTL_SM <= 0 or fTT_SM <= 0:
        raise RuntimeError("PolarizationFractionsGenBin: SM fractions must be > 0 and sum < 1 in gen bin " + str(iBin))
      print (" gen bin ", iBin, " SM fractions: f_LL = ", fLL_SM, " f_TL = ", fTL_SM, " f_TT = ", fTT_SM)

      self.modelBuilder.doVar(f"mu_{iBin}[1,0,10]")
      self.modelBuilder.doVar(f"f_LL_{iBin}[{fLL_SM},0,1]")
      self.modelBuilder.doVar(f"f_TL_{iBin}[{fTL_SM},0,1]")

      self.modelBuilder.factory_(f'expr::scale_{iBin}_LL("@0*@1/{fLL_SM}", mu_{iBin}, f_LL_{iBin})')
      self.modelBuilder.factory_(f'expr::scale_{iBin}_TL("@0*@1/{fTL_SM}", mu_{iBin}, f_TL_{iBin})')
      self.modelBuilder.factory_(f'expr::scale_{iBin}_TT("@0*(1-@1-@2)/{fTT_SM}", mu_{iBin}, f_LL_{iBin}, f_TL_{iBin})')

      pois += [f"mu_{iBin}", f"f_LL_{iBin}", f"f_TL_{iBin}"]

    self.modelBuilder.doSet("POI", ",".join(pois))

  def getYieldScale(self, bin, process):
    genBin, pol = getGenBinPolarization(process)
    if genBin is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> scale_" + str(genBin) + "_" + pol)
    return "scale_" + str(genBin) + "_" + pol


polarizationFractionsGenBin = PolarizationFractionsGenBin()
