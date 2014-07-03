#!/bin/tcsh

#setenv YANKHOME ${HOME}/yank/yank.choderalab
setenv YANKHOME ${HOME}/anaconda/lib/python2.7/site-packages

# Run in serial mode.
python ${YANKHOME}/yank/yank.py --receptor_prmtop setup/receptor.prmtop --ligand_prmtop setup/ligand.prmtop --complex_prmtop setup/complex.prmtop --complex_crd setup/complex.inpcrd --restraints harmonic --randomize_ligand --iterations 500 --verbose --platform OpenCL

# Run in MPI mode.
#mpirun -rmk pbs python ${YANKHOME}/yank/yank.py --receptor_prmtop receptor.prmtop --ligand_prmtop ligand.prmtop --complex_prmtop complex.prmtop --complex_crd complex.inpcrd --restraints harmonic --randomize_ligand --iterations 500 --verbose --mpi --platform OpenCL --gpus_per_node 4

