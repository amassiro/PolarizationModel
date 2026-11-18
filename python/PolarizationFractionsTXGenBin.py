import re
from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization fractions model, TL and TT merged into TX, in gen-level bins
#
#   POI, for each gen bin N:  mu_N, f_LL_N     (f_TX_N = 1 - f_LL_N)
#
# Processes are assigned to a gen bin and a polarization state from their name suffix:
#
#     <anything>_binN_LL                               ->  gen bin N, LL
#     <anything>_binN_TL (or _LT), <anything>_binN_TT  ->  gen bin N, TX
#     anything else                                    ->  not scaled (background)
#
# Gen bins are found automatically in the datacard and must be N = 0, 1, ..., nGenBins-1.
#
# Scaling of the SM templates:
#
#     N_LL_N    = mu_N * f_LL_N / f_LL_N^SM * N_LL_N^SM
#     N_TL,TT_N = mu_N * (1 - f_LL_N) / (1 - f_LL_N^SM) * N_TL,TT_N^SM
#
# SM fractions (gen level) as comma separated list ordered by gen bin:
#
#     --PO fLL_SM=0.05,0.06,0.08
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationFractionsTXGenBin:polarizationFractionsTXGenBin \
#                       --PO fLL_SM=0.05,0.06,0.08 -o model.root
#


def getGenBinPolarization(process):
  match = re.search(r"_bin(\d+)_(LL|TL|LT|TT)$", process)
  if match is None:
    if re.search(r"_(LL|TL|LT|TT)$", process):
      raise RuntimeError("process " + process + " has a polarization suffix but no _binN_: fix the name")
    return None, None
  pol = "LL" if match.group(2) == "LL" else "TX"
  return int(match.group(1)), pol


class PolarizationFractionsTXGenBin(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)
    self.fLL_SM = None

  def setPhysicsOptions(self, physOptions):
    for po in physOptions:
      if po.startswith("fLL_SM="):
        self.fLL_SM = [float(x) for x in po.replace("fLL_SM=", "").split(",")]

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
      raise RuntimeError("PolarizationFractionsTXGenBin: gen bins must be 0, ..., N-1, found " + str(sorted(genBins)))
    print (" nGenBins = ", nGenBins)

    if self.fLL_SM is None:
      raise RuntimeError("PolarizationFractionsTXGenBin: SM fractions required, use --PO fLL_SM=x0,x1,...")
    if len(self.fLL_SM) != nGenBins:
      raise RuntimeError("PolarizationFractionsTXGenBin: need " + str(nGenBins) + " values in fLL_SM")

    pois = []
    for iBin in range(nGenBins):
      fLL_SM = self.fLL_SM[iBin]
      fTX_SM = 1. - fLL_SM
      if fLL_SM <= 0 or fLL_SM >= 1:
        raise RuntimeError("PolarizationFractionsTXGenBin: fLL_SM must be in (0,1) in gen bin " + str(iBin))
      print (" gen bin ", iBin, " SM fractions: f_LL = ", fLL_SM, " f_TX = ", fTX_SM)

      self.modelBuilder.doVar(f"mu_{iBin}[1,0,10]")
      self.modelBuilder.doVar(f"f_LL_{iBin}[{fLL_SM},0,1]")

      self.modelBuilder.factory_(f'expr::scale_{iBin}_LL("@0*@1/{fLL_SM}", mu_{iBin}, f_LL_{iBin})')
      self.modelBuilder.factory_(f'expr::scale_{iBin}_TX("@0*(1-@1)/{fTX_SM}", mu_{iBin}, f_LL_{iBin})')

      pois += [f"mu_{iBin}", f"f_LL_{iBin}"]

    self.modelBuilder.doSet("POI", ",".join(pois))

  def getYieldScale(self, bin, process):
    genBin, pol = getGenBinPolarization(process)
    if genBin is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> scale_" + str(genBin) + "_" + pol)
    return "scale_" + str(genBin) + "_" + pol


polarizationFractionsTXGenBin = PolarizationFractionsTXGenBin()
