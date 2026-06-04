from _defs._init import *

## temporal generalization decoding
import mne
from mne.decoding import (SlidingEstimator, GeneralizingEstimator, Scaler,
                          cross_val_multiscore, LinearModel, get_coef,
                          Vectorizer, CSP)
mne.utils.set_config('MNE_USE_CUDA', 'true') 

def hplots(acc,times,tt,ttlabel,title=[],vmin=0.16,vmax=0.5,savefigpath=0):
    # data - n_figures x n_times x n_times
    
#     cmap = cm.get_cmap('seismic',5)
    cmap='coolwarm'
    row=int(np.sqrt(acc.shape[0])); col=int(np.sqrt(acc.shape[0]));
    
    i=0; fontsize=15;figsize=6
    fig, ax = plt.subplots(row, col,figsize=(col*figsize,row*figsize))
    for ii in range(row):
        for kk in range(col):
            score = acc[i]
            im = ax[ii][kk].imshow(score, interpolation='gaussian',origin='lower', cmap=cmap,
                           extent=times[[0, -1, 0, -1]], vmin=vmin, vmax=vmax)

            ax[ii][kk].set_xticks(tt)
            ax[ii][kk].set_yticks(tt)
            ax[ii][kk].set_xticklabels(ttlabel,fontsize=fontsize)
            ax[ii][kk].set_yticklabels(ttlabel,fontsize=fontsize)
            
            if kk==0:
                ax[ii][kk].set_ylabel('Train Time (s)',fontsize=fontsize)
            if ii==(col-1):
                ax[ii][kk].set_xlabel('Test Time (s)',fontsize=fontsize)
            
            ax[ii][kk].set_title('Rank'+str(ii+1)+' to Rank'+str(kk+1),fontsize=fontsize)

            c = 'w'
            for j in range(len(tt)):
                ax[ii][kk].axvline(tt[j], c=c)
                ax[ii][kk].axhline(tt[j], c=c)
            i=i+1
    
    cbar = plt.colorbar(im, ax=ax,shrink=0.12,anchor=(1.4,0.49))
    cbar.set_label('Accuracy',fontsize=15,rotation=90,labelpad=-60,y=0.5)
    cbar.ax.tick_params(labelsize=15)
    plt.suptitle(title,x=0.5,y=0.93,fontsize=16);
    plt.subplots_adjust(wspace = 0.2, hspace = 0.2)
    
    
    if savefigpath!=0:
        plt.savefig(savefigpath)

    plt.show()


