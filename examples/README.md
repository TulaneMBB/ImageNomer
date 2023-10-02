# Examples for Mapping Local Data to Docker Image

This directory contains an example data directory which you can unzip, then map to the docker image (when starting the image).

The target directory in the container should be:

```
/root/ImageNomer/data/MyCohort
```

where "MyCohort" can be any name you want. The full command for starting the container with a mapped directory is:
   
```
docker -run -p 8008:8008 \
    -v /full/path/to/my/unzipped/cohort:/root/ImageNomer/data/VicariousPunishment \
    ghcr.io/aorliche/image-nomer:latest
```

Once the container is running, you can navigate to http://localhost:8008/ and refresh the page to see your data.

It should be visible under the cohorts dropdown, which may originally be set to Fibromyalgia.

This example dataset is dataset ds004775 from OpenNeuro.

Please see this [section of the docs](https://imagenomer.readthedocs.io/en/latest/#adding-your-own-data-to-docker-image) for more information.
