//
//---- 2D likelihood scan, -2DlnL map with 68% and 95% CL contours (2 POIs: 2.30, 5.99)
//
//   r99t higgsCombine2D.root drawScan2D.cxx\(\"f_LL\",\"f_TL\",\"f_{LL}\",\"f_{TL}\",0.06,0.27,\"scan2D\"\)
//
//   xSM, ySM: SM point (drawn as a star)
//   line f_LL + f_TL = 1 drawn (f_TT = 0), if inside the range
//


void drawScan2D(std::string xVar = "f_LL", std::string yVar = "f_TL", std::string xTitle = "f_{LL}", std::string yTitle = "f_{TL}", float xSM = 0.06, float ySM = 0.27, std::string outName = "scan2D") {

  gStyle->SetOptStat(0);
  gStyle->SetPalette(kBird);
  gStyle->SetNumberContours(255);

  TTree* limit = (TTree*) _file0->Get("limit");

  //---- best fit is the first entry (quantileExpected = -1)
  float x_best = 0;
  float y_best = 0;
  limit->SetBranchAddress(xVar.c_str(), &x_best);
  limit->SetBranchAddress(yVar.c_str(), &y_best);
  limit->GetEntry(0);
  float x_bestfit = x_best;
  float y_bestfit = y_best;
  limit->ResetBranchAddresses();

  TString whatToDraw = Form("%s:%s:2*deltaNLL", xVar.c_str(), yVar.c_str());
  int n = limit->Draw(whatToDraw.Data(), "quantileExpected != 1", "goff");
  std::cout << " points = " << n << std::endl;

  TGraph2D* graphScan = new TGraph2D(n, limit->GetV1(), limit->GetV2(), limit->GetV3());
  graphScan->SetNpx(200);
  graphScan->SetNpy(200);
  TH2D* histo = graphScan->GetHistogram();
  histo->SetTitle("");

  TCanvas* cc = new TCanvas("cc", "", 800, 600);
  cc->SetTicks();
  cc->SetRightMargin(0.15);
  cc->SetLeftMargin(0.12);
  cc->SetBottomMargin(0.12);

  histo->GetXaxis()->SetTitle(xTitle.c_str());
  histo->GetYaxis()->SetTitle(yTitle.c_str());
  histo->GetZaxis()->SetTitle("-2 #Delta lnL");
  histo->GetXaxis()->SetTitleSize(0.05);
  histo->GetYaxis()->SetTitleSize(0.05);
  histo->GetXaxis()->SetTitleOffset(1.0);
  histo->GetYaxis()->SetTitleOffset(1.0);
  histo->GetZaxis()->SetRangeUser(0, 15);
  histo->Draw("colz");

  //---- contours
  TH2D* histoContour = (TH2D*) histo->Clone("histoContour");
  Double_t contours[2] = {2.30, 5.99};
  histoContour->SetContour(2, contours);
  histoContour->Draw("cont3 same");
  histoContour->SetLineColor(kBlack);
  histoContour->SetLineWidth(3);

  //---- clone for the legend (cont3 draws all levels with the same style)
  TH2D* h68 = new TH2D("h68", "", 1, 0, 1, 1, 0, 1);
  h68->SetLineColor(kBlack);
  h68->SetLineWidth(3);

  //---- f_TT = 0 line: x + y = 1
  float xMin = histo->GetXaxis()->GetXmin();
  float xMax = histo->GetXaxis()->GetXmax();
  float yMax = histo->GetYaxis()->GetXmax();
  TLine* lineBoundary = 0;
  if (xMax + yMax > 1) {
    lineBoundary = new TLine(std::max(xMin, (float) (1 - yMax)), std::min(yMax, (float) (1 - xMin)), xMax, 1 - xMax);
    lineBoundary->SetLineColor(kRed);
    lineBoundary->SetLineWidth(2);
    lineBoundary->SetLineStyle(2);
    lineBoundary->Draw();
  }

  TMarker* markerSM = new TMarker(xSM, ySM, 29);
  markerSM->SetMarkerSize(3);
  markerSM->SetMarkerColor(kRed);
  markerSM->Draw();

  TMarker* markerBest = new TMarker(x_bestfit, y_bestfit, 34);
  markerBest->SetMarkerSize(2);
  markerBest->SetMarkerColor(kBlack);
  markerBest->Draw();

  TLegend* leg = new TLegend(0.60, 0.70, 0.83, 0.88);
  leg->SetTextSize(0.035);
  leg->SetBorderSize(1);
  leg->SetFillColor(0);
  leg->AddEntry(h68, "68%, 95% CL", "l");
  leg->AddEntry(markerSM, "SM", "p");
  leg->AddEntry(markerBest, "best fit", "p");
  if (lineBoundary) leg->AddEntry(lineBoundary, "f_{TT} = 0", "l");
  leg->Draw();

  TLatex* tex = new TLatex(0.12, 0.92, "Asimov, cut&count test datacard");
  tex->SetNDC();
  tex->SetTextFont(42);
  tex->SetTextSize(0.04);
  tex->Draw();

  std::cout << " best fit: " << xVar << " = " << x_bestfit << "  " << yVar << " = " << y_bestfit << std::endl;

  cc->SaveAs((outName + ".png").c_str());
  cc->SaveAs((outName + ".pdf").c_str());
}
