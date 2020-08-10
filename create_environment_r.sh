#!/bin/bash


wget -q https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p "$HOME/miniconda"
rm Miniconda3-latest-Linux-x86_64.sh

export PATH="$HOME/miniconda/bin:$PATH"

conda create -y -q --name r-CS

source activate r-CS
conda install -y -q -c anaconda r-base=3.6
conda install -y -q -c anaconda r-essentials=3.6
conda install -y -q -c anaconda gxx_linux-64=7.3
conda install -y -q -c anaconda gfortran_linux-64=7.3
source deactivate r-CS


cd $HOME/miniconda/pkgs
rm *.tar.bz2 -f 2> /dev/null
