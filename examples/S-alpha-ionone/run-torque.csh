#!/bin/tcsh
#  Batch script for mpirun job on cbio cluster.
#
#
# walltime : maximum wall clock time (hh:mm:ss)
#PBS -l walltime=08:00:00
#
# join stdout and stderr
#PBS -j oe
#
# spool output immediately
#PBS -k oe
#
# specify queue
#PBS -q gpu
#
# nodes: number of 8-core nodes
#   ppn: how many cores per node to use (1 through 8)
#       (you are always charged for the entire node)
#PBS -l nodes=1:ppn=4:gpus=4:shared
#
# export all my environment variables to the job
##PBS -V
#
# job name (default = name of script file)
#PBS -N S-alpha-ionone
#
# specify email
#PBS -M rosaluirink@gmail.com
#
# mail settings
#PBS -m n
#
# filename for standard output (default = <job_name>.o<job_id>)
# at end of job, it is in directory from which qsub was executed
# remove extra ## from the line below if you want to name your own file
##PBS -o /cbio/jclab/yank/cragganmore/example/torque.out

cd $PBS_O_WORKDIR

#setenv YANKHOME ${HOME}/yank/yank.choderalab
setenv YANKHOME ${HOME}/anaconda/lib/python2.7/site-packages

date
hostname

mpirun -rmk pbs python $YANKHOME/yank/yank.py --receptor_prmtop setup/receptor.prmtop --ligand_prmtop setup/ligand.prmtop --complex_prmtop setup/complex.prmtop --complex_crd setup/complex.inpcrd --restraints harmonic --randomize_ligand --iterations 500 --verbose --mpi --platform OpenCL --gpus_per_node 4 >& output
date

