'''
Created on 03.09.2014

@author: jan-hendrikprinz
'''

import mdtraj as md
import os
if __name__ == '__main__':
    
    
    DATA_FOLDER = os.path.join('..','..', 'traj')
    TOP_FILE = os.path.join('..','..', 'RUNS', 'RUN1', 'minimized.pdb')
    
    top_file = md.load(TOP_FILE)
    
    heme_indices = [ a.index for a in top_file.topology.atoms if a.residue.name == 'HEM']
    counterion_indices = [ a.index for a in top_file.topology.atoms if a.residue.name == 'Na+']
    solvent_indices = [ a.index for a in top_file.topology.atoms if a.residue.name == 'HOH']
    protein_indices = [ a.index for a in top_file.topology.atoms if a.residue.name != 'Na+' and a.residue.name != 'HEM' and a.residue.name != 'HOH']
    
    relevant_indices = protein_indices + heme_indices

    top_relevant = md.load(TOP_FILE)
    top_relevant.restrict_atoms(relevant_indices)
    
#    t = md.Topology()

    save_topology_filename = os.path.join(DATA_FOLDER, 'relevant.pdb')
        
    top_relevant.save_pdb(save_topology_filename, True)
        
    stream_folders = os.walk(DATA_FOLDER).next()[1]
        
    for stream_no, stream_folder in enumerate(stream_folders):
        print 'Stream :', stream_no
        stream_path = os.path.join(DATA_FOLDER, stream_folder)
        parts_folders = os.walk(stream_path).next()[1]
        sorted_folders = sorted(parts_folders, key=lambda value: int(value))
        
        if len(sorted_folders) > 0:
            stream_files = [os.path.join(stream_path, folder, 'frames.xtc') for folder in sorted_folders]
                    
#            print stream_folder, stream_files
            traj = md.load(stream_files, top = top_file)
    #        traj = md.Trajectory()
            traj.restrict_atoms(relevant_indices)
            
            print traj.topology.n_atoms
            save_data_filename = os.path.join(stream_path, 'all.xtc')
            traj.save_xtc(save_data_filename, True)
    
    pass