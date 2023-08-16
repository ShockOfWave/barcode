
# Barcode project


## Intro

The script (program) presented below is designed to calculate Vietoris-Rips complexes and Betti numbers (topological data analysis) using in general [GUDHI](https://gudhi.inria.fr/) library. In the Infochemistry Scientific Center ([ISC](https://infochemistry.ru/)), this approach is applied not to natural images, but to topography data obtained using atomic force and scanning electron microscopy. You can find out more about the use of TDA for real objects from material and surface sciences in the articles by Skorb, Nosonovsky, Zhukov, Aglikov, and Aliev. Links will be added later, as articles are published.

## Dependencies
To run code need to install [git](https://git-scm.com/) and [conda](https://www.anaconda.com/) package manager.

## Installation

```bash
git clone https://github.com/ShockOfWave/barcode.git
cd barcode
conda env create -f environment.yml
conda activate barcode
```

## Usage
- To run code put the data in project directory.
```bash
python -m src
```
- Select folder with data in terminal
- Output data will be in folder output in directory with data

The program will ask you for AFM data resolution and the maximum length of the Vietoris-Rips complex. We do not recommend that you choose the maximum length of the Vietoris-Rips complex greater than 200. Calculations can take a considerable amount of time.

## Output example

### Description of results

As a result of the calculations, you will get images of a persistent barcode and a diagram, an autocorrelation function along the x and y axes, as well as \*.csv files with numerical values of the above metrics. In addition to the above, you will get statistical values of minima/maxima for 3\*3 patches.

### Graphs

<p align="center">

![First image](images/barcode4github1.png)

</p>

<p align="center">

![Second image](images/diagram4github1.png)

</p>

<p align="center">

![Third image](images/autocorr_function.png)

</p>

# Asknowledgemen

We humbly thank Dr. Syam Hasan for the idea and great help in the implementation of the program.

> Md Syam Hasan, Michael Nosonovsky, "Topological data analysis for friction modeling",  EPL (Europhysics Letters) vol. 135 issue 5 (2021) pp: 56001, [https://doi.org/10.1209/0295-5075/ac2655](https://doi.org/10.1209/0295-5075/ac2655)

For LaTeX:

```tex
@article{Hasan2021,
  doi = {10.1209/0295-5075/ac2655},
  url = {https://doi.org/10.1209/0295-5075/ac2655},
  year = {2021},
  month = sep,
  publisher = {{IOP} Publishing},
  volume = {135},
  number = {5},
  pages = {56001},
  author = {Md Syam Hasan and Michael Nosonovsky},
  title = {Topological data analysis for friction modeling},
  journal = {{EPL} (Europhysics Letters)}
}
```

# Reference & Citation

The authors are more than happy if you refer the following works:

> Mikhail V. Zhukov, Aleksandr S. Aglikov, Mirnah Sabboukh, Dmitry A. Kozodaev, Timur A. Aliev,
Sviatlana A. Ulasevich, Michael Nosonovsky, Ekaterina V. Skorb, "AFM-Topological Data Analysis of Brass after Ultrasonic Surface Modification", [https://doi.org/10.1021/acsaenm.3c00233](https://doi.org/10.1021/acsaenm.3c00233)


# License
## MIT

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
