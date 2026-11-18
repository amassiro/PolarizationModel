#
# Check the yield scaling of a polarization model workspace
#
# Sets the POIs to some test values and compares, for each bin and process,
#   n_exp(test POIs) / n_exp(default POIs)
# with the expected scaling computed here independently.
# Nuisances stay at their nominal values.
#
# Run:
#     python3 checkModel.py -i model.root -m PolarizationFractions --fLL 0.06 --fTL 0.27 -p mu=1.2,f_LL=0.15,f_TL=0.30
#

import argparse
import re
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input",  required=True, help="workspace root file")
parser.add_argument("-m", "--model",  required=True, help="model name, e.g. PolarizationFractions")
parser.add_argument("-p", "--pois",   required=True, help="test values, e.g. mu=1.2,f_LL=0.15")
parser.add_argument("--fLL", default="", help="SM f_LL (comma separated per gen bin)")
parser.add_argument("--fTL", default="", help="SM f_TL (comma separated per gen bin)")
parser.add_argument("--fLX", default="", help="SM f_LX (comma separated per gen bin)")
args = parser.parse_args()

toList = lambda s : [float(x) for x in s.split(",")] if s != "" else []
fLL_SM = toList(args.fLL)
fTL_SM = toList(args.fTL)
fLX_SM = toList(args.fLX)

f = ROOT.TFile.Open(args.input)
ws = f.Get("w")

poisTest = {}
for item in args.pois.split(","):
  name, value = item.split("=")
  poisTest[name] = float(value)


#
# expected scale, independent of the model code
#
def expectedScale(process, p):
  match = re.search(r"(?:_bin(\d+))?_(LL|TL|LT|TT)$", process)
  if match is None:
    return 1.
  pol = "TL" if match.group(2) == "LT" else match.group(2)
  genBin = match.group(1)
  i = int(genBin) if genBin is not None else 0
  sfx = ("_" + genBin) if genBin is not None else ""
  model = args.model.replace("GenBin", "")

  if model == "PolarizationFractions":
    fSM = {"LL" : fLL_SM[i], "TL" : fTL_SM[i], "TT" : 1 - fLL_SM[i] - fTL_SM[i]}
    fFit = {"LL" : p["f_LL" + sfx], "TL" : p["f_TL" + sfx], "TT" : 1 - p["f_LL" + sfx] - p["f_TL" + sfx]}
    return p["mu" + sfx] * fFit[pol] / fSM[pol]
  if model == "PolarizationFractionsLX":
    if pol == "TT":
      return p["mu" + sfx] * (1 - p["f_LX" + sfx]) / (1 - fLX_SM[i])
    return p["mu" + sfx] * p["f_LX" + sfx] / fLX_SM[i]
  if model == "PolarizationFractionsTX":
    if pol == "LL":
      return p["mu" + sfx] * p["f_LL" + sfx] / fLL_SM[i]
    return p["mu" + sfx] * (1 - p["f_LL" + sfx]) / (1 - fLL_SM[i])
  if model == "PolarizationSignalStrengths":
    return p["mu_" + pol + sfx]
  if model == "PolarizationSignalStrengthsLX":
    return p["mu_" + ("TT" if pol == "TT" else "LX") + sfx]
  if model == "PolarizationSignalStrengthsTX":
    return p["mu_" + ("LL" if pol == "LL" else "TX") + sfx]
  raise RuntimeError("unknown model " + args.model)


#
# read nominal yields at default POI values
#
pois = ws.set("POI")
poisDefault = {}
for poi in pois:
  poisDefault[poi.GetName()] = poi.getVal()
print (" default POIs = ", poisDefault)

nExp = {}
for func in ws.allFunctions():
  name = func.GetName()
  if name.startswith("n_exp_bin") and "_proc_" in name:
    nExp[name] = func.getVal()

#
# set test values, missing ones stay at default
#
poisAll = dict(poisDefault)
poisAll.update(poisTest)
for name, value in poisAll.items():
  ws.var(name).setVal(value)
print (" test POIs    = ", poisAll)

nBad = 0
for name in sorted(nExp.keys()):
  process = name.split("_proc_")[1]
  ratio = ws.function(name).getVal() / nExp[name] if nExp[name] != 0 else 0.
  expected = expectedScale(process, poisAll) / expectedScale(process, poisDefault)
  ok = abs(ratio - expected) < 1e-6 * max(1., abs(expected))
  if not ok:
    nBad += 1
  print ("  %-45s ratio = %10.6f   expected = %10.6f   %s" % (name, ratio, expected, "OK" if ok else "<--- MISMATCH"))

print (" result: ", "ALL OK" if nBad == 0 else str(nBad) + " MISMATCHES")
exit(0 if nBad == 0 else 1)
