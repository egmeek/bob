#include "torch5spro.h"

using namespace Torch;

///////////////////////////////////////////////////////////////////////////
// Main
///////////////////////////////////////////////////////////////////////////

int main(int argc, char* argv[])
{
	char* image_filename = 0;
	int s_nb = 1;
	int s_min = 1;
	int s_step = 1;
	double sigma = 0.6;

	// Read the command line
	CmdLine cmd;
	cmd.info("Testing program for SelfQuotientImage.\n");
	cmd.addSCmdArg("image", &image_filename, "input image");
	cmd.addICmdOption("-s_nb", &s_nb, 1, "Number of different scales ");
	cmd.addICmdOption("-s_min", &s_min, 1, "Minimum scale: (2*s_min+1)");
	cmd.addICmdOption("-s_step", &s_step, 1, "Step scale: (2*s_step)");
	cmd.addDCmdOption("-sigma", &sigma, 0.6, "Gaussian kernel's variance at the minimum scale");

	cmd.read(argc, argv);

	// Load the image to play with
	xtprobeImageFile xtprobe;
	Image image_(1, 1, 3);

	CHECK_FATAL(xtprobe.load(image_, image_filename) == true);
	print("Loaded image of size [%dx%d] with [%d] planes.\n\n",
		image_.getWidth(), image_.getHeight(), image_.getNPlanes());

        // Convert it in Gray level (1 channel)
        Image image(image_.size(1),image_.size(0),1);
        CHECK_FATAL(image.copyFrom(image_) == true); 

	Image sqi_image(1, 1, image.size(2));

	// Set the Gaussian filter and smooth the image
	ipSelfQuotientImage sqi;
	CHECK_FATAL(sqi.setIOption("s_nb", s_nb) == true);
	CHECK_FATAL(sqi.setIOption("s_min", s_min) == true);
	CHECK_FATAL(sqi.setIOption("s_step", s_step) == true);
	CHECK_FATAL(sqi.setDOption("Sigma", sigma) == true);
	CHECK_FATAL(sqi.process(image) == true);
	CHECK_FATAL(sqi.getNOutputs() == 1);
	CHECK_FATAL(sqi.getOutput(0).getDatatype() == Tensor::Short);

	const ShortTensor& output_sqi = (const ShortTensor&)sqi.getOutput(0);
        CHECK_FATAL(sqi_image.resize(output_sqi.size(1), output_sqi.size(0), output_sqi.size(2)) == true);
	CHECK_FATAL(sqi_image.copyFrom(output_sqi) == true);
	CHECK_FATAL(xtprobe.save(sqi_image, "selfQuotientImage.pgm") == true);


	Image histo_image(1, 1, image.size(2));

        // Perform Histogram Equalization
        ipHistoEqual histoEqual;
        print("Performing Histogram Equalization...\n");
        CHECK_FATAL(histoEqual.process(sqi_image) == true);
        CHECK_FATAL(histoEqual.getNOutputs() == 1); 
        CHECK_FATAL(histoEqual.getOutput(0).getDatatype() == Tensor::Short);

        const ShortTensor& output_histo = (const ShortTensor&)histoEqual.getOutput(0);
        
	// Save the smoothed image
        CHECK_FATAL(histo_image.resize(output_histo.size(1), output_histo.size(0), output_histo.size(2)) == true);
	CHECK_FATAL(histo_image.copyFrom(output_histo) == true);
	CHECK_FATAL(xtprobe.save(histo_image, "selfQuotientImageHistoEqual.pgm") == true);


	//CHECK_FATAL(msr_image.resize(output.size(1), output.size(0), output.size(2)) == true);
	//CHECK_FATAL(xtprobe.save(msr_image, "multiscaleRetinex.jpg") == true);

	return 0;
}