def hplots_stats(dat,title=[],vmin=0.16,vmax=0.5,savefigpath=0,cmap=0,threshold=0.22):
    # data - n_figures x n_times x n_times
    
    acc = dat['acc']; acc_shuffle = dat['acc_shuffle']
    times = dat['times']; tt = dat['tt'][:2]; ttlabel = dat['ttlabel'][:2]
    
    structure =  [[0,1,0],[1,1,1],[0,1,0]]
    maxcluster=[]
    for i in range(len(acc_shuffle)):
        labeled_array, num_features = label(acc_shuffle[i]>threshold,structure=structure)
        cluster_sizes = np.array([np.sum(labeled_array == i) for i in range(1, num_features + 1)])
        maxcluster.append(cluster_sizes.max())
    maxcluster = np.array(maxcluster).max()
    
    if cmap==0:
        cmap = cm.get_cmap('seismic',5)
    else:
        cmap=cmap
    row=int(np.sqrt(acc.shape[0])); col=int(np.sqrt(acc.shape[0]));

    redrat = 3.6;
    i=0; fs=6*redrat;
    # figsize=6
    fig, ax = plt.subplots(row, col,figsize=(2*redrat,2*redrat))
    for ii in range(row):
        for kk in range(col):
            score = acc[i]
            
            labeled_array, num_features = label(acc[i]>threshold,structure=structure)
            cluster_sizes = np.array([np.sum(labeled_array == j) for j in range(1, num_features + 1)])
            inds = np.where(cluster_sizes>maxcluster)[0]
            la=np.zeros(labeled_array.shape)==1
            for j,ind in enumerate(inds):
                la = (la) | (labeled_array==ind+1)
            
            
            
            im = ax[ii][kk].imshow(score, interpolation='gaussian',origin='lower', cmap=cmap,
                           extent=times[[0, -1, 0, -1]], vmin=vmin, vmax=vmax)

            ax[ii][kk].contour(la, levels=1, colors='white',origin='lower',linestyles='dashed',
                               alpha=1,extent=times[[0, -1, 0, -1]],linewidths=1)
            ax[ii][kk].set_xticks(tt)
            ax[ii][kk].set_yticks(tt)
            if ii==1: 
                ax[ii][kk].set_xticklabels(ttlabel,fontsize=fs) 
            else: 
                ax[ii][kk].set_xticklabels([],fontsize=fs)
            if kk==0: 
                ax[ii][kk].set_yticklabels(ttlabel,fontsize=fs) 
            else: 
                ax[ii][kk].set_yticklabels([],fontsize=fs)
            
            if kk==0:
                ax[ii][kk].set_ylabel('train time (s)',fontsize=fs)
            if ii==(col-1):
                ax[ii][kk].set_xlabel('test time (s)',fontsize=fs)
            
            ax[ii][kk].set_title('rank'+str(ii+1)+' -> rank'+str(kk+1),fontsize=fs)
            ax[ii][kk].spines['top'].set_visible(False)  # Remove top spine
            ax[ii][kk].spines['right'].set_visible(False)  # Remove right spine
            ax[ii][kk].spines['bottom'].set_visible(False)  # Remove bottom spine
            ax[ii][kk].spines['left'].set_visible(False)  # Remove left spine

            
            c = 'w'
            for j in range(len(tt)):
                ax[ii][kk].axvline(tt[j], c=c)
                ax[ii][kk].axhline(tt[j], c=c)
            i=i+1
    
    cbar = plt.colorbar(im, ax=ax,shrink=0.4,anchor=(2,0.49))
    cbar.outline.set_visible(False)
    cbar.set_label('decoding accuracy',fontsize=fs,rotation=90,labelpad=-90,y=0.5)
    cbar.ax.tick_params(labelsize=fs)
    if len(title)>0: plt.suptitle(title,x=0.5,y=0.97,fontsize=fs);
    plt.subplots_adjust(wspace = 0.2, hspace = 0.2)
    
    
    if savefigpath!=0:
        plt.savefig(savefigpath, format='pdf', dpi=300, bbox_inches='tight')

    plt.show()



def ssplot(subspace_dat,titles,colors2,lss,lim,legnd,isrot=1):
    
    xys_L = subspace_dat['xys']
    c_uni = subspace_dat['label']
    c2_uni = subspace_dat['label2']
    
    redrat = 3.6; fs = 5 * redrat
    fig = plt.figure(figsize=[3.4* redrat,1* redrat])
    
    # fig=plt.figure(figsize=(4.5*3, 4))
    for rid in range(3):
        
        if isrot==1:
            xm = xys_L[rid,0,0].mean()
            ym = xys_L[rid,0,1].mean()
            xys_L[rid,:,0] = xys_L[rid,:,0]-xm
            xys_L[rid,:,1] = xys_L[rid,:,1]-ym

            if len(c2_uni)>1:
                vector =  xys_L[rid,1:,:,0].mean(0)
            elif len(c2_uni)==1:
                vector =  xys_L[rid,0,:,0]
            angle = np.arctan2(vector[0], vector[1])
            rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                        [np.sin(angle), np.cos(angle)]])
        elif isrot==0:
            rotation_matrix = np.array([[1,0],[0,1]])
        
