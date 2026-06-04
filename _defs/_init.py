## default settings
import os
import os.path as op
import glob
import h5py
import random
import time
import pickle
import shutil
from tabulate import tabulate

## plot package
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import cm
# blue,orange,green,red,purple,
# brown,pink,gray,yellow-green,cyan
colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728',
         '#9467bd','#8c564b','#e377c2','#7f7f7f',
         '#bcbd22','#17becf']
import seaborn as sns


## data strcuture package
import numpy as np
from numpy.random import default_rng
import pandas as pd


## scipy package
import scipy
import scipy.io
import scipy.io as sio
from scipy.ndimage import gaussian_filter,label,find_objects

from scipy import signal
from scipy.signal import correlate2d
from scipy.signal import convolve
from scipy.signal import find_peaks

from scipy import stats
from scipy.stats import pearsonr, spearmanr, norm, zscore

from scipy.optimize import curve_fit
from scipy.linalg import svd, subspace_angles


import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

import sklearn
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression,Lasso,LassoLars,SGDClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.decomposition import IncrementalPCA

from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn import manifold,feature_selection
from sklearn.feature_selection import SelectKBest, chi2, RFE

from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer


currentpath = os.getcwd()
print('currentpath: ', currentpath)
cpkeys = currentpath.split('/')
subjID = cpkeys[4]; date = cpkeys[-3]; anatype = cpkeys[-1];

if (subjID != 'group'):
    ROI = cpkeys[-4];
    datepath = '/'.join(cpkeys[:7])
    studypath = '/'.join(cpkeys[:6])
    print('studypath:',studypath)
    outputdir = currentpath+'/data'
    if not os.path.exists(outputdir): os.makedirs(outputdir)
    gdatapath = datepath+'/gdata'
    if not os.path.exists(gdatapath): os.makedirs(gdatapath)
    markerFile=gdatapath+'/eventTimes.mat'
    if (subjID == '2019')|(subjID == '0239'):
        logpath = '/mnt/sda/TP_CON_raw/'+subjID+'/'+ROI+'/_logs'
    
        if date!='session':
            rawpath = '/mnt/sda/TP_CON_raw/'+subjID+'/'+ROI+'/'+date
            markerPath = rawpath+'/marker/Episode001.h5'
            matPath = rawpath+'/matlab'
            rawFilePath = rawpath+'/tpdata/Image_001_001.raw'
    
            h5FilePath = gdatapath+'/Image_001_001.h5'
            # dataPath = gdatapath+'/'+anatype[3:]+'/plane0'
            dataPath = gdatapath+'/s2pmcorr/plane0'

    elif subjID == 'groot':
        logpath = '/mnt/backup2/ephys_CON_raw/'+subjID+'/_logs'
        
        if date!='session':
            rawpath = '/mnt/backup2/ephys_CON_raw/'+subjID+'/'+date
            
            rawh5Path = gdatapath+'/raw_orig.h5'
            # dataPath = gdatapath+'/'+anatype[3:]
            dataPath = gdatapath+'/analysis'
            resh5Path = dataPath+'/raw_res.h5'
            preph5Path = dataPath+'/raw_prep.h5'
            spikeh5Path = dataPath+'/raw_spk.h5'
            muah5Path = dataPath+'/raw_mua.h5'
            
        ch_names = [f'PFC{i+1:03d}' if i < 160 else f'PPC{i+1-160:03d}' for i in range(256)]
        ch_types = [f'eeg' for i in range(256)]
    
elif (subjID == 'group'):
    studypath = '/'.join(cpkeys[:4])
    outputdir = currentpath+'/data'
    if not os.path.exists(outputdir): os.makedirs(outputdir)
    
