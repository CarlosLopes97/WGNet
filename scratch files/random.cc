 /* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
 /*
  * This program is free software; you can redistribute it and/or modify
  * it under the terms of the GNU General Public License version 2 as
  * published by the Free Software Foundation;
  *
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with this program; if not, write to the Free Software
  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
  */
 #include "ns3/simulator.h"
 #include "ns3/nstime.h"
 #include "ns3/command-line.h"
 #include "ns3/random-variable-stream.h"
 #include <iostream>
 #include "ns3/ptr.h"
 #include "ns3/double.h"
 #include "ns3/string.h"
 #include "ns3/integer.h"
 #include "ns3/gnuplot.h"
 #include <fstream>
 #include <map>
 #include <cmath>
 
 using namespace ns3;
 namespace {
  
/**
 * Round a double number to the given precision.
 * For example, `dround(0.234, 0.1) = 0.2` 
 * and `dround(0.257, 0.1) = 0.3`
 * \param [in] number The number to round.
 * \param [in] precision The least significant digit to keep in the rounding.
 * \returns \p number rounded to \p precision.
 */
double dround (double number, double precision)
{
  number /= precision;
  if (number >= 0)
    number = std::floor (number + 0.5);
  else
    number = std::ceil (number - 0.5);
  number *= precision;
  return number;
}

/**
 * Generate a histogram from a RandomVariableStream.
 * \param [in] rndvar The RandomVariableStream to sample.
 * \param [in] probes The number of samples.
 * \param [in] precision The precision to round samples to.
 * \param [in] title The title for the histogram.
 * \param [in] impulses Set the plot style to IMPULSES.
 * \return The histogram as a GnuPlot data set.
 */
static GnuplotDataset
Histogram (Ptr<RandomVariableStream> rndvar, unsigned int probes, double precision, const std::string& title, bool impulses = false)
{
  typedef std::map<double, unsigned int> histogram_maptype;
  histogram_maptype histogram;

  for(unsigned int i = 0; i < probes; ++i)
    {
      double val = dround ( rndvar->GetValue (), precision );
    //   std::cout<<"Valor: " << val<<std::endl;
      ++histogram[val];
    }

  Gnuplot2dDataset data;
  data.SetTitle (title);

  if (impulses)
    {
      data.SetStyle (Gnuplot2dDataset::IMPULSES);
    }

  for(histogram_maptype::const_iterator hi = histogram.begin ();
      hi != histogram.end (); ++hi)
    {
      data.Add (hi->first, (double)hi->second / (double)probes / precision);
    }
  return data;
}

}  // unnamed namespace


 int main (int argc, char *argv[])
 {
   CommandLine cmd;
   cmd.Parse (argc, argv);  
//    SeedManager::SetRun (3);
 
//    Ptr<UniformRandomVariable> uv = CreateObject<UniformRandomVariable> ();
//    uv->SetAttribute("Min", DoubleValue (0.9));

//    std::cout << uv->GetValue () << std::endl;

   
 unsigned int probes = 1000;
  double precision = 0.01;

//   GnuplotCollection gnuplots ("main-random-variables.pdf");
//   gnuplots.SetTerminal ("png");

  std::string fileNameWithNoExtension = "uniform-random-variable";
  std::string graphicsFileName      = fileNameWithNoExtension + ".png";
  std::string plotFileName        = fileNameWithNoExtension + ".plt";
  std::string plotTitle           = "RNV vs id";
  std::string dataTitle           = "Numbers";

  // Instantiate the plot and set its title.
    Gnuplot gnuplots (graphicsFileName);
    gnuplots.SetTitle(plotTitle);

    // Make the graphics file, which the plot file will be when it
    // is used with Gnuplot, be a PNG file.
    gnuplots.SetTerminal ("png");

   Gnuplot2dDataset dataset;
   dataset.SetStyle (Gnuplot2dDataset::LINES_POINTS);


  {
    Gnuplot plot;
    plot.SetTitle ("UniformRandomVariable");
    // plot.AppendExtra ("set yrange [0:]");

    Ptr<UniformRandomVariable> x = CreateObject<UniformRandomVariable> ();
    x->SetAttribute ("Min", DoubleValue (0.0));
    x->SetAttribute ("Max", DoubleValue (1.0));

    plot.AddDataset ( Histogram (x, probes, precision, "UniformRandomVariable [0.0 .. 1.0]") );
    // plot.AddDataset ( Gnuplot2dFunction ("1.0", "0 <= x && x <= 1 ? 1.0 : 0") );

    // Open the plot file.
    std::ofstream plotFile (plotFileName.c_str());
    // Write the plot file.
    plot.GenerateOutput (plotFile);
    // Close the plot file.
    plotFile.close ();

    // gnuplots.AddDataset (plot);
  }

 }