#       
        alphas = (c2_uni)/c2_uni.max()
        plt.subplot(1,3,rid+1)
        for j in range(len(c2_uni)):
            xys_r = np.dot(rotation_matrix, xys_L[rid,j])
            for i in range(len(c_uni)):
                plt.scatter(x = xys_r[0,i], y=xys_r[1,i],c=colors[i],s=100,alpha=alphas[j])
            xs = np.append(xys_r[0,:],xys_r[0,0])
            ys = np.append(xys_r[1,:],xys_r[1,0])
            plt.plot(xs, ys,c=colors2[rid*len(c2_uni)+j],label=legnd[j],ls=lss[j])
            if (legnd!=0) & (rid==2): plt.legend(bbox_to_anchor=(0.5, 0., 0.9, 0.8),fontsize=fs-6,frameon=False)
            plt.title(titles[rid],fontsize=fs)
            plt.xlabel('PC1',fontsize=fs)
            plt.ylabel('PC2',fontsize=fs)
        if len(lim)==1:
            lim=lim[0]
            plt.ylim([-lim,lim]);plt.xticks(np.arange(-lim,lim+0.001,2*lim/4),fontsize=fs)
            plt.xlim([-lim,lim]);plt.yticks(np.arange(-lim,lim+0.001,2*lim/4),fontsize=fs)
        else:
            plt.ylim([-lim[rid],lim[rid]]);plt.xticks(np.arange(-lim[rid],lim[rid]+0.001,2*lim[rid]/4),fontsize=fs)
            plt.xlim([-lim[rid],lim[rid]]);plt.yticks(np.arange(-lim[rid],lim[rid]+0.001,2*lim[rid]/4),fontsize=fs)
        plt.gca().spines['top'].set_visible(False);plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(True);plt.gca().spines['left'].set_visible(True)
        #     plt.grid(True)
    plt.tight_layout()
    plt.show()

    return fig


def subspace_pcangle(latent, N=100, k_ratio=0.012, seed=42):
    # N: 随机采样次数，n_permutation
    # k: 每次采样数
    pairs_angle = [(0,1), (0,2), (1,2), (0,0), (1,1), (2,2)]
    rng = default_rng(seed)
    n_samples = [c.shape[0] for c in latent]
    k = [np.maximum(5,int(c.shape[0]*k_ratio)) for c in latent]
    
    print(f"adaptive k value (E, R1, R2): {k}")
    
    degs = np.zeros((N, len(pairs_angle)))
    for p, (i1, i2) in enumerate(pairs_angle):
        idx1 = rng.choice(n_samples[i1], size=(N, k[i1]), replace=True)
        idx2 = rng.choice(n_samples[i2], size=(N, k[i2]), replace=True)
        s1 = latent[i1][idx1]  # (N, k, n_neurons, n_latens)
        s2 = latent[i2][idx2]
        sbspce1 = s1.mean(axis=1) # (N, n_neurons, n_latens)
        sbspce2 = s2.mean(axis=1)
        for ii in range(N):
            angles_rad = subspace_angles(sbspce1[ii], sbspce2[ii]) # from scipy.linalg
            angles_deg = np.degrees(angles_rad)
            degs[ii, p] = angles_deg.mean()
            
    result = np.zeros((N + 1, len(pairs_angle) + 1))
    result[0, 1:] = [10*a + b + 11 for a, b in pairs_angle]
    result[1:, 0] = np.arange(N)
    result[1:, 1:] = degs
    return result



def vaf(sbspce1,sbspce2):
    # sbspce1, subspace to project
    # sbspce2, target subspace
    # subspace of size: n_locs x n_neurons

    if np.var(sbspce1, axis=0).sum() == 0:
        return 0.0
    # pm = np.dot(np.linalg.pinv(sbspce1.T), sbspce2.T).T # Compute the projection matrix
    pm = np.dot(np.linalg.pinv(sbspce1.T, rcond=1e-10), sbspce2.T).T
    proj_sbspce = np.dot(pm, sbspce1) # Project subspace 2 onto subspace 1
    proj_var = np.var(proj_sbspce, axis=0).sum()
    total_var = np.var(sbspce1, axis=0).sum()
    ratio = proj_var / total_var
    
    return min(ratio, 1.0 / ratio) if ratio > 0 else 0.0

