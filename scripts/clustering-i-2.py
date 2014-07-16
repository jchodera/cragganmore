
# coding: utf-8

# This example demonstrates one possible way to cluster data sets that are too large to fit into memory using MDTraj and `scipy.cluster`. The idea for the algorithim is that we'll cluster every N-th frame directly, and then, considering the clusters fixed "assign" the remaining frames to the nearest cluster. It's not the most sophisticated algorithm, but it's a good demonstration of how MDTraj can be integrated with other data science tools.

# In[ ]:

import random
from collections import defaultdict
import mdtraj as md
import numpy as np
import scipy.cluster.hierarchy


# In[ ]:

stride = 1
h5traj = raw_input("Enter here the path to the trajectory:")
nc= raw_input("Enter here the number of clusters:")
n_clusters = int(nc)
subsampled= md.load(h5traj, stride=stride)
print subsampled


# In[ ]:

# Compute the pairwise RMSD between all of the frames. This requires
# N^2 memory, which is why we might need to stride.

distances = np.empty((subsampled.n_frames, subsampled.n_frames))
for i in range(subsampled.n_frames):
    distances[i] = md.rmsd(subsampled, subsampled, i)


# In[ ]:

# Now that we have the distances, we can use out favorite clustering
# algorithm. I like ward.
#n_clusters = nc_int
linkage = scipy.cluster.hierarchy.ward(distances)
labels = scipy.cluster.hierarchy.fcluster(linkage, t=n_clusters, criterion='maxclust')
print labels


# In[ ]:

# Now, we need to extract n_leaders random samples from each of the clusters.
# One way to do this is by building a map from each of the cluster labels
# to the list of the indices of the subsampled confs which belong to it.
mapping = defaultdict(lambda : [])
for i, label in enumerate(labels):
    mapping[label].append(i)
print mapping


# In[ ]:

# Now we can iterate through the mapping and select n_leaders random
# samples from each list. As we select them, we'll extract the
# conformation and append it to a new trajectory called `leaders`, which
# will start empty.

n_leaders_per_cluster = 2
leaders = md.Trajectory(xyz=np.empty((0, subsampled.n_atoms, 3)),
                        topology=subsampled.topology)
leader_labels = []
for label, indices in mapping.items():
    leaders = leaders.join(subsampled[np.random.choice(indices, n_leaders_per_cluster)])
    leader_labels.extend([label] * n_leaders_per_cluster)
print leaders
print leader_labels


# In[ ]:

# Now our `leaders` trajectory contains a set of representitive conformations
# for each cluster. Here comes the second pass of the two-pass clustering.
# Let's now consider these clusters as fixed objects and iterate through
# *every* frame in our data set, assigning each frame to the cluster
# it's closest to. We take the simple approach here of computing the distance
# from each frame to each leader and assigning the frame to the cluster whose
# leader is closest.

# Note that this whole algorithm never requires having the entire
# dataset in memory at once

labels = []
for frame in md.iterload(h5traj, chunk=1):
    labels.append(leader_labels[np.argmin(md.rmsd(leaders, frame, 0))])
labels = np.array(labels)

#Save as text with np loadtxt so it can be later used with np
np.savetxt('savelabel.out', labels, delimiter=' ', fmt="%s")
loadtext= np.loadtxt('savelabel.out', dtype=str , delimiter='\n')
#print loadtext

#For loop to take from the trajectory the frames corresponding to a cluster and put them in 1 pdb trajectory
for i in xrange (1, n_clusters+1):
    j = str(i)
    numindex= np.where(loadtext==j)
    x = 'numindex' + j 
    xout= x + '.out'
    x2 = x + '_int.out'
    trajecti= 'trajectory' + j + '.pdb'
    np.savetxt(xout, numindex, delimiter=' ', fmt="%s")
    makeint = np.loadtxt(xout, dtype=str, delimiter=' ')
    xout2 = map(int, makeint)
    np.savetxt(x2, xout2, delimiter=' ', fmt="%i")
    x3= np.loadtxt(x2, dtype=int, delimiter=' ')
    slicedi=subsampled.slice(x3)
    slicedi.save_pdb(trajecti)
#    np.savetxt(trajecti,slicedi, delimiter='\n', fmt ="%s")
#    pdbi= md.load_frame(h5traj, x2)
#    np.savetxt(trajecti,pdbi, delimiter= '\n', fmt ="%s")

#    blabla = np.loadtxt(x2, dtype=int, delimiter=' ')
#    print blabla



