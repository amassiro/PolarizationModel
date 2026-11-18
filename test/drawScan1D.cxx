//
//---- 1D likelihood scan, one or more files overlaid
//
//   r99t higgsCombineA.root higgsCombineB.root drawScan1D.cxx\(\"f_LL\",\"f_{LL}\",\"total,stat only\",\"scan_f_LL\"\)
//
//   variables: one name for all files, or comma separated, one per file (e.g. "f_LL_0,f_LL_1")
//   labels:    comma separated, one per file
//


std::vector<std::string> splitString(std::string input) {
  std::vector<std::string> result;
  std::stringstream ss(input);
  std::string item;
  while (std::getline(ss, item, ',')) {
    result.push_back(item);
  }
  return result;
}


TGraph* getScan(TFile* file, std::string variable) {

  TTree* limit = (TTree*) file->Get("limit");
  TString toDraw = Form("2*deltaNLL:%s", variable.c_str());
  int n = limit->Draw(toDraw.Data(), "deltaNLL<50 && deltaNLL>-30 && quantileExpected != 1", "goff");

  //---- sort, remove duplicates, fix the 0 of the likelihood scan
  std::map <double, double> x_y_map;
  for (int iPoint = 0; iPoint < n; iPoint++) {
    x_y_map[limit->GetV2()[iPoint]] = limit->GetV1()[iPoint];
  }

  double minimum = 1000;
  for (auto it = x_y_map.begin(); it != x_y_map.end(); it++) {
    if (it->second < minimum) minimum = it->second;
  }

  TGraph* graphScan = new TGraph();
  for (auto it = x_y_map.begin(); it != x_y_map.end(); it++) {
    graphScan->SetPoint(graphScan->GetN(), it->first, it->second - minimum);
  }
  return graphScan;
}


//---- find where the scan crosses "level", left and right of the minimum
void printInterval(TGraph* graphScan, std::string name, double level) {

  int iMin = 0;
  for (int iPoint = 0; iPoint < graphScan->GetN(); iPoint++) {
    if (graphScan->GetY()[iPoint] < graphScan->GetY()[iMin]) iMin = iPoint;
  }
  double x_min = graphScan->GetX()[iMin];
  double low  = -999;
  double high = -999;
  for (int iPoint = iMin; iPoint > 0; iPoint--) {
    double y1 = graphScan->GetY()[iPoint];
    double y0 = graphScan->GetY()[iPoint-1];
    if (y1 <= level && y0 > level) {
      low = graphScan->GetX()[iPoint-1] + (level - y0) / (y1 - y0) * (graphScan->GetX()[iPoint] - graphScan->GetX()[iPoint-1]);
      break;
    }
  }
  for (int iPoint = iMin; iPoint < graphScan->GetN()-1; iPoint++) {
    double y0 = graphScan->GetY()[iPoint];
    double y1 = graphScan->GetY()[iPoint+1];
    if (y0 <= level && y1 > level) {
      high = graphScan->GetX()[iPoint] + (level - y0) / (y1 - y0) * (graphScan->GetX()[iPoint+1] - graphScan->GetX()[iPoint]);
      break;
    }
  }
  std::cout << " " << name << " : min = " << x_min << "   [" << low << ", " << high << "]   at -2DLL = " << level;
  if (low == -999 || high == -999) std::cout << "   (-999 = no crossing in scan range)";
  std::cout << std::endl;
}


void drawScan1D(std::string variables = "f_LL", std::string xTitle = "f_{LL}", std::string labels = "Expected", std::string outName = "scan", float yMax = 6) {

  gStyle->SetOptStat(0);

  std::vector<std::string> vars = splitString(variables);
  std::vector<std::string> legs = splitString(labels);

  int colors[] = {kBlue, kRed, kGreen+2, kMagenta, kOrange+7};
  int styles[] = {1, 2, 1, 2, 1};

  TCanvas* cc = new TCanvas("cc", "", 800, 600);
  cc->SetGrid();
  cc->SetTicks();
  cc->SetRightMargin(0.05);
  cc->SetBottomMargin(0.12);
  cc->SetLeftMargin(0.12);

  TLegend* leg = new TLegend(0.40, 0.74, 0.70, 0.88);
  leg->SetTextSize(0.04);
  leg->SetBorderSize(1);
  leg->SetFillColor(0);

  std::vector<TGraph*> graphs;
  float minX =  999;
  float maxX = -999;

  int iFile = 0;
  TIter next(gROOT->GetListOfFiles());
  while (TFile* file = (TFile*) next()) {
    std::string variable = vars.size() > 1 ? vars.at(iFile) : vars.at(0);
    std::cout << " file = " << file->GetName() << "  variable = " << variable << std::endl;

    TGraph* graphScan = getScan(file, variable);
    graphScan->SetLineWidth(3);
    graphScan->SetLineColor(colors[iFile % 5]);
    graphScan->SetLineStyle(styles[iFile % 5]);
    graphs.push_back(graphScan);

    minX = std::min(minX, (float) graphScan->GetX()[0]);
    maxX = std::max(maxX, (float) graphScan->GetX()[graphScan->GetN()-1]);

    std::string name = iFile < (int) legs.size() ? legs.at(iFile) : variable;
    leg->AddEntry(graphScan, name.c_str(), "l");
    printInterval(graphScan, name, 1.0);
    printInterval(graphScan, name, 3.84);
    iFile++;
  }

  //---- plot ----
  TH1F* frame = cc->DrawFrame(minX, 0, maxX, yMax);
  frame->GetXaxis()->SetTitle(xTitle.c_str());
  frame->GetYaxis()->SetTitle("-2 #Delta lnL");
  frame->GetXaxis()->SetTitleSize(0.05);
  frame->GetYaxis()->SetTitleSize(0.05);
  frame->GetXaxis()->SetTitleOffset(1.0);
  frame->GetYaxis()->SetTitleOffset(1.0);

  //  -2DlnL = 1.00 (68%) and 3.84 (95%), 1 POI
  TLine* line1 = new TLine(minX, 1.0, maxX, 1.0);
  line1->SetLineWidth(2);
  line1->SetLineStyle(2);
  line1->SetLineColor(kGray+1);
  line1->Draw();
  TLine* line2 = new TLine(minX, 3.84, maxX, 3.84);
  line2->SetLineWidth(2);
  line2->SetLineStyle(2);
  line2->SetLineColor(kGray+1);
  line2->Draw();

  for (auto graphScan : graphs) {
    graphScan->Draw("L");
  }
  leg->Draw();

  TLatex* tex = new TLatex(0.12, 0.92, "Asimov, cut&count test datacard");
  tex->SetNDC();
  tex->SetTextFont(42);
  tex->SetTextSize(0.04);
  tex->Draw();

  cc->SaveAs((outName + ".png").c_str());
  cc->SaveAs((outName + ".pdf").c_str());
}
