#!/bin/bash
#
# Test all polarization models on the cut&count datacards:
#   - text2workspace
#   - yield scaling check (checkModel.py)
#   - Asimov fit (best fit must be the SM point) with uncertainties
#
# Run from the test folder, with combine available:
#     python3 makeDatacards.py
#     bash runTests.sh
#

PKG=HiggsAnalysis.PolarizationModel

mkdir -p workspaces logs
nFail=0

# ---- ----
# arguments: name datacard model poi-options check-options test-pois
# ---- ----
runModel() {
  name=$1 ; card=$2 ; model=$3 ; po=$4 ; check=$5 ; test=$6
  obj="$(echo ${model:0:1} | tr A-Z a-z)${model:1}"

  echo "==== $name : $model"

  text2workspace.py $card -P $PKG.$model:$obj $po -o workspaces/$name.root > logs/t2w_$name.log 2>&1
  if [ $? -ne 0 ]; then echo "  text2workspace FAILED, see logs/t2w_$name.log"; nFail=$((nFail+1)); return; fi

  python3 checkModel.py -i workspaces/$name.root -m $model $check -p $test > logs/check_$name.log 2>&1
  if [ $? -ne 0 ]; then echo "  checkModel FAILED, see logs/check_$name.log"; nFail=$((nFail+1)); fi
  tail -1 logs/check_$name.log

  #
  # Asimov at the SM point = default POI values in the workspace
  # (without --setParameters combine generates the Asimov from the B-only model, i.e. POIs = 0)
  #
  smPoint=$(python3 -c "
import ROOT
ws = ROOT.TFile.Open('workspaces/$name.root').Get('w')
print (','.join([p.GetName() + '=' + str(p.getVal()) for p in ws.set('POI')]))
")
  echo "  Asimov at: $smPoint"

  combine -M MultiDimFit workspaces/$name.root -t -1 --setParameters $smPoint --algo singles -n _$name > logs/fit_$name.log 2>&1
  if [ $? -ne 0 ] || grep -q "MultiDimFit failed" logs/fit_$name.log; then echo "  fit FAILED, see logs/fit_$name.log"; nFail=$((nFail+1)); return; fi
  grep -E "^\s+\S+ :\s+[+-]" logs/fit_$name.log | sed 's/^/  /'
}

#
# simple datacard
#
runModel simple_fractions     datacard_simple.txt PolarizationFractions          "--PO fLL_SM=0.06 --PO fTL_SM=0.27" "--fLL 0.06 --fTL 0.27" "mu=1.2,f_LL=0.15,f_TL=0.30"
runModel simple_fractionsLX   datacard_simple.txt PolarizationFractionsLX        "--PO fLX_SM=0.33"                  "--fLX 0.33"            "mu=0.8,f_LX=0.5"
runModel simple_strengths     datacard_simple.txt PolarizationSignalStrengths    ""                                  ""                      "mu_LL=2,mu_TL=0.5,mu_TT=1.1"
runModel simple_strengthsLX   datacard_simple.txt PolarizationSignalStrengthsLX  ""                                  ""                      "mu_LX=1.5,mu_TT=0.9"
runModel simple_fractionsTX   datacard_simple.txt PolarizationFractionsTX        "--PO fLL_SM=0.06"                  "--fLL 0.06"            "mu=0.9,f_LL=0.2"
runModel simple_strengthsTX   datacard_simple.txt PolarizationSignalStrengthsTX  ""                                  ""                      "mu_LL=2.5,mu_TX=0.8"

#
# gen-binned datacard
#
runModel genbin_fractions     datacard_genbin.txt PolarizationFractionsGenBin         "--PO fLL_SM=0.05,0.08 --PO fTL_SM=0.25,0.3" "--fLL 0.05,0.08 --fTL 0.25,0.3" "mu_0=1.1,f_LL_0=0.1,f_TL_0=0.2,mu_1=0.7,f_LL_1=0.2,f_TL_1=0.4"
runModel genbin_fractionsLX   datacard_genbin.txt PolarizationFractionsLXGenBin       "--PO fLX_SM=0.3,0.38"                       "--fLX 0.3,0.38"                 "mu_0=1.1,f_LX_0=0.4,mu_1=0.7,f_LX_1=0.6"
runModel genbin_strengths     datacard_genbin.txt PolarizationSignalStrengthsGenBin   ""                                           ""                               "mu_LL_0=2,mu_TL_0=0.5,mu_TT_0=1.1,mu_LL_1=3,mu_TT_1=0.8"
runModel genbin_strengthsLX   datacard_genbin.txt PolarizationSignalStrengthsLXGenBin ""                                           ""                               "mu_LX_0=1.5,mu_TT_0=0.9,mu_LX_1=0.6"
runModel genbin_fractionsTX   datacard_genbin.txt PolarizationFractionsTXGenBin       "--PO fLL_SM=0.05,0.08"                      "--fLL 0.05,0.08"                "mu_0=1.1,f_LL_0=0.15,mu_1=0.7,f_LL_1=0.02"
runModel genbin_strengthsTX   datacard_genbin.txt PolarizationSignalStrengthsTXGenBin ""                                           ""                               "mu_LL_0=2.5,mu_TX_0=0.9,mu_TX_1=1.2"

echo "==== failures: $nFail"
