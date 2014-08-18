"""
Generate XML files from AMBER prmtop/inpcrd files.

@author John D. Chodera
@date 6 Aug 2014

"""

import os, os.path
import numpy

# Import OpenMM modules.
from simtk.openmm import version
from simtk.openmm import app
from simtk import openmm
from simtk import unit

#
# PARAMETERS
#
rundir = "./RUNS/RUN0/"
nclones = range(5,100)
nsteps_to_test = 500 # number of timesteps to run from each clone to test

# Show actual OpenMM version to be used
print "Using OpenMM Version : ", version.full_version

#
# SUBROUTINES
#
def write_file(filename, contents):
    with open(filename, 'w') as outfile:
        outfile.write(contents)
        
def read_file(filename):
    with open(filename, 'r') as infile:
        return infile.read()

def write_pdb(filename, topology, positions):
    with open(filename, 'w') as outfile:
        app.PDBFile.writeFile(topology, positions, file=outfile)


# Write system.
print "Deserializing system..."
system_filename = os.path.join(rundir, "system.xml")
system = openmm.XmlSerializer.deserialize(read_file(system_filename))

# Create a Langevin integrator with specified temperature, collision rate, and timestep.
print "Deserializing integrator..."
integrator_filename = os.path.join(rundir, "integrator.xml")
integrator = openmm.XmlSerializer.deserialize(read_file(integrator_filename))

# Get temperature from integrator
temperature = integrator.getTemperature()

# Create a context.
print "Creating context..."
context = openmm.Context(system, integrator)

# Show platform used.
print "Using platform : ", context.getPlatform().getName()

# Read minimized coordinates
state_filename = os.path.join(rundir, "minimized.xml")
state = openmm.XmlSerializer.deserialize(read_file(state_filename))
minimized_positions = state.getPositions()

# Get Boxvectors from state
box_vectors = state.getPeriodicBoxVectors()

# Generate initial conditions.
for clone_index in nclones:
    print "Clone %d / %d..." % (clone_index, max(nclones))
    # Reset positions and box vectors
    context.setPositions(minimized_positions)
    context.setPeriodicBoxVectors(*box_vectors)

    # Choose new velocities from Maxwell-Boltzmann distribution.
    context.setVelocitiesToTemperature(temperature)

    # Take a single step to engage constraints.
    integrator.step(1)

    # Get state and write to file.
    state = context.getState(getPositions=True, getVelocities=True, getForces=True, getEnergy=True, getParameters=True, enforcePeriodicBox=True)
    state_filename = os.path.join(rundir, 'state%d.xml' % clone_index)
    serialized = openmm.XmlSerializer.serialize(state)
    write_file(state_filename, serialized)

    # Test.
    print "Testing with %d steps of integration..." % nsteps_to_test
    integrator.step(nsteps_to_test)
    state = context.getState(getEnergy=True)
    potential_energy = state.getPotentialEnergy()
    if numpy.isnan(potential_energy / unit.kilocalories_per_mole):
        raise Exception("Energy became NaN after %d steps of test dynamics." % nsteps_to_test)