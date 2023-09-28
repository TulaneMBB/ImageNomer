# ImageNomer

fMRI and omics viewer for machine learning

## Goals

1. Exploration of fMRI data
2. Quality control
3. Correlation analysis
4. Visualization of ML model weights and distribution

## On-Line Demo

There is a live demo available at [https://aorliche.github.io/ImageNomer/live/](https://aorliche.github.io/ImageNomer/live/).

See [the Fibromyalgia dataset tutorial](https://imagenomer.readthedocs.io/en/latest/Fibromyalgia.html#fibromyalgia-tutorial) for a walkthrough of how to use ImageNomer.

## Quick Start with Docker

1. Install Docker.
2. Download and run the ImageNomer Docker image.
3. Navigate to [http://localhost:8008/](http://localhost:8008/)

We have provided a sample Fibromyalgia dataset from OpenNeuro for you to explore. Access to the PNC and BSNIP datasets requires application to relevant funding agencies (see docs link below).

The docker-related commands are:

```bash
docker pull ghcr.io/aorliche/image-nomer:latest
docker run -p 8008:8008 ghcr.io/aorliche/image-nomer:latest
```

The docker images are currently available for the amd64 and arm64 architectures.

Visit [our ReadTheDocs site](https://imagenomer.readthedocs.io/en/latest/) for more information and a comprehensive tutorial.

## Importing Your Data

ImageNomer uses a particular directory structure for storing FC, PC, SNPs, and model weights. Phenotype data is stored in a "demographics.pkl" file. Check the notebooks directory file 

```
notebooks/ImageNomer26FibromyalgiaDataset.ipynb
```

to see how that data was imported, starting from a csv and BOLD timeseries.

To use the ImageNomer docker image with your own data, you must map your local directory to the docker image when starting the container.

```
docker -run -p 8008:8008 -v /full/path/to/my/local/cohort/dir:/root/ImageNomer/data/MyCohort ghcr.io/aorliche/image-nomer:latest
```

Your local cohort should now show up in the ImageNomer browser-based GUI, asuming you have created a "demographics.pkl" file in the cohort directory, along with Power264-template FC in an fc subdirectory of the cohort directory.

Please check the layout of the Fibromyalgia dataset provided in this repo and the Jupyter notebook mentioned above.

Currently, ImageNomer assumes you are using the 264-ROI Power atlas.

## Architecture

<img width='600' src='https://raw.githubusercontent.com/TulaneMBB/ImageNomer/main/images/FigureArchitecture.png'>

## Capabilities

FC View. You have the ability to create summary images.

<img width='800' src='https://raw.githubusercontent.com/TulaneMBB/ImageNomer/main/images/FigureFCPanel.png'>

Phenotype Groups. We identify bias in general intelligence surrogate, even when certain confounders are regressed out.

<img width='400' src='https://raw.githubusercontent.com/TulaneMBB/ImageNomer/main/images/FigureBias2.png'>

Identify Significant Effects. A simple comparison reveals unexpected information hidden in functional connectivity.

<img width='800' src='https://raw.githubusercontent.com/TulaneMBB/ImageNomer/main/images/FigureNullCorrelation2.png'>

Model Weights. We find that only a few SNPs are consistently chosen by bootstrapped LASSO mdoels.

<img width='600' src='https://raw.githubusercontent.com/TulaneMBB/ImageNomer/main/images/FigureWeights.png'>

## Publications

<a href='https://www.techrxiv.org/articles/preprint/ImageNomer_developing_an_fMRI_and_omics_visualization_tool_to_detect_racial_bias_in_functional_connectivity/21992006'>A preprint is available.</a>

Presented at SPIE: Medical Imaging 2023.

## Contact

My <a href='https://aorliche.github.io'>personal website</a><br>
<a href='mailto:aorlichenko@tulane.edu'>mailto:aorlichenko@tulane.edu</a>

