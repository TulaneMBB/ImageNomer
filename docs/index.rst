.. ImageNomer documentation master file, created by
   sphinx-quickstart on Fri Jun 16 14:04:05 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ImageNomer Documentation
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Getting Started - Live Web Demo
===============================

There is a live web demo running at https://aorliche.github.io/ImageNomer/live

This demo contains a single Fibromyalgia dataset from OpenNeuro.org, the same as contained in the Docker image.

Once you have loaded ImageNomer, you can check out the :ref:`Fibromyalgia-Tutorial`. 

**Note: The beta version of ImageNomer retains state for the duration of the session.** 

This includes generated correlation images, which may impact stability if many users access the web demo in a short amount of time.

.. _Getting-Started:

Getting Started with Docker
===========================

Install docker
--------------

You need to install docker for this to work.

Download and run the docker image
---------------------------------

.. code-block:: bash

    docker pull ghcr.io/aorliche/image-nomer:latest
    docker run -p 8008:8008 ghcr.io/aorliche/image-nomer:latest

We expose port 8008 of the container to be accessible from your web browser.

In your browser, navigate to http://localhost:8008

Explore example data
--------------------

We have provided an fMRI study of fibromyalgia from OpenNeuro.org for you to explore.

Unfortunately, due to NIH data policy, we cannot provide access to the Philadelphia Neurodevelopmental Cohort (PNC) dataset or to BSNIP. Access may be obtained for research purposes through the database of Genotypes and Phenotypes (dbGaP). If you do have permission, we would be happy to work with you regarding functions such as, e.g. SNPs, that are not available in the Fibromyalgia dataset.

Adding Your Own Data
====================

To add your own data, you will need to clone the GitHub repository and install the required Python dependencies.

.. code-block:: bash

   git clone https://github.com/TulaneMBB/ImageNomer
   cd ImageNomer
   pip install -r requirements.txt

The repository already contains the Fibromyalgia dataset. To run ImageNomer, execute the following command:

.. code-block:: bash

   python backend/app.py

Then, navigate to http://localhost:8008 

Data is stored in the "ImageNomer/data/anton/cohorts" directory. Currently, the only user is "anton". See the `ImageNomer26FibromyalgiaDataset.ipynb <https://github.com/TulaneMBB/ImageNomer/tree/main/notebooks>`_ notebook file for an example of how to import data into ImageNomer when starting with a csv file and BOLD timeseries.

An additional description of the dataset layout in ImageNomer is coming soon.

Changing the Code
=================

.. image:: images/FigureArchitecture.png
   width: 600px

ImageNomer consists of a a Python backend and a Vue javascript frontend. All Python packages are listed in the `requirements.txt <https://github.com/TulaneMBB/ImageNomer/blob/main/requirements.txt>`_ file. Vue requirements can be installed with *npm* from the `frontend` directory.

Please reach out with any questions.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
