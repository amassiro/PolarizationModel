import re
from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel

#
# Polarization signal strengths model, TL and TT merged into TX, in gen-level bins
#
#   POI, for each gen bin N:  mu_LL_N, mu_TX_N
#
# Processes are assigned to a gen bin and a polarization state from their name suffix:
#
#     <anything>_binN_LL                               ->  scaled by mu_LL_N
#     <anything>_binN_TL (or _LT), <anything>_binN_TT  ->  scaled by mu_TX_N
#     anything else                                    ->  not scaled (background)
#
# Gen bins are found automatically in the datacard and must be N = 0, 1, ..., nGenBins-1.
# mu_AA_N = sigma_AA_N / sigma_AA_N^SM: no SM fractions needed.
# NB: TL and TT are scaled by the same factor, i.e. their SM ratio is assumed.
#
# Run:
#     text2workspace.py datacard.txt -P HiggsAnalysis.PolarizationModel.PolarizationSignalStrengthsTXGenBin:polarizationSignalStrengthsTXGenBin -o model.root
#


def getGenBinPolarization(process):
  match = re.search(r"_bin(\d+)_(LL|TL|LT|TT)$", process)
  if match is None:
    if re.search(r"_(LL|TL|LT|TT)$", process):
      raise RuntimeError("process " + process + " has a polarization suffix but no _binN_: fix the name")
    return None, None
  pol = "LL" if match.group(2) == "LL" else "TX"
  return int(match.group(1)), pol


class PolarizationSignalStrengthsTXGenBin(PhysicsModel):

  def __init__(self):
    PhysicsModel.__init__(self)

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
      raise RuntimeError("PolarizationSignalStrengthsTXGenBin: gen bins must be 0, ..., N-1, found " + str(sorted(genBins)))
    print (" nGenBins = ", nGenBins)

    pois = []
    for iBin in range(nGenBins):
      for pol in ["LL", "TX"]:
        self.modelBuilder.doVar(f"mu_{pol}_{iBin}[1,0,20]")
        pois.append(f"mu_{pol}_{iBin}")

    self.modelBuilder.doSet("POI", ",".join(pois))

  def getYieldScale(self, bin, process):
    genBin, pol = getGenBinPolarization(process)
    if genBin is None:
      return 1
    print (" bin = ", bin, " process = ", process, " -> mu_" + pol + "_" + str(genBin))
    return "mu_" + pol + "_" + str(genBin)


polarizationSignalStrengthsTXGenBin = PolarizationSignalStrengthsTXGenBin()
