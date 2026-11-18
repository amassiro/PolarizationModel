import re
from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization fractions model, LL and TL merged into LX, in gen-level bins
#
#   POI, for each gen bin N:  mu_N, f_LX_N     (f_TT_N = 1 - f_LX_N)
#
# Processes are assigned to a gen bin and a polarization state from their name suffix:
#
#     <anything>_binN_LL, <anything>_binN_TL (or _LT)  ->  gen bin N, LX
#     <anything>_binN_TT                               ->  gen bin N, TT
#     anything else                                    ->  not scaled (background)
#
# Gen bins are found automatically in the datacard and must be N = 0, 1, ..., nGenBins-1.
#
# Scaling of the SM templates:
#
#     N_LL,TL_N = mu_N * f_LX_N / f_LX_N^SM * N_LL,TL_N^SM
#     N_TT_N    = mu_N * (1 - f_LX_N) / (1 - f_LX_N^SM) * N_TT_N^SM
#
# SM fractions (gen level) as comma separated list ordered by gen bin:
#
#     --PO fLX_SM=0.30,0.33,0.38
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationFractionsLXGenBin:polarizationFractionsLXGenBin \
#                       --PO fLX_SM=0.30,0.33,0.38 -o model.root
#


def getGenBinPolarization(process):
  match = re.search(r"_bin(\d+)_(LL|TL|LT|TT)$", process)
  if match is None:
    if re.search(r"_(LL|TL|LT|TT)$", process):
      raise RuntimeError("process " + process + " has a polarization suffix but no _binN_: fix the name")
    return None, None
  pol = "TT" if match.group(2) == "TT" else "LX"
  return int(match.group(1)), pol


class PolarizationFractionsLXGenBin(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)
    self.fLX_SM = None

  def setPhysicsOptions(self, physOptions):
    for po in physOptions:
      if po.startswith("fLX_SM="):
        self.fLX_SM = [float(x) for x in po.replace("fLX_SM=", "").split(",")]

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
      raise RuntimeError("PolarizationFractionsLXGenBin: gen bins must be 0, ..., N-1, found " + str(sorted(genBins)))
    print (" nGenBins = ", nGenBins)

    if self.fLX_SM is None:
      raise RuntimeError("PolarizationFractionsLXGenBin: SM fractions required, use --PO fLX_SM=x0,x1,...")
    if len(self.fLX_SM) != nGenBins:
      raise RuntimeError("PolarizationFractionsLXGenBin: need " + str(nGenBins) + " values in fLX_SM")

    pois = []
    for iBin in range(nGenBins):
      fLX_SM = self.fLX_SM[iBin]
      fTT_SM = 1. - fLX_SM
      if fLX_SM <= 0 or fLX_SM >= 1:
        raise RuntimeError("PolarizationFractionsLXGenBin: fLX_SM must be in (0,1) in gen bin " + str(iBin))
      print (" gen bin ", iBin, " SM fractions: f_LX = ", fLX_SM, " f_TT = ", fTT_SM)

      self.modelBuilder.doVar(f"mu_{iBin}[1,0,10]")
      self.modelBuilder.doVar(f"f_LX_{iBin}[{fLX_SM},0,1]")

      self.modelBuilder.factory_(f'expr::scale_{iBin}_LX("@0*@1/{fLX_SM}", mu_{iBin}, f_LX_{iBin})')
      self.modelBuilder.factory_(f'expr::scale_{iBin}_TT("@0*(1-@1)/{fTT_SM}", mu_{iBin}, f_LX_{iBin})')

      pois += [f"mu_{iBin}", f"f_LX_{iBin}"]

    self.modelBuilder.doSet("POI", ",".join(pois))

  def getYieldScale(self, bin, process):
    genBin, pol = getGenBinPolarization(process)
    if genBin is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> scale_" + str(genBin) + "_" + pol)
    return "scale_" + str(genBin) + "_" + pol


polarizationFractionsLXGenBin = PolarizationFractionsLXGenBin()
