/*#include <opencv2/opencv.hpp>*/
#include <opencv2/core.hpp>
#include <opencv2/dnn/dnn.hpp>
#include <iostream>
using namespace std;
using namespace cv;

class SpectralImage
{
public:
	void setImage();
	void setMetadata();
	Mat getBand(Mat Image, int band);
	dnn::Dict getMetadata();
private:
	Mat SpectralImage;
	dnn::Dict metadata;
};

int main(void)
{
	SpectralImage micaSenseRedEdge;
	return 0;
}