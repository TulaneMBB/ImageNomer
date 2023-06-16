.. ImageNomer documentation master file, created by
   sphinx-quickstart on Fri Jun 16 14:04:05 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ImageNomer Documentation
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Getting Started
===============

Download the docker image
-------------------------

.. code-block:: bash
docker pull ghcr.io/image-nomer/image-nomer:latest

Run the image
-------------

.. code-block:: bash
docker run -p 8008:8008 --it ghcr.io/image-nomer/image-nomer:latest

We expose port 8008 of the container to be accessible from your web browser.

Open the app in your browser
----------------------------

In your browser, navigate to http://localhost:8008

Explore example data
--------------------

We have provided an fMRI study of fibromyalgia from OpenNeuro.org for you to explore.

Unfortunately, due to NIH data policy, we cannot provide access to the Philadelphia Neurodevelopmental Cohort (PNC) dataset. 
Access may be obtained for research purposes through the database of Genotypes and Phenotypes (dbGaP).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
