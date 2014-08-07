import base64
import os
import gzip
import siegetank

system_name = "CYP2D6_HUMAN"

# Need a more secure way to store and load this.
my_token = os.environ["SIEGETANK_TOKEN"]
siegetank.login(my_token)

RUNS_PATH = "./RUNS/RUN0/"

description = """\
This project explores the conformational dynamics of human cytochrome P450 2D6, an enzyme responsible for metabolizing 25% of clinically used drugs. A better understanding of the dynamics and function of this enzyme will eventually lead to safer and less toxic therapeutics.\
"""

opts = {'description': description, 'steps_per_frame': 125000}

target = siegetank.add_target(options=opts, engines=['openmm_601_cuda', 'openmm_601_opencl', 'openmm_601_cpu'])

system_filename = os.path.join(RUNS_PATH, "system.xml")
system_gz = gzip.compress(open(system_filename, 'rb').read())
encoded_system = base64.b64encode(system_gz).decode()

integrator_filename = os.path.join(RUNS_PATH, "integrator.xml")
integrator_gz = gzip.compress(open(integrator_filename, 'rb').read())
encoded_intg = base64.b64encode(integrator_gz).decode()

for i in range(200):
    print(i)
    state_filename = os.path.join(RUNS_PATH, "state%d.xml" % i)
    state_gz = gzip.compress(open(state_filename, 'rb').read())
    encoded_state = base64.b64encode(state_gz).decode()

    data = {
        'system.xml.gz.b64': encoded_system,
        'state.xml.gz.b64': encoded_state,
        'integrator.xml.gz.b64': encoded_intg
    }

    stream = target.add_stream(files=data, scv='vspg11')
