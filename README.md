PolarizationModel
====

Combine physics models for diboson polarization fits (LL, TL, TT).

Processes are assigned to a polarization state from the suffix of their name in the datacard:

    <anything>_LL            longitudinal - longitudinal
    <anything>_TL            transverse - longitudinal (also _LT accepted)
    <anything>_TT            transverse - transverse
    <anything>_binN_AA       as above, in gen-level bin N = 0, 1, 2, ... (GenBin models only)
    anything else            not scaled (background)

The templates in the datacard are always the SM predictions.


Models
----

Inclusive:

| Model (python/) | POI | Scaling |
| --- | --- | --- |
| `PolarizationFractions` | `mu, f_LL, f_TL` | $N_{AA} = \mu \, f_{AA}/f^{SM}_{AA} \, N^{SM}_{AA}$, with $f_{TT} = 1 - f_{LL} - f_{TL}$ |
| `PolarizationFractionsLX` | `mu, f_LX` | LL, TL: $\mu \, f_{LX}/f^{SM}_{LX}$; TT: $\mu \, (1-f_{LX})/(1-f^{SM}_{LX})$ |
| `PolarizationFractionsTX` | `mu, f_LL` | LL: $\mu \, f_{LL}/f^{SM}_{LL}$; TL, TT: $\mu \, (1-f_{LL})/(1-f^{SM}_{LL})$ |
| `PolarizationSignalStrengths` | `mu_LL, mu_TL, mu_TT` | $N_{AA} = \mu_{AA} \, N^{SM}_{AA}$ |
| `PolarizationSignalStrengthsLX` | `mu_LX, mu_TT` | LL, TL: $\mu_{LX}$; TT: $\mu_{TT}$ |
| `PolarizationSignalStrengthsTX` | `mu_LL, mu_TX` | LL: $\mu_{LL}$; TL, TT: $\mu_{TX}$ |

Gen-level binned (same logic, one set of POIs per gen bin N, `_N` appended to the POI names, e.g. `f_LL_0`, `mu_TT_2`):

    PolarizationFractionsGenBin           mu_N, f_LL_N, f_TL_N
    PolarizationFractionsLXGenBin         mu_N, f_LX_N
    PolarizationFractionsTXGenBin         mu_N, f_LL_N
    PolarizationSignalStrengthsGenBin     mu_LL_N, mu_TL_N, mu_TT_N
    PolarizationSignalStrengthsLXGenBin   mu_LX_N, mu_TT_N
    PolarizationSignalStrengthsTXGenBin   mu_LL_N, mu_TX_N

Where:

    mu      = sigma / sigma^SM (in the gen bin, for GenBin models)
    f_AA    = sigma_AA / sigma
    LX      = LL + TL (at least one longitudinal boson), TX = TL + TT (at least one transverse boson)
    mu_AA   = sigma_AA / sigma_AA^SM = mu * f_AA / f_AA^SM

NB:

    - the fraction models need the SM fractions f_AA^SM where the fractions are defined (fiducial / gen level),
      NOT the fractions of the reco yields in the datacard (efficiencies differ among LL, TL, TT):
          --PO fLL_SM=0.06 --PO fTL_SM=0.27              (PolarizationFractions)
          --PO fLX_SM=0.33                               (PolarizationFractionsLX)
          --PO fLL_SM=0.06                               (PolarizationFractionsTX)
          --PO fLL_SM=0.05,0.08 --PO fTL_SM=0.25,0.3     (GenBin: one value per gen bin, ordered by N)
    - POI defaults are the SM point: mu = 1, f_AA = f_AA^SM, mu_AA = 1
    - LX models scale LL and TL with the same factor, i.e. their SM ratio is assumed (TX models: TL and TT)
    - f_LL + f_TL > 1 gives negative TT yields: restrict ranges if needed (--setParameterRanges)
    - GenBin models find the gen bins in the datacard; they must be 0, ..., N-1.
      A process ending with _AA but without _binN_ is an error in GenBin models


To install (CMSSW):

    cd $CMSSW_BASE/src/HiggsAnalysis
    git clone git@github.com:amassiro/PolarizationModel.git
    scramv1 b -j 8

To install (standalone combine, built with pixi, see combine docs):

    git clone --depth 1 --branch v10.6.1 https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    cd HiggsAnalysis/CombinedLimit
    pixi add pandas      # needed by text2workspace, missing in pixi.toml of v10.6.1
    pixi run install
    ln -s /path/to/PolarizationModel/python .pixi/envs/default/lib/python3.12/site-packages/HiggsAnalysis/PolarizationModel
    eval "$(pixi shell-hook)"

NB: HiggsAnalysis is a regular python package (it has __init__.py), so adding another HiggsAnalysis folder to PYTHONPATH does not work: use the symlink.


Run:

    text2workspace.py datacard.txt -o model.root \
        -P HiggsAnalysis.PolarizationModel.PolarizationFractions:polarizationFractions \
        --PO fLL_SM=0.06 --PO fTL_SM=0.27

    combine -M MultiDimFit model.root -t -1 --algo singles

    combine -M MultiDimFit model.root -t -1 --algo grid --points 50 -P f_LL --floatOtherPOIs 1

Python object for each model: same name as the file, first letter lowercase (e.g. `PolarizationFractionsLXGenBin:polarizationFractionsLXGenBin`).


Test
----

Cut&count datacards with signal (sig_LL, sig_TL, sig_TT or sig_binN_AA) and a "background":

    cd test
    python3 makeDatacards.py
    bash runTests.sh

Where:

    makeDatacards.py   creates datacard_simple.txt (3 reco regions) and datacard_genbin.txt (2 gen bins, 2 reco bins x 3 regions)
    checkModel.py      checks n_exp in the workspace vs the expected scaling, for test POI values
    runTests.sh        text2workspace + checkModel + Asimov MultiDimFit for all the models

Likelihood scans (Asimov at the SM point, other POIs profiled, total and stat-only), after runTests.sh:

    bash makeScans.sh

Where:

    makeScans.sh       combine grid scans (scans/) and plots (plots/)
    drawScan1D.cxx     1D scans, more files overlaid, prints 68% / 95% CL intervals (-2DlnL = 1, 3.84)
    drawScan2D.cxx     2D scan with 68% / 95% CL contours (-2DlnL = 2.30, 5.99), SM point and best fit

    r99t higgsCombineA.root higgsCombineB.root drawScan1D.cxx\(\"f_LL\",\"f_{LL}\",\"total,stat only\",\"scan_f_LL\"\)
    r99t higgsCombine2D.root drawScan2D.cxx\(\"f_LL\",\"f_TL\",\"f_{LL}\",\"f_{TL}\",0.06,0.27,\"scan2D\"\)
