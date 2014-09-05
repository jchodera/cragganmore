'''
Created on 03.09.2014

@author: jan-hendrikprinz
'''

import mdtraj as md
import os
import sys
import numpy as np

import matplotlib.pyplot as plt

if __name__ == '__main__':
    
    DATA_FOLDER = os.path.join('..','..', 'traj')
    TOP_FILE = os.path.join(DATA_FOLDER, 'relevant.pdb')
    
    top_file = md.load(TOP_FILE)
                        
    traj_list = []
    
    heme_indices = [ a.index for a in top_file.topology.atoms if a.residue.name == 'HEM']
    counterion_indices = [ a.index for a in top_file.topology.atoms if a.residue.name == 'Na+']
    solvent_indices = [ a.index for a in top_file.topology.atoms if a.residue.name == 'HOH']
    protein_indices = [ a.index for a in top_file.topology.atoms if a.residue.name != 'Na+' and a.residue.name != 'HEM' and a.residue.name != 'HOH']
        
    sys.stdout.write("LOADING TRAJECTORIES : ")
    
    tot_length = 0
    
#    md.topology.Atom.
    
    top = md.Topology()

    stream_folders = os.walk(DATA_FOLDER).next()[1]
            
    for stream_no, stream_folder in enumerate(stream_folders[0:]):
        stream_path = os.path.join(DATA_FOLDER, stream_folder)
        load_data_filename = os.path.join(stream_path, 'all.xtc')        

        if os.path.isfile(load_data_filename):
        
            traj = md.load(load_data_filename, top = top_file)
            traj_list.append(traj)
            
            tot_length += traj.n_frames
            sys.stdout.write("#")
            sys.stdout.flush()

    sys.stdout.write(' (' + str(len(traj_list)) + ')')
    print ''    
    
    print [(idx, t.n_frames) for idx, t in enumerate(traj_list)]

    print '# Total Length : ', tot_length, 'frames (', tot_length / 4, 'ns )'    
    
#    t = md.Trajectory()
#    rmsd = md.rmsd(traj, traj[0])
#    print rmsd
    
    traj.superpose(traj[0], atom_indices = heme_indices)
    
    traj.save_xtc(os.path.join(DATA_FOLDER, 'test.xtc'))
    
#    rmsd = [ md.rmsd(traj, traj[0]) for traj in traj_list ]
#    print type(rmsd)

    for traj in traj_list:
        x_axis = np.arange(0.0,1.0 * len(traj), 1.0) / 4.0
        y_axis = md.rmsd(traj, traj[0])
    
        plt.plot(x_axis, y_axis, 'k')

    plt.show()
    
    for traj in traj_list:
        x_axis = np.arange(0.0,1.0 * len(traj), 1.0) / 4.0
        traj = traj.superpose(traj[0], atom_indices = heme_indices)
        y_axis = md.rmsd(traj, traj[0], atom_indices = heme_indices)
    
        plt.plot(x_axis, y_axis, 'k')

    plt.show()
    
    for traj in traj_list:
        x_axis = np.arange(0.0,1.0 * len(traj), 1.0) / 4.0
        traj = traj.superpose(traj[0])
        y_axis = md.compute_rg(traj)
    
        plt.plot(x_axis, y_axis, 'k')

    plt.show()
