"""
Generate XML files from AMBER prmtop/inpcrd files.

@author John D. Chodera
@date 6 Aug 2014

"""

import numpy

# Import OpenMM modules.
from simtk.openmm import app
from simtk import openmm
from simtk import unit

#
# PARAMETERS
#
cutoff = 9.0*unit.angstrom # nonbonded cutoff
temperature = 300.0*unit.kelvin
collision_rate = 1./unit.picosecond
timestep = 2.0*unit.femtoseconds
nonbondedMethod = app.PME
constraints = app.HBonds
pressure = 1.0*unit.atmospheres
barostatFrequency = 50
rundir = "./RUNS/RUN0/"
nclones = 500
nsteps_to_test = 500 # number of timesteps to run from each clone to test

#
# SUBROUTINES
#
def write_file(filename, contents):
    with open(filename, 'w') as outfile:
        outfile.write(contents)

# Load the Amber format parameters and topology files.
prmtop = app.AmberPrmtopFile('input.prmtop')
inpcrd = app.AmberInpcrdFile('input.inpcrd', loadBoxVectors=True)

# Create a System object using the parameters defined in the prmtop file.
system = prmtop.createSystem(nonbondedMethod=nonbondedMethod, nonbondedCutoff=cutoff, constraints=constraints)

# Write system.
system_filename = os.path.join(rundir, "system.xml")
write_file(system_filename, mm.XmlSerializer.serialize(system))

# Add a Monte Carlo barostat.
force = openmm.MonteCarloBarostat(pressure, temperature, barostatFrequency)

# Create a Langevin integrator with specified temperature, collision rate, and timestep.
integrator = LangevinIntegrator(temperature, collision_rate, timestep)
integrator_filename = os.path.join(rundir, "integrator.xml")
write_file(integrator_filename, mm.XmlSerializer.serialize(integrator))

# Create a context.
context = openmm.Context(system, integrator)

# Set positions and box vectors.
context.setPositions(inpcrd.positions)
simulation.context.setBoxVectors(inpcrd.getBoxVectors)

# Minimize the energy prior to simulation.
simulation.minimizeEnergy()
state = context.getState(getPositions=True)
minimized_positions = state.getPositions()
state_filename = os.path.join(rundir, "minimized.xml")
write_file(state_filename, mm.XmlSerializer.serialize(state))

# Generate initial conditions.
for clone_index in range(nclones):
    # Reset positions and box vectors
    context.setPositions(minimized_positions)
    simulation.context.setBoxVectors(inpcrd.getBoxVectors)

    # Choose new velocities from Maxwell-Boltzmann distribution.
    context.setVelocitiesToTemperature(temperature)

    # Take a single step to engage constraints.
    integrator.step(1)

    # Get state and write to file.
    state = simulation.context.getState(getPositions=True, getVelocities=True, getForces=True, getEnergy=True, getParameters=True, enforcePeriodicBox=True)
    state_filename = os.path.join(rundir, 'state%d.xml' % clone_index)
    serialized = mm.XmlSerializer.serialize(state)
    write_file(state_filename, serialized)

    # Test.
    integrator.step(nsteps_to_test)
    state = simulation.context.getState(getEnergy=True)
    potential_energy = state.getPotentialEnergy()
    if numpy.isnan(potential_energy / units.kilocalories_per_mole):
        raise Exception("Energy became NaN after %d steps of test dynamics." % nsteps_to_test)