def subspace_vaf(coef, N=100, k_ratio=0.012, seed=42):
    # N: 随机采样次数，n_permutation
    # k: 每次采样数
    pairs_vaf = [
        (0,1), (1,0), (0,2), (2,0), (1,2), (2,1), (0,0), (1,1), (2,2)
    ]

    rng = default_rng(seed)
    n_samples = [c.shape[0] for c in coef]
    k = [np.maximum(5,int(c.shape[0]*k_ratio)) for c in coef]
    print(f"adaptive k value (E, R1, R2): {k}")
    vafs = np.zeros((N, len(pairs_vaf)))
    for p, (i1, i2) in enumerate(pairs_vaf):
        idx1 = rng.choice(n_samples[i1], size=(N, k[i1]), replace=True)   # 有放回
        idx2 = rng.choice(n_samples[i2], size=(N, k[i2]), replace=True)
        s1 = coef[i1][idx1]          # (N, k, n_locs, n_neurons)
        s2 = coef[i2][idx2]
        sbspce1 = s1.mean(axis=1)    # (N, n_locs, n_neurons)
        sbspce2 = s2.mean(axis=1)
        for ii in range(N):
            vafs[ii, p] = vaf(sbspce1[ii], sbspce2[ii])
            
    result = np.zeros((N + 1, len(pairs_vaf) + 1))
    result[0, 1:] = [10*a + b + 11 for a, b in pairs_vaf]
    result[1:, 0] = np.arange(N)
    result[1:, 1:] = vafs
    return result


def subspace_relplot(vafs_L,degs_L):
    redrat = 3.6;fs = 6 * redrat

    labels_vaf=['E-R1','R1-E','E-R2','R2-E','R1-R2','R2-R1','E-E','R1-R1','R2-R2']
    fig1 = plt.figure(figsize=[3* redrat,1.7* redrat])
    c = vafs_L[0,1:]
    # plt.violinplot(vafs_L[1:,1:],positions=range(len(c)));
    plt.boxplot((vafs_L[1:,1:]),positions=range(len(c)));
    plt.xticks(range(len(c)),labels=labels_vaf,rotation=30,fontsize=fs);
    plt.yticks([0,0.2,0.4,0.6,0.8,1],fontsize=fs);plt.ylim([-0.1,1.1])
    plt.ylabel('VAF ratio',fontsize=fs)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)


    labels_angle_between = ['E-R1', 'E-R2', 'R1-R2']
    labels_angle_within  = ['E-E', 'R1-R1', 'R2-R2']
    fig, ax = plt.subplots(figsize=[1.5*redrat,1.7*redrat])
    data=degs_L[1:,[4,5,6]]
    x = range(3);y=data.mean(0);y_err=data.std(0)
    ax.plot(x,y,c='k',lw=2, linestyle='--')
    ax.errorbar(x, y, yerr=y_err, linestyle='--', capsize=0,c='k',lw=2)
    ax.set_ylabel('Principle Angle (°) ',c='k',fontsize=fs)
    ax.set_xticks(x);ax.set_xlim([-0.5,2.5])
    ax.set_xticklabels(labels_angle_within,c='k',fontsize=fs)
    ax.set_ylim([-10,100]);ax.set_yticks([0,30,60,90]);ax.set_yticklabels(['0','30','60','90'],fontsize=fs)
    
    ax.set_xlabel('within subspaces',fontsize=fs,c='k')
    axt = ax.twiny()
    data=degs_L[1:,[1,2,3]]
    
    x = range(3);y=data.mean(0);y_err=data.std(0)
    axt.plot(x,y,c='k',lw=2, linestyle='-')
    axt.errorbar(x, y, yerr=y_err, linestyle='-', capsize=0,c='k',lw=2)
    # axt.set_yticks([0,5,10]);
    # axt.set_xlabel('within subspaces')
    axt.set_xticks(x);axt.set_xlim([-0.5,2.5])
    axt.set_xticklabels(labels_angle_between,fontsize=fs)
    axt.set_xlabel('between subspaces',fontsize=fs,c='k')
    fig.patch.set_facecolor('white')
    return fig1, fig