def subjParams(animID):
    # sfel=1000; # sampling frequency for eyelink data
    rfr=60 #  refresh rate of stimulus display
    
    if animID == 'groot':
        animName2='M3'
        animName = 'Monkey 3'
        prestimDur=30; stimdur=2; mskSOA=3;maskdur=15;ISI=48;
        prestimDur=prestimDur/rfr;
        sftp = 100  # sampling frequency for downsampled FR
        t1 = 0; t2 = int(sftp*3.5)
        tr1 = 5; tr2 = 30 # sample period 50ms - 600ms
        tc1 = 50; tc2 = 150
        baseline_window = [0,40] # -400ms ~ 0ms

    elif animID == 'groot2':
        animName2='M3'
        animName = 'Monkey 3'
        prestimDur=30; stimdur=2; mskSOA=3;maskdur=15;ISI=48;
        prestimDur=prestimDur/rfr;
        sftp = 1000  # sampling frequency for downsampled FR
        t1 = int(-0.5*sftp); t2 = int(3.5*sftp)
        tr1 = 5; tr2 = 30 # sample period 50ms - 600ms
        baseline_window = [0,40] # -400ms ~ 0ms

    elif animID == '0239':
        animName2='M1'
        animName = 'Monkey 1'
        prestimDur=72; stimdur=1; mskSOA=3;maskdur=15;ISI=60;
        prestimDur=prestimDur/rfr+0.1;
        sftp = 30 # sampling frequency for two-photon imaging
        t1 = 0; t2 = int(sftp*6)
        tr1 = 5; tr2 = 25  # sample period 150ms - 600ms
        tc1 = 35; tc2 = 70
        baseline_window=[0,35]
        
    elif animID == '2019':
        animName2='M2'
        animName = 'Monkey 2'
        prestimDur=60; stimdur=3; mskSOA=3;maskdur=15;ISI=48;
        prestimDur=prestimDur/rfr+0.1;
        sftp = 30 # sampling frequency for two-photon imaging
        t1 = 0; t2 = int(sftp*5)
        tr1 = 5; tr2 = 25  # sample period 150ms - 600ms
        tc1 = 30; tc2 = 70
        baseline_window=[0,25] # -800ms 
        
    T1ONset=prestimDur;TDur=(stimdur+mskSOA+maskdur)/rfr;
    T2ONset=T1ONset+TDur+ISI/rfr;
    
    # tt1=[T1ONset,T1ONset+TDur+ISI/60];
    # tp=np.round(tt*sftp); 
    # tp1=np.round(tt1*sftp)
    tt=[T1ONset,T2ONset,T2ONset+TDur+ISI/rfr];
    tp=np.round(np.array(tt)*sftp)
    ttlabel = np.array(['T1','T2','DL']);

    times = np.arange(t1,t2,1)/sftp;
    times_cut = np.arange(-tc1,tc2,1)/sftp;
    
    Params = {'animID':animID,'animName':animName,'animName2':animName2,
              'sftp':sftp,'t1':t1,'t2':t2,'times':times,'times_cut':times_cut,
              'pDur':prestimDur,'sDur':TDur,'T1On':T1ONset,'T2On':T2ONset,'ISI':ISI/rfr,
              'tt':tt,'tp':tp,'ttlabel':ttlabel,'tr1':tr1,'tr2':tr2,'tc1':tc1,'tc2':tc2,
              'baseline_window':baseline_window}
    return Params





