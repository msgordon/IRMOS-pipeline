IRMOS-pipeline
==============

Repository for IRMOS data reduction

Requirements
* ```numpy```
* ```skimage```
* ```matplotlib```
* ```scipy```
* ```pyfits```
* ```pyraf``` (and ```iraf```)

## General notes
All programs in the pipeline utilize the python built-in ```argparse``` module, which creates a unified help menu at the terminal.  For all programs, type ```python IRMOS_[].py -h``` to see the proper usage.

## Reduction steps
### BITPIX fix
The Java FITS writer from STScI neglects to add the 'BITPIX' keyword to the headers, thus rendering the files unreadable.  The following method simply updates the headers of input archive images.

```python IRMOS_bitfix.py \path\to\files\*.fit```

### Image combining
For each set of observations, there are 6 types of images each with the same split positions:

| Name | Description |
| ------- | ----- |
| Source | targets |
| Source Dark | target darks |
| Flat | flat lamp |
| Flat Dark | flat lamp darks |
| Neon | cal lamps |
| Neon Dark | cal lamp darks |

Each set must be combined individually. Refer to the observation log to find the file numbers of each set and feed those into ```IRMOS_combine.py```.

```python IRMOS_combine.py \path\to\files\ basename num_start num_end outfile```

E.g. If the flat darks are files [```'\raw\NGC253_7.fit'```, ```'\raw\NGC253_8.fit'```, ```'\raw\NGC253_9.fit'```], the command would read:

```python IRMOS_combine.py \raw NGC253_ 7 9 FlatDark.fit```

### Image arithmetic
The appropriate darks must be subtracted from the appropriate data set.  For each image type (source, flat, neon), use ```IRMOS_imarith.py``` to perform the subtraction.

```python IRMOS_imarith.py file1 file2 output -method sub```

### Cosmic clean
Like most CCDs, the IRMOS camera suffers from hot and dead pixels.  Using an implementation of Pieter Van Dokkum's [LA Cosmic](http://www.astro.yale.edu/dokkum/lacosmic/) routine, ```IRMOS_clean.py``` cleans input images of cosmic rays and hot/dead pixels all at once.

```python IRMOS_clean.py \path\to\files\*.fit [-o outdir]```

### Image derotation
The CCD and the grating mirror are actually at an angle inside IRMOS, which forces the spectra from each slit to fall on the camera at an angle. Therefore, to extract the spectra, the image plane must first be derotated so the dispersion is horizontal.

**NOTE:** At the time of this writing, we assume all slit positions are vertical, so the resulting spectra spill roughly horizontal across the image plane. The correction angle has been hardcoded to 1.15 degrees.

Derotation is performed as follows:

```python IRMOS_derotate.py \path\to\files\*.fit [-o outdir]```
