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
prefix = os.path.join('setup', 'system')
prmtop_filename = prefix + '.prmtop'
inpcrd_filename = prefix + '.inpcrd'
cutoff = 9.0*unit.angstrom # nonbonded cutoff
temperature = 300.0*unit.kelvin
collision_rate = 1./unit.picosecond
timestep = 2.0*unit.femtoseconds
nonbondedMethod = app.PME
constraints = app.HBonds
pressure = 1.0*unit.atmospheres
barostatFrequency = 50
rundir = "./RUNS/RUN0/"
nsteps = 125000 # number of timesteps to run to equilibrate

# Show actual OpenMM version to be used
print "Using OpenMM Version : ", version.full_version

#
# SUBROUTINES
#
def write_file(filename, contents):
    with open(filename, 'w') as outfile:
        outfile.write(contents)

def write_pdb(filename, topology, positions):
    with open(filename, 'w') as outfile:
        app.PDBFile.writeFile(topology, positions, file=outfile)

# Create directories if they do not exist.
if not os.path.exists(rundir):
    os.makedirs(rundir)

# Copy system PDB files
import shutil
shutil.copyfile(prefix + '.pdb', os.path.join(rundir, 'system.pdb'))

# Load the Amber format parameters and topology files.
print "Reading prmtop and inpcrd..."
prmtop = app.AmberPrmtopFile(prmtop_filename)
inpcrd = app.AmberInpcrdFile(inpcrd_filename, loadBoxVectors=True)
box_vectors = inpcrd.getBoxVectors()

# Write initial file.
pdb_filename = os.path.join(rundir, "initial.pdb")
write_pdb(pdb_filename, prmtop.topology, inpcrd.positions)

# Create a System object using the parameters defined in the prmtop file.
print "Creating system..."
system = prmtop.createSystem(nonbondedMethod=nonbondedMethod, nonbondedCutoff=cutoff, constraints=constraints)

# Add a Monte Carlo barostat.
print "Adding barostat..."
force = openmm.MonteCarloBarostat(pressure, temperature, barostatFrequency)
system.addForce(force)

# Create a Langevin integrator with specified temperature, collision rate, and timestep.
print "Creating and serializing integrator..."
integrator = openmm.LangevinIntegrator(temperature, collision_rate, timestep)
integrator_filename = os.path.join(rundir, "integrator.xml")
write_file(integrator_filename, openmm.XmlSerializer.serialize(integrator))

# Create a context.
print "Creating context..."
context = openmm.Context(system, integrator)

# Show platform used.
print "Using platform : ", context.getPlatform().getName()

# Set positions and box vectors.
print "Setting positions and box vectors..."
context.setPositions(inpcrd.positions)
context.setPeriodicBoxVectors(*box_vectors)

# Minimize the energy prior to simulation.
print "Minimizing..."
minimizer = openmm.LocalEnergyMinimizer.minimize(context)
state = context.getState(getPositions=True)
minimized_positions = state.getPositions()
state_filename = os.path.join(rundir, "minimized.xml")
write_file(state_filename, openmm.XmlSerializer.serialize(state))
pdb_filename = os.path.join(rundir, "minimized.pdb")
write_pdb(pdb_filename, prmtop.topology, minimized_positions)

# Generate initial conditions.
# Reset positions and box vectors
context.setPositions(minimized_positions)
context.setPeriodicBoxVectors(*box_vectors)

# Choose new velocities from Maxwell-Boltzmann distribution.
context.setVelocitiesToTemperature(temperature)

# Test.
print "Testing with %d steps of integration..." % nsteps
integrator.step(nsteps)
state = context.getState(getEnergy=True)
potential_energy = state.getPotentialEnergy()
if numpy.isnan(potential_energy / unit.kilocalories_per_mole):
    raise Exception("Energy became NaN after %d steps of test dynamics." % nsteps)

# Get state and write to file.
state = context.getState(getPositions=True, getVelocities=True, getForces=True, getEnergy=True, getParameters=True, enforcePeriodicBox=True)
state_filename = os.path.join(rundir, 'state%d.xml' % clone_index)
serialized = openmm.XmlSerializer.serialize(state)
write_file(state_filename, serialized)

# Update periodic box vectors.
box_vectors = state.getPeriodicBoxVectors()
system.updateDefaultPeriodicBoxVectors(*box_vectors)

# Write system with updated periodic box vectors.
print "Serializing system..."
system_filename = os.path.join(rundir, "system.xml")
write_file(system_filename, openmm.XmlSerializer.serialize(system))