## save and load dictionary
def save_dictionary_pickle(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load_dictionary_pickle(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data



## preprocessing, filtering, detrending, etc.?





## epoching
def epoching(X,event_timings,t1,t2):
    # X - n_neurons x n_times
    # event_timings - n_trials
    # t1, t2 - time range
    epochs = []
    for ii in range(len(event_timings)):
        event_time = int(event_timings[ii])
        if (event_time+t2)>X.shape[1]:
            n = event_time+t2-X.shape[1]
            epoch_ii = np.concatenate([X[:,(event_time+t1):(X.shape[1])],np.zeros([len(X),n])],1)
        else:
            epoch_ii = X[:,event_time+t1:event_time+t2]
        epochs.append(epoch_ii)
    return np.array(epochs)

def zscale(X):
    # scale along n_times axis
    # X - n_trials x n_neuron x n_times
    X_scaled = np.zeros(X.shape)
    for i in range(X.shape[2]):
        scaler = StandardScaler()
        scaler.fit(X[:,:,i])
        X_scaled[:,:,i] = scaler.transform(X[:,:,i])
    return X_scaled


def ifilt(X,win,po,axis=-1):
    # X - last dimension = n_times
    X_filt = signal.savgol_filter(X,window_length=win,polyorder=po,axis=-1)
    return X_filt

def pad_with_offset(arr, total_neurons, start_idx):
    # arr - n_trials x n_neurons x n_times
    padded = np.zeros((arr.shape[0], total_neurons, arr.shape[2]), dtype=arr.dtype)
    end_idx = start_idx + arr.shape[1]
    padded[:, start_idx:end_idx, :] = arr
    return padded


## regression
def tempReg(X,y):
    # X - n_samples x n_neurons x n_times
    # Y - n_samples
    coefs = [];r2scores=[]
    for ii in range(X.shape[2]):
        
        scaler = StandardScaler()
        scaler.fit(X[:,:,ii])
        X_scaled = scaler.transform(X[:,:,ii])

        Y_true = y

        clf = Lasso(alpha=0.05,max_iter=2000)
        clf.fit(X_scaled,Y_true)
        coef = clf.coef_

        Y_pred = clf.predict(X_scaled)
        r2score=sklearn.metrics.r2_score(Y_true,Y_pred)
        
        coefs.append(coef)
        r2scores.append(r2score)
        print(str(ii),end='')
    return np.array(coefs),np.array(r2scores)

def TLDA(X,y,iscale=True,islog=1):
    # X - n_trials x n_neuron x n_times
    # y - n_trials
    
    coefs = [];EVRs=[];COVs=[]
    for i in range(X.shape[2]):
        if iscale==True:
            scaler = StandardScaler()
            scaler.fit(X[:,:,i])
            X_scaled = scaler.transform(X[:,:,i])
        elif iscale ==False:
            X_scaled = X[:,:,i]
            
            
        clf = LinearDiscriminantAnalysis(solver='svd',store_covariance=True)
        clf.fit(X_scaled, y)
        coefs.append(clf.coef_)
        EVRs.append(clf.explained_variance_ratio_)
        COVs.append(clf.covariance_)
        if (islog==1)*(np.mod(i,20)==0): print(str(i),end='')
    return np.array(coefs), np.array(EVRs),np.array(COVs)
    
def LDA(X,y,iscale=True):
    # X - n_trials x n_neuron
    # y - n_trials
    if iscale==True:
        scaler = StandardScaler()
        scaler.fit(X)
        X_scaled = scaler.transform(X)
    elif iscale ==False:
        X_scaled = X

    clf = LinearDiscriminantAnalysis(solver='svd',store_covariance=True)
    clf.fit(X_scaled, y)
    coef = clf.coef_
    EVR = clf.explained_variance_ratio_
    COV = clf.covariance_
    
    return coef, EVR, COV

def TReg(X,y,iscale=True):
    # X - n_samples x n_neurons x n_times
    # Y - n_samples
    coefs = [];r2scores=[]
    for i in range(X.shape[2]):
        
        if iscale==True:
            scaler = StandardScaler()
            scaler.fit(X[:,:,i])
            X_scaled = scaler.transform(X[:,:,i])
        elif iscale ==False:
            X_scaled = X[:,:,i]

        Y_true = y

        clf = Lasso(alpha=0.05,max_iter=2000)
        clf.fit(X_scaled,Y_true)
        coef = clf.coef_

        Y_pred = clf.predict(X_scaled)
        r2score=sklearn.metrics.r2_score(Y_true,Y_pred)
        
        coefs.append(coef)
        r2scores.append(r2score)
        print(str(i),end='')
    return np.array(coefs),np.array(r2scores)


def MG(X,y,X_test,n_latents=2):
    # multivariate gaussian (MG)
    # X - n_samples x n_features
    # y - n_samples
    # n_latents - dimensionality of latent space 
    
    n_samples, n_features = X.shape
    classes,class_counts = np.unique(y,return_counts=True)
    n_classes = classes.shape[0]
    class_ratios = class_counts/y.shape[0]
    priors = class_ratios


    means = np.zeros([n_classes,X.shape[1]])
    for idx, iclass in enumerate(classes):
        means[idx, :] = X[y == iclass].mean(0)

    # overall mean, weighted mean of the class means using the prior probabilities
    xbar = priors @ means 

    # centered data matrix where each sample is subtracted by the mean of its class
    Xc = []
    for idx, iclass in enumerate(classes):
        Xg = X[y == iclass]
        Xc.append(Xg - means[idx, :])
    Xc = np.concatenate(Xc, axis=0)

    # 1) within (univariate) scaling by with classes std-dev
    std = np.std(Xc, axis=0)
    std[std == 0] = 1.0 # avoid division by zero in normalization
    fac = 1.0 / (n_samples - n_classes)

    # 2) Within variance scaling
    Xw = np.sqrt(fac) * (Xc / std)
    # SVD of centered (within)scaled data
    U, S, Vt = svd(Xw, full_matrices=False)

    tol = 1.0e-4 # for 'svd'
    rank = sum(S > tol)

    # Scaling of within covariance is: V' 1/S
    scalings = (Vt[:rank, :] / std).T / S[:rank]
    fac = 1.0 / (n_classes - 1)

    # 3) Between variance scaling
    # Scale weighted centers
    Xb = ((np.sqrt(n_samples * priors) * fac) * (means - xbar).T).T @ scalings
    _, S, Vt = svd(Xb, full_matrices=False)

    explained_variance_ratio_ = (S**2 / np.sum(S**2))
    rank = sum(S > tol * S[0])

    # transformation matrix for projecting data into the latent space
    latent = scalings @ Vt.T[:, :rank]
    latent = latent[:,:n_latents]

    coef = (means - xbar) @ latent
    coef = coef @ latent.T
    
    X_new = (X_test - xbar) @ latent
    
    return X_new, coef, latent, explained_variance_ratio_[:n_latents]

def MG_transform(X,y, X_test, n_latents=2):
    # multivariate gaussian (MG)
    # X - n_samples x n_features
    # y - n_samples
    # n_latents - dimensionality of latent space 
    
    n_samples, n_features = X.shape
    classes,class_counts = np.unique(y,return_counts=True)
    n_classes = classes.shape[0]
    class_ratios = class_counts/y.shape[0]
    priors = class_ratios


    means = np.zeros([n_classes,X.shape[1]])
    for idx, iclass in enumerate(classes):
        means[idx, :] = X[y == iclass].mean(0)

    # overall mean, weighted mean of the class means using the prior probabilities
    xbar = priors @ means 

    # centered data matrix where each sample is subtracted by the mean of its class
    Xc = []
    for idx, iclass in enumerate(classes):
        Xg = X[y == iclass]
        Xc.append(Xg - means[idx, :])
    Xc = np.concatenate(Xc, axis=0)

    # 1) within (univariate) scaling by with classes std-dev
    std = np.std(Xc, axis=0)
    std[std == 0] = 1.0 # avoid division by zero in normalization
    fac = 1.0 / (n_samples - n_classes)

    # 2) Within variance scaling
    Xw = np.sqrt(fac) * (Xc / std)
    # SVD of centered (within)scaled data
    U, S, Vt = svd(Xw, full_matrices=False)

    tol = 1.0e-4 # for 'svd'
    rank = sum(S > tol)

    # Scaling of within covariance is: V' 1/S
    scalings = (Vt[:rank, :] / std).T / S[:rank]
    fac = 1.0 / (n_classes - 1)

    # 3) Between variance scaling
    # Scale weighted centers
    Xb = ((np.sqrt(n_samples * priors) * fac) * (means - xbar).T).T @ scalings
    _, S, Vt = svd(Xb, full_matrices=False)

    explained_variance_ratio_ = (S**2 / np.sum(S**2))
    rank = sum(S > tol * S[0])

    # transformation matrix for projecting data into the latent space
    latent = scalings @ Vt.T[:, :rank]
    latent = latent[:,:n_latents]

    coef = (means - xbar) @ latent
    coef = coef @ latent.T
    
    X_new = (X_test - xbar) @ latent
    
    return X_new, coef, latent, explained_variance_ratio_[:n_latents]



## statistics
def temp_ttest(data1,data2,ttype='ind'):
    # data: n_sample x n_time
    # ttype = 'ind' or 'rel'
    ntime=data1.shape[1]
    ts=[];ps=[]
    for i in range(ntime):
        if ttype=='ind':
            t, p = stats.ttest_ind(data1[:,i], data2[:,i])
        elif ttype=='rel':
            t, p = stats.ttest_rel(data1[:,i], data2[:,i])
        elif ttype=='1samp':
            t, p = stats.ttest_1samp(data1[:,i],popmean=0)
        ts.append(t);ps.append(p)
    return np.array(ts),np.array(ps)






## plot

def rplot(X,times,vmin,vmax,Params,title=''):
    ## plot regression results

    times=Params['times'];tt = Params['tt'];ttlabel=Params['ttlabel']
    
    fs=12;extent=[0,6,times[0],times[-1]]
    xlabel = 'no.Neuron';

    rows = 1; cols = len(X); figsize = 5
    fig, ax = plt.subplots(rows,cols,figsize=[figsize*cols,figsize*rows])
    for i in range(cols):
        im=ax[i].imshow(X[i],vmin=vmin,vmax=vmax,extent=extent,origin='lower');
        if i == 0:
            ax[i].set_xlabel(xlabel,fontsize=fs);
        ax[i].set_xticks([]);
        if i==0:
            ax[i].set_yticks(tt);ax[i].set_yticklabels(ttlabel,fontsize=fs);
        else:
            ax[i].set_yticks([])
        
        ax[i].set_title(title+str(i+1),fontsize=fs)
        
        for ii in range(len(tt)):
            ax[i].axhline(tt[ii],c='w',ls='-',lw=1)

    cbar = plt.colorbar(im,ax=ax,shrink=0.3,anchor=(-0.2,0.49))
    cbar.set_label('β Coefficient',fontsize=fs/6*5,rotation=0,labelpad=0,y=1.4)
    cbar.ax.tick_params(labelsize=fs/3*2);
#     plt.subplots_adjust(wspace = 0.11, hspace = None)


























































