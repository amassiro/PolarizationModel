#
# Make simple cut&count datacards to test the polarization models
#
# Reco yields are built from gen-level SM yields and fractions times efficiencies,
# so that the SM fractions given to the models (--PO fLL_SM=...) are consistent
# with the datacard.
#
#   datacard_simple.txt  : 3 reco regions (LL-, TL-, TT-enriched), processes sig_LL, sig_TL, sig_TT, background
#   datacard_genbin.txt  : 2 gen bins x 2 reco bins x 3 reco regions, processes sig_binN_AA, background
#

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outdir", default=".", help="output folder")
args = parser.parse_args()

pols = ["LL", "TL", "TT"]

#
# reco regions, e.g. cuts on the decay angles, enriched in one polarization state
# efficiency of each polarization state in each region
#
regions = ["regLL", "regTL", "regTT"]
eff = {
  "regLL" : {"LL" : 0.25, "TL" : 0.10, "TT" : 0.05},
  "regTL" : {"LL" : 0.15, "TL" : 0.25, "TT" : 0.15},
  "regTT" : {"LL" : 0.05, "TL" : 0.10, "TT" : 0.30},
}
bkg = {"regLL" : 100., "regTL" : 150., "regTT" : 200.}


def writeDatacard(fileName, bins, processes, rates, lnN):

  #
  # bins      : list of bin names
  # processes : list of process names, index 0..n-1 signal, last one "background"
  # rates     : rates[bin][process]
  # lnN       : list of (name, {process : value})
  #
  width = max([len(p) for p in processes] + [len(b) for b in bins]) + 4
  col = lambda x : str(x).ljust(width)

  lines = []
  lines.append("imax *")
  lines.append("jmax *")
  lines.append("kmax *")
  lines.append("-" * 80)
  lines.append(col("bin") + "".join([col(b) for b in bins]))
  lines.append(col("observation") + "".join([col("%.1f" % sum(rates[b].values())) for b in bins]))
  lines.append("-" * 80)

  binLine = col("bin")
  procLine = col("process")
  indexLine = col("process")
  rateLine = col("rate")
  for b in bins:
    for iProc, p in enumerate(processes):
      binLine += col(b)
      procLine += col(p)
      # signal index <= 0, background > 0
      indexLine += col(1 if p == "background" else -iProc)
      rateLine += col("%.3f" % rates[b][p])
  lines += [binLine, procLine, indexLine, rateLine]
  lines.append("-" * 80)

  for name, values in lnN:
    line = col(name + " lnN")
    for b in bins:
      for p in processes:
        line += col(values.get(p, "-"))
    lines.append(line)

  with open(fileName, "w") as f:
    f.write("\n".join(lines) + "\n")
  print ("written ", fileName)


#
# simple datacard
#
nGen = 2000.
fSM = {"LL" : 0.06, "TL" : 0.27, "TT" : 0.67}

processes = ["sig_" + pol for pol in pols] + ["background"]
rates = {}
for reg in regions:
  rates[reg] = {}
  for pol in pols:
    rates[reg]["sig_" + pol] = nGen * fSM[pol] * eff[reg][pol]
  rates[reg]["background"] = bkg[reg]

lnN = [
  ("lumi",    {p : 1.02 for p in processes}),
  ("bkgnorm", {"background" : 1.10}),
]

writeDatacard(args.outdir + "/datacard_simple.txt", regions, processes, rates, lnN)
print ("   SM fractions: --PO fLL_SM=%g --PO fTL_SM=%g" % (fSM["LL"], fSM["TL"]))


#
# gen-binned datacard
#   gen bins, e.g. in m_jj or pT, with migrations to reco bins
#
nGenBins = 2
nGenPerBin = [1500., 500.]
fSMGenBin = [
  {"LL" : 0.05, "TL" : 0.25, "TT" : 0.70},
  {"LL" : 0.08, "TL" : 0.30, "TT" : 0.62},
]
# migration[recoBin][genBin] = probability that an event in genBin is reconstructed in recoBin
recoBins = ["reco0", "reco1"]
migration = {
  "reco0" : [0.85, 0.20],
  "reco1" : [0.15, 0.80],
}
bkgRecoBin = {"reco0" : 0.7, "reco1" : 0.3}

processes = ["sig_bin%d_%s" % (iGen, pol) for iGen in range(nGenBins) for pol in pols] + ["background"]
bins = []
rates = {}
for recoBin in recoBins:
  for reg in regions:
    b = recoBin + "_" + reg
    bins.append(b)
    rates[b] = {}
    for iGen in range(nGenBins):
      for pol in pols:
        rates[b]["sig_bin%d_%s" % (iGen, pol)] = nGenPerBin[iGen] * fSMGenBin[iGen][pol] * migration[recoBin][iGen] * eff[reg][pol]
    rates[b]["background"] = bkg[reg] * bkgRecoBin[recoBin]

lnN = [
  ("lumi",    {p : 1.02 for p in processes}),
  ("bkgnorm", {"background" : 1.10}),
]

writeDatacard(args.outdir + "/datacard_genbin.txt", bins, processes, rates, lnN)
print ("   SM fractions: --PO fLL_SM=%s --PO fTL_SM=%s --PO fLX_SM=%s" % (
       ",".join(["%g" % f["LL"] for f in fSMGenBin]),
       ",".join(["%g" % f["TL"] for f in fSMGenBin]),
       ",".join(["%g" % (f["LL"] + f["TL"]) for f in fSMGenBin])))
