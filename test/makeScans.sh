#!/bin/bash
#
# Likelihood scans (Asimov at the SM point) and plots
# Needs the workspaces from runTests.sh
#
# Run:
#     bash makeScans.sh
#
# Output in plots/
#

mkdir -p scans plots logs

# ---- ----
# arguments: workspace POI range SM-point tag [extra options]
# other POIs are profiled
# ---- ----
scan1D() {
  ws=$1 ; poi=$2 ; range=$3 ; sm=$4 ; tag=$5 ; shift 5
  combine -M MultiDimFit workspaces/$ws.root -t -1 --setParameters $sm \
          --algo grid --points 100 -P $poi --floatOtherPOIs 1 --setParameterRanges $poi=$range \
          -n _${ws}_${poi}_${tag} $@ > logs/scan_${ws}_${poi}_${tag}.log 2>&1
  mv higgsCombine_${ws}_${poi}_${tag}.MultiDimFit.mH120.root scans/
}

# ---- ----
# both total and stat only (all constrained nuisances frozen)
# ---- ----
scan1DTotStat() {
  scan1D $1 $2 $3 $4 tot
  scan1D $1 $2 $3 $4 stat --freezeParameters allConstrainedNuisances
}

#
# simple datacard
#
SM=mu=1,f_LL=0.06,f_TL=0.27
scan1DTotStat simple_fractions f_LL 0,0.25    $SM
scan1DTotStat simple_fractions f_TL 0,0.6     $SM
scan1DTotStat simple_fractions mu   0.75,1.25 $SM

SM=mu=1,f_LX=0.33
scan1DTotStat simple_fractionsLX f_LX 0.1,0.6 $SM

SM=mu_LL=1,mu_TL=1,mu_TT=1
scan1DTotStat simple_strengths mu_LL 0,4   $SM
scan1DTotStat simple_strengths mu_TL 0,2.5 $SM
scan1DTotStat simple_strengths mu_TT 0.6,1.4 $SM

#
# 2D scan f_LL vs f_TL, mu profiled
#
combine -M MultiDimFit workspaces/simple_fractions.root -t -1 --setParameters mu=1,f_LL=0.06,f_TL=0.27 \
        --algo grid --points 2500 -P f_LL -P f_TL --floatOtherPOIs 1 \
        --setParameterRanges f_LL=0,0.25:f_TL=0,0.6 \
        -n _simple_fractions_2D > logs/scan_simple_fractions_2D.log 2>&1
mv higgsCombine_simple_fractions_2D.MultiDimFit.mH120.root scans/

#
# gen-binned datacard
#
SM=mu_0=1,f_LL_0=0.05,f_TL_0=0.25,mu_1=1,f_LL_1=0.08,f_TL_1=0.3
scan1D genbin_fractions f_LL_0 0,0.5 $SM tot
scan1D genbin_fractions f_LL_1 0,0.5 $SM tot
scan1D genbin_fractions f_TL_0 0,0.8 $SM tot
scan1D genbin_fractions f_TL_1 0,0.8 $SM tot
scan1D genbin_fractions mu_0   0.5,1.5 $SM tot
scan1D genbin_fractions mu_1   0.5,1.5 $SM tot


#
# plots
#
cd scans
draw1D() {
  # files variables xTitle labels outName
  root -l -b -q $1 "../drawScan1D.cxx(\"$2\",\"$3\",\"$4\",\"../plots/$5\")" | grep -E "^ \S+.* : min"
}

draw1D "higgsCombine_simple_fractions_f_LL_tot.MultiDimFit.mH120.root higgsCombine_simple_fractions_f_LL_stat.MultiDimFit.mH120.root"   f_LL "f_{LL}" "total,stat only" simple_fractions_f_LL
draw1D "higgsCombine_simple_fractions_f_TL_tot.MultiDimFit.mH120.root higgsCombine_simple_fractions_f_TL_stat.MultiDimFit.mH120.root"   f_TL "f_{TL}" "total,stat only" simple_fractions_f_TL
draw1D "higgsCombine_simple_fractions_mu_tot.MultiDimFit.mH120.root higgsCombine_simple_fractions_mu_stat.MultiDimFit.mH120.root"       mu   "#mu"    "total,stat only" simple_fractions_mu
draw1D "higgsCombine_simple_fractionsLX_f_LX_tot.MultiDimFit.mH120.root higgsCombine_simple_fractionsLX_f_LX_stat.MultiDimFit.mH120.root" f_LX "f_{LX}" "total,stat only" simple_fractionsLX_f_LX
draw1D "higgsCombine_simple_strengths_mu_LL_tot.MultiDimFit.mH120.root higgsCombine_simple_strengths_mu_LL_stat.MultiDimFit.mH120.root" mu_LL "#mu_{LL}" "total,stat only" simple_strengths_mu_LL
draw1D "higgsCombine_simple_strengths_mu_TL_tot.MultiDimFit.mH120.root higgsCombine_simple_strengths_mu_TL_stat.MultiDimFit.mH120.root" mu_TL "#mu_{TL}" "total,stat only" simple_strengths_mu_TL
draw1D "higgsCombine_simple_strengths_mu_TT_tot.MultiDimFit.mH120.root higgsCombine_simple_strengths_mu_TT_stat.MultiDimFit.mH120.root" mu_TT "#mu_{TT}" "total,stat only" simple_strengths_mu_TT

draw1D "higgsCombine_genbin_fractions_f_LL_0_tot.MultiDimFit.mH120.root higgsCombine_genbin_fractions_f_LL_1_tot.MultiDimFit.mH120.root" f_LL_0,f_LL_1 "f_{LL}" "gen bin 0,gen bin 1" genbin_fractions_f_LL
draw1D "higgsCombine_genbin_fractions_f_TL_0_tot.MultiDimFit.mH120.root higgsCombine_genbin_fractions_f_TL_1_tot.MultiDimFit.mH120.root" f_TL_0,f_TL_1 "f_{TL}" "gen bin 0,gen bin 1" genbin_fractions_f_TL
draw1D "higgsCombine_genbin_fractions_mu_0_tot.MultiDimFit.mH120.root higgsCombine_genbin_fractions_mu_1_tot.MultiDimFit.mH120.root"     mu_0,mu_1     "#mu"    "gen bin 0,gen bin 1" genbin_fractions_mu

root -l -b -q higgsCombine_simple_fractions_2D.MultiDimFit.mH120.root "../drawScan2D.cxx(\"f_LL\",\"f_TL\",\"f_{LL}\",\"f_{TL}\",0.06,0.27,\"../plots/simple_fractions_2D\")" | grep "best fit"
cd ..