def subspace_rel2plot(vafs_L,degs_L):
    redrat = 3.6; fs = 6 * redrat
    fig1 = plt.figure(figsize=[3* redrat,1.7* redrat])
    
    clb=['Ev-Ev','M1v-M1v','M2v-M2v','Ev-Es','M1v-M1s','M2v-M2s',
         'Es-Es','M1s-M1s','M2s-M2s','Es-Ev','M1s-M1v','M2s-M2v']
    c = vafs_L[0,1:]
    # plt.violinplot(vafs_L[1:,1:],positions=range(len(c)));
    plt.boxplot((vafs_L[1:,1:]),positions=range(len(c)));
    plt.xticks(range(len(c)),labels=clb,rotation=30,fontsize=fs);
    plt.yticks([0,0.2,0.4,0.6,0.8,1],fontsize=fs);plt.ylim([-0.1,1.1])
    plt.ylabel('VAF ratio',fontsize=fs)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)

    
    fig, ax = plt.subplots(figsize=[1.5*redrat,1.7*redrat])
    data=degs_L[1:,[1,2,3]]
    x = range(3);y=data.mean(0);y_err=data.std(0)
    ax.plot(x,y,c='k',label='v-v', linestyle='--')
    ax.errorbar(x, y, yerr=y_err, linestyle='--', capsize=0,c='k')

    # data=degs_L[1:,[4,5,6]]
    # x = range(3);y=data.mean(0);y_err=data.std(0)
    # ax.plot(x,y,ls='--',c='gray',label='s-s')
    # ax.errorbar(x, y, yerr=y_err, linestyle='-', capsize=0,c='gray')

    
    ax.set_ylabel('Principle Angle (°) ',c='k',fontsize=fs)
    ax.set_xticks(x)
    ax.set_xticklabels(['Ev-Ev','M1v-M1v','M2v-M2v'],c='k')
    ax.set_ylim([-10,100]);ax.set_yticks([0,30,60,90]);
    ax.set_xticks(x);ax.set_xlim([-0.5,2.5])
    ax.set_xlabel('within subspaces',fontsize=fs,c='k')
    plt.xticks(fontsize=fs);plt.yticks(fontsize=fs)
    
    axt = ax.twiny()
    data=degs_L[1:,[7,8,9]]
    x = range(3);y=data.mean(0);y_err=data.std(0)
    axt.plot(x,y,c='k')
    axt.errorbar(x, y, yerr=y_err, linestyle='-', capsize=0,c='k')
    # axt.set_yticks([0,5,10]);
    # axt.set_xlabel('within subspaces')
    axt.set_xticks(x);axt.set_xlim([-0.5,2.5])
    axt.set_xticklabels(['Ev-Es','M1v-M1s','M2v-M2s']);
    axt.set_xlabel('between subspaces',fontsize=fs,c='k')
    plt.xticks(fontsize=fs);plt.yticks(fontsize=fs)
    fig.patch.set_facecolor('white')
    return fig1, fig





###  single neuron plot



def iplot_location(data,Params,neuID,rid,fontsize):
    seqIDs0 = data['seqID']; respIDs0 =  data['respID']
    tconstrasts0 = data['tconstrast']; epochs0 = data['epoch'][:,neuID,:].mean(1)

    times = Params['times']; tt = Params['tt']
    
    picks = respIDs0[:,rid]!=0 # pick responded trials
    
    seqIDs = seqIDs0[picks]; respIDs = respIDs0[picks]
    tconstrasts = tconstrasts0[picks]; epochs = epochs0[picks]
    
    
    c1 = seqIDs[:,rid]; c2 = tconstrasts[:,rid]; c3 = respIDs[:,rid];
    c1uni = np.unique(c1); c2uni = np.unique(c2)
    for ii in range(len(c1uni)):
        epochm = epochs[(c1==c1uni[ii])&(c2!=c2uni[0])&(c1==c3),:]
        print(len(epochm),end=',')
        x=times;y=epochm.mean(0);yerr=epochm.std(0)/np.sqrt(len(epochm))
        plt.plot(x,y,lw=1,label=str(ii+1))
        plt.fill_between(x, y-yerr, y+yerr, alpha=0.2)
    plt.xticks(fontsize=fontsize);plt.yticks(fontsize=fontsize)
    print('')
    plt.axvline(tt[0],c='k',ls=':',lw=1)
    plt.axvline(tt[1],c='k',ls=':',lw=1)

    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)













