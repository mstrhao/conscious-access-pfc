from _defs._init import *


def popTSplot(reconsDA,Params,plotType='correct',smth=7,locIDs=[1]):
    """
    Parameters:
    reconsDA: 
    Params: 
    plotType: 'contrast', 'contrast_loc','correct','full'
    locIDs: for plotType='contrast_loc' only


    return:
    reconw, reconis
    """
    seqIDs_L = reconsDA['seqIDs_L']; respIDs_L = reconsDA['respIDs_L']; respIDms_L = reconsDA['respIDms_L']; 
    tconstrasts_L = reconsDA['tconstrasts_L']; holdTimes_L = reconsDA['holdTimes_L']; 
    recons_L = reconsDA['recons_L'];
    
    times=Params['times'];tt = Params['tt'];ttlabel = Params['ttlabel'];tp = Params['tp']
    tr1 = Params['tr1']; tr2 = Params['tr2'];sftp=Params['sftp']
    tc1 = Params['tc1']; tc2 = Params['tc2']
    times_cut = Params['times_cut']; animID = Params['animID']; animName=Params['animName']

    reconw = [];reconis=[]
    redrat = 3;fs = 7 * redrat    
    if plotType=='contrast':

        c1l=['0%','4%','8%','15%','100%']
        reds = [ "gray", "gray", "k", "brown", "red"]
        lss = ['--','-','-','-','-']
        cmpn = ['shared item','rank1','rank2']
        fig = plt.figure(figsize=[10,3*2]); pn=1
        for j in range(3):
            if j==0: reconiNum=[]
            for k in range(2):
                
                if (j==0) | ((j==1)&(k==0)) | ((j==2)&(k==1)):
                    if pn<=2: plt.subplot(2,2,2*pn-1);
                    elif pn==3: plt.subplot(2,2,pn-1);
                    elif pn==4: plt.subplot(2,2,pn);
                    pn=pn+1
                    plt.title(cmpn[j]+' subspace --> T'+str(k+1),fontsize=15)
                    p = ((seqIDs_L[k] != 0) )& ((seqIDs_L[k]==respIDs_L[k]) | (tconstrasts_L[k]==np.unique(tconstrasts_L[k])[0]))
                    seqID = seqIDs_L[k][p]
                    respID = respIDs_L[k][p]
                    tcon = tconstrasts_L[k][p]
                    recon = recons_L[k][:,:,p,:]
                    recon = ifilt(recon,smth,0)
        
                    ci = tcon; ciuni=np.unique(ci)
                    for i in range(len(ciuni)):                            
                        reconi=[]
                        for l in range(len(np.unique(seqID))):
                            p = (ci==ciuni[i]) & (seqID==np.unique(seqID)[l])
                            reconi.append(recon[l,j,p,:])
                        reconi = np.concatenate(reconi,axis=0)
                        
                        if j==0:
                            reconw.append(reconi[:,int(tp[k]+tr1):int(tp[k]+tr2)].mean(1))
                        else:
                            reconw.append(reconi[:,int(tp[k]+tr2):-20].mean(1))
                        print(c1l[i],',',len(reconi),end=', ')
                        
                        x=times;y=reconi.mean(0);yerr=reconi.std(0)/np.sqrt(len(reconi))
                        plt.plot(x,y,label=c1l[i],c=reds[i], linestyle=lss[i],lw=1.5)
                        
                        if j == 0: plt.ylabel('Decoding accuracy',fontsize=15)
                        if (pn == 3)|(pn==5): plt.xticks(tt[:2],labels=ttlabel[:2],fontsize=15)
                        else: plt.xticks([])
                        if pn==2: plt.legend(title='',frameon=False,fontsize=11);
                    for ii in range(len(tt)-1):
                        plt.axvline(tt[ii],c='k',ls='--',lw=1,alpha=0.3)
                    plt.axhline(1/6,c='k',ls='--',lw=1,alpha=0.3)
                    plt.axvline(int(tp[k]+tr1)/sftp,c='k',ls='--',lw=1)
                    plt.axvline(int(tp[k]+tr2)/sftp,c='k',ls='--',lw=1)
                    plt.yticks(fontsize=15)
                    print(';')


    elif plotType=='contrast2':
        c1l = ['0%', '4%', '8%', '15%', '100%']
        reds = ["gray", "gray", "k", "brown", "red"]
        lss = ['--', '-', '-', '-', '-']
        cmpn = ['shared item', 'rank1', 'rank2']
        
        # ====================== 数据处理 + 画图 ======================
        fig = plt.figure(figsize=[13, 6])
        plot_count = 0
        
        # 用于存储合并后的数据（按面板和contrast）
        merged_data = {0: {}, 1: {}}   # panel 0: 左图, panel 1: 右图
        
        for j in range(3):
            for k in range(2):
                if not ((j == 0) | ((j == 1) and (k == 0)) | ((j == 2) and (k == 1))):
                    continue
                
                panel_idx = 0 if plot_count <= 1 else 1
                
                p = ((seqIDs_L[k] != 0)) & ((seqIDs_L[k] == respIDs_L[k]) | 
                                            (tconstrasts_L[k] == np.unique(tconstrasts_L[k])[0]))
                
                seqID = seqIDs_L[k][p]
                tcon = tconstrasts_L[k][p]
                recon = recons_L[k][:, :, p, :]
                recon = ifilt(recon, smth, 0)
                
                ciuni = np.unique(tcon)
                seq_unique = np.unique(seqID)
                
                for i, contrast in enumerate(ciuni):
                    reconi_list = []
                    for l_idx in range(len(seq_unique)):
                        p_cond = (tcon == contrast) & (seqID == seq_unique[l_idx])
                        reconi_list.append(recon[l_idx, j, p_cond, :])
                    
                    reconi = np.concatenate(reconi_list, axis=0)
                    
                    # 窗口截取（按你最新版本）
                    t_start = int(tp[k] - tc1)
                    t_end   = int(tp[k] + tc2)
                    window = reconi[:, t_start:t_end]
                    
                    # 存入对应面板的相同contrast
                    cond_key = c1l[i]
                    if cond_key not in merged_data[panel_idx]:
                        merged_data[panel_idx][cond_key] = []
                    merged_data[panel_idx][cond_key].append(window)
                
                plot_count += 1
        
        # ====================== 绘图 ======================

        dats=[]; nts=[]
        for panel_idx in [0, 1]:
            ax = plt.subplot(1, 2, panel_idx + 1)
            
            title = "entry" if panel_idx == 0 else "rank"
            plt.title(title, fontsize=16)

            dat=[];nt=[]
            for i, contrast_name in enumerate(c1l):
                if contrast_name in merged_data[panel_idx]:
                    # 合并相同contrast的所有数据
                    all_windows = merged_data[panel_idx][contrast_name]
                    merged_window = np.concatenate(all_windows, axis=0)   # 合并 trials
                    
                    y = merged_window.mean(0)
                    n = merged_window.shape[0]
                    yerr = merged_window.std(0) / np.sqrt(max(n, 1))

                    dat.append(y); nt.append(n)
                    x = times_cut
                    
                    plt.plot(x, y, 
                             label=f"{contrast_name} (n={n})", 
                             color=reds[i], 
                             linestyle=lss[i], 
                             lw=2.2)
                    
                    # 保存reconw（每个contrast合并后的窗口平均）
                    reconw.append(merged_window.mean(1))
            dats.append(np.array(dat))
            nts.append(np.array(nt))
            
            plt.axhline(1/6, c='k', ls='--', lw=1, alpha=0.3)
            plt.axvline(0, c='k', ls='--', lw=1, alpha=0.3)
            if panel_idx == 0:
                plt.ylabel('Decoding accuracy', fontsize=15)
            
            plt.xticks(fontsize=13)
            plt.yticks(fontsize=15)
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
        
        plt.legend(title='', frameon=False, fontsize=11, loc='best')
        plt.tight_layout()
        plt.show()
        
        plot_data = {'c1l':c1l, 'reds':reds,'lss':lss, 'times_cut':times_cut, 'dats':dats, 'nts':nts}
        save_dictionary_pickle(plot_data, outputdir+'/contrastDynamics_'+animID+'.pkl')
    
    elif plotType=='contrast_loc':
        c1l=['0%','4%','8%','15%','100%']
        reds = [ "gray", "gray", "k", "brown", "red"]
        lss = ['--','-','-','-','-']
        cmpn = ['shared item','rank1','rank2']
        fig = plt.figure(figsize=[10,3*2]); pn=1
        for j in range(3):
            if j==0: reconiNum=[]
            for k in range(2):
                
                if (j==0) | ((j==1)&(k==0)) | ((j==2)&(k==1)):
                    if pn<=2: plt.subplot(2,2,2*pn-1);
                    elif pn==3: plt.subplot(2,2,pn-1);
                    elif pn==4: plt.subplot(2,2,pn);
                    pn=pn+1
                    plt.title(cmpn[j]+' subspace --> T'+str(k+1),fontsize=15)
                    p0 = (seqIDs_L[k]==locIDs[0])
                    if len(locIDs)>1:
                        for i in range(len(locIDs)-1):
                             p0=p0 | (seqIDs_L[k]==locIDs[i+1])
                       
                    p = (seqIDs_L[k] != 0) & (((seqIDs_L[k]==respIDs_L[k]) & p0 )| (tconstrasts_L[k]==np.unique(tconstrasts_L[k])[0]))
                        
                    seqID = seqIDs_L[k][p]
                    respID = respIDs_L[k][p]
                    tcon = tconstrasts_L[k][p]
                    recon = recons_L[k][:,:,p,:]
                    recon = ifilt(recon,smth,0)
        
                    ci = tcon; ciuni=np.unique(ci)
                    for i in range(len(ciuni)):                            
                        reconi=[]
                        for l in range(len(np.unique(seqID))):
                            p = (ci==ciuni[i]) & (seqID==np.unique(seqID)[l])
                            reconi.append(recon[l,j,p,:])
                        reconi = np.concatenate(reconi,axis=0)
                        
                        if j==0:
                            reconw.append(reconi[:,int(tp[k]+tr1):int(tp[k]+tr2)].mean(1))
                        else:
                            reconw.append(reconi[:,int(tp[k]+tr2):-20].mean(1))
                        print(c1l[i],',',len(reconi),end=', ')
                        
                        x=times;y=reconi.mean(0);yerr=reconi.std(0)/np.sqrt(len(reconi))
                        plt.plot(x,y,label=c1l[i],c=reds[i], linestyle=lss[i],lw=1.5)
                        
                        if j == 0: plt.ylabel('Decoding accuracy',fontsize=15)
                        if (pn == 3)|(pn==5): plt.xticks(tt[:2],labels=ttlabel[:2],fontsize=15)
                        else: plt.xticks([])
                        if pn==2: plt.legend(title='',frameon=False,fontsize=11);
                    for ii in range(len(tt)-1):
                        plt.axvline(tt[ii],c='k',ls='--',lw=1,alpha=0.3)
                    plt.axhline(1/6,c='k',ls='--',lw=1,alpha=0.3)
                    plt.axvline(int(tp[k]+tr1)/sftp,c='k',ls='--',lw=1)
                    plt.axvline(int(tp[k]+tr2)/sftp,c='k',ls='--',lw=1)
                    plt.yticks(fontsize=15)
                    print(';')

    elif plotType=='contrast_loc2':
        c1l = ['0%', '4%', '8%', '15%', '100%']
        reds = ["gray", "gray", "k", "brown", "red"]
        lss = ['--', '-', '-', '-', '-']
        cmpn = ['shared item', 'rank1', 'rank2']
        
        # ====================== 数据处理 + 画图 ======================
        fig = plt.figure(figsize=[13, 6])
        plot_count = 0
        
        # 用于存储合并后的数据（按面板和contrast）
        merged_data = {0: {}, 1: {}}   # panel 0: 左图, panel 1: 右图
        
        for j in range(3):
            for k in range(2):
                if not ((j == 0) | ((j == 1) and (k == 0)) | ((j == 2) and (k == 1))):
                    continue
                
                panel_idx = 0 if plot_count <= 1 else 1

                p0 = (seqIDs_L[k]==locIDs[0])
                if len(locIDs)>1:
                    for i in range(len(locIDs)-1):
                         p0=p0 | (seqIDs_L[k]==locIDs[i+1])
                       
                
                p = ((seqIDs_L[k] != 0)) & (((seqIDs_L[k]==respIDs_L[k]) & p0 ) | 
                                            (tconstrasts_L[k] == np.unique(tconstrasts_L[k])[0]))
                
                seqID = seqIDs_L[k][p]
                tcon = tconstrasts_L[k][p]
                recon = recons_L[k][:, :, p, :]
                recon = ifilt(recon, smth, 0)
                
                ciuni = np.unique(tcon)
                seq_unique = np.unique(seqID)
                
                for i, contrast in enumerate(ciuni):
                    reconi_list = []
                    for l_idx in range(len(seq_unique)):
                        p_cond = (tcon == contrast) & (seqID == seq_unique[l_idx])
                        reconi_list.append(recon[l_idx, j, p_cond, :])
                    
                    reconi = np.concatenate(reconi_list, axis=0)
                    
                    # 窗口截取（按你最新版本）
                    t_start = int(tp[k] - tc1)
                    t_end   = int(tp[k] + tc2)
                    window = reconi[:, t_start:t_end]
                    
                    # 存入对应面板的相同contrast
                    cond_key = c1l[i]
                    if cond_key not in merged_data[panel_idx]:
                        merged_data[panel_idx][cond_key] = []
                    merged_data[panel_idx][cond_key].append(window)
                
                plot_count += 1
        
        # ====================== 绘图 ======================
        dats=[]; nts=[]
        for panel_idx in [0, 1]:
            ax = plt.subplot(1, 2, panel_idx + 1)
            
            title = "entry" if panel_idx == 0 else "rank"
            plt.title(title, fontsize=16)

            dat=[];nt=[]
            for i, contrast_name in enumerate(c1l):
                if contrast_name in merged_data[panel_idx]:
                    # 合并相同contrast的所有数据
                    all_windows = merged_data[panel_idx][contrast_name]
                    merged_window = np.concatenate(all_windows, axis=0)   # 合并 trials
                    
                    y = merged_window.mean(0)
                    n = merged_window.shape[0]
                    yerr = merged_window.std(0) / np.sqrt(max(n, 1))

                    dat.append(y); nt.append(n)
                    x = times_cut
                    
                    plt.plot(x, y, 
                             label=f"{contrast_name} (n={n})", 
                             color=reds[i], 
                             linestyle=lss[i], 
                             lw=2.2)
                    
                    # 保存reconw（每个contrast合并后的窗口平均）
                    reconw.append(merged_window.mean(1))
            dats.append(np.array(dat))
            nts.append(np.array(nt))
            
            plt.axhline(1/6, c='k', ls='--', lw=1, alpha=0.3)
            plt.axvline(0, c='k', ls='--', lw=1, alpha=0.3)
            if panel_idx == 0:
                plt.ylabel('Decoding accuracy', fontsize=15)
            
            plt.xticks(fontsize=13)
            plt.yticks(fontsize=15)
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
        
        plt.legend(title='', frameon=False, fontsize=11, loc='best')
        plt.tight_layout()
        plt.show()
        
        plot_data = {'c1l':c1l, 'reds':reds,'lss':lss, 'times_cut':times_cut, 'dats':dats, 'nts':nts}
        save_dictionary_pickle(plot_data, outputdir+'/contrastDynamics_'+animID+'.pkl')
    
    elif plotType=='full':
        
        c1l=['100% correct']; cmpn = ['entry','rank1','rank2']; pn=1
        fig=plt.figure(figsize=[2.5*redrat,2*redrat]);
        
        for j in range(3):
            for k in range(2):
                if (j==0) | ((j==1)&(k==0)) | ((j==2)&(k==1)):
                    if pn<=2: plt.subplot(2,2,2*pn-1);
                    elif pn==3: plt.subplot(2,2,pn-1);
                    elif pn==4: plt.subplot(2,2,pn);
                    pn=pn+1
        
                    plt.title(cmpn[j]+' subspace --> T'+str(k+1))
                    for Li in range(1):
                        p = (respIDs_L[k] != 0)
                        seqID = seqIDs_L[k][p]; respID = respIDs_L[k][p]; tcon = tconstrasts_L[k][p]
                        recon = recons_L[k][:,:,p,:]; recon = ifilt(recon,smth,0)
        
                        if Li == 0:
                            p = (seqID == respID) & (tcon==np.unique(tcon)[-1])
                            ID = seqID
                            color=colors[3]
        
                        recon = recon[:,:,p,:];tcon = tcon[p]
                        seqID = seqID[p];respID = respID[p]; ID = ID[p]
        
                        reconi=[]
                        ci = tcon; ciuni=np.unique(ci)
                        for i in range(len(ciuni)):
                            for l in range(len(np.unique(ID))):
                                p = (ci==ciuni[i]) & (ID==np.unique(ID)[l])
                                reconi.append(recon[l,j,p,:])
                        reconi = np.concatenate(reconi,axis=0)
                        reconis.append(reconi)
        
                        if j==0: reconw.append(reconi[:,int(tp[k]+tr1):int(tp[k]+tr2)].mean(1))
                        else: reconw.append(reconi[:,int(tp[k]+tr2):-20].mean(1))
                        
                        print(c1l[Li],',',len(reconi),end=', ')
                        x=times;y=reconi.mean(0);yerr=reconi.std(0)/np.sqrt(len(reconi))
                        plt.plot(x,y,label=c1l[Li],color=color,lw=1)
                        plt.fill_between(x, y-yerr, y+yerr,color=color, alpha=0.2)
        
                        if j==0: plt.ylabel('decoding accuracy')
                        if (pn==3)|(pn==5): plt.xticks(tt[:2],labels=ttlabel[:2])
                        else: plt.xticks([])
                        if pn==2: plt.legend(frameon=False,loc='upper right');
                        for ii in range(len(tt)-1):
                            plt.axvline(tt[ii],c='k',ls='--',lw=1,alpha=0.3)
                        plt.axhline(1/6,c='k',ls='--',lw=1,alpha=0.3)
                        plt.axvline(int(tp[k]+tr1)/sftp,c='k',ls='--',lw=1)
                        plt.axvline(int(tp[k]+tr2)/sftp,c='k',ls='--',lw=1)
                    print(';')
    
    
    elif plotType=='correct': # sequence trials
        c1l=['correct']; cmpn = ['entry','rank1','rank2']; pn=1
        fig=plt.figure(figsize=[2.5*redrat,2*redrat]);
        for j in range(3):
            for k in range(2):
                if (j==0) | ((j==1)&(k==0)) | ((j==2)&(k==1)):
                    if pn<=2: plt.subplot(2,2,2*pn-1);
                    elif pn==3: plt.subplot(2,2,pn-1);
                    elif pn==4: plt.subplot(2,2,pn);
                    pn=pn+1
        
                    plt.title(cmpn[j]+' subspace --> T'+str(k+1))
                    for Li in range(1):
                        
                        
                        p1 = ((seqIDs_L[0][respIDms_L[0] != 0]==respIDs_L[0][respIDms_L[0] != 0]) 
                              & (seqIDs_L[1][respIDs_L[1] != 0]==respIDs_L[1][respIDs_L[1] != 0]))
                        
        
                        p = (respIDms_L[k] != 0) & (respIDs_L[k] != 0)
                        seqID = seqIDs_L[k][p][p1]; respID = respIDs_L[k][p][p1]; tcon = tconstrasts_L[k][p][p1]
                        recon = recons_L[k][:,:,p,:][:,:,p1,:]; recon = ifilt(recon,smth,0)
        
                        if Li == 0:
                            p = (seqID == respID)
                            ID = seqID
                            color=colors[3]
        
                        recon = recon[:,:,p,:];tcon = tcon[p]
                        seqID = seqID[p];respID = respID[p]; ID = ID[p]
        
                        reconi=[]
                        ci = tcon; ciuni=np.unique(ci)
                        for i in range(len(ciuni)):
                            for l in range(len(np.unique(ID))):
                                p = (ci==ciuni[i]) & (ID==np.unique(ID)[l])
                                reconi.append(recon[l,j,p,:])
                        reconi = np.concatenate(reconi,axis=0)
                        reconis.append(reconi)
        
                        if j==0: reconw.append(reconi[:,int(tp[k]+tr1):int(tp[k]+tr2)].mean(1))
                        else: reconw.append(reconi[:,int(tp[k]+tr2):-20].mean(1))
                        
                        print(c1l[Li],',',len(reconi),end=', ')
                        x=times;y=reconi.mean(0);yerr=reconi.std(0)/np.sqrt(len(reconi))
                        plt.plot(x,y,label=c1l[Li],color=color,lw=1)
                        plt.fill_between(x, y-yerr, y+yerr,color=color, alpha=0.2)
        
                        if j==0: plt.ylabel('decoding accuracy')
                        if (pn==3)|(pn==5): plt.xticks(tt[:2],labels=ttlabel[:2])
                        else: plt.xticks([])
                        if pn==2: plt.legend(frameon=False,loc='upper right');
                        for ii in range(len(tt)-1):
                            plt.axvline(tt[ii],c='k',ls='--',lw=1,alpha=0.3)
                        plt.axhline(1/6,c='k',ls='--',lw=1,alpha=0.3)
                        plt.axvline(int(tp[k]+tr1)/sftp,c='k',ls='--',lw=1)
                        plt.axvline(int(tp[k]+tr2)/sftp,c='k',ls='--',lw=1)
                    print(';')

    elif plotType == 'null':
        c1l=['response\n (0%)','stimulus\n (100%)','shuffle\n (0%)']
        cmpn = ['entry','rank1','rank2'];kl=[3,1,3];pn=1
        fig=plt.figure(figsize=[3*redrat,2.2*redrat]); 
        for j in range(3):
            for k in range(2):
                if (j==0) | ((j==1)&(k==0)) | ((j==2)&(k==1)):
                    if pn<=2: plt.subplot(2,2,2*pn-1);
                    elif pn==3: plt.subplot(2,2,pn-1);
                    elif pn==4: plt.subplot(2,2,pn);
                    pn=pn+1
                    plt.title(cmpn[j]+' subspace --> T'+str(k+1),fontsize=fs)
                    for Li in range(3):
                        t=tconstrasts_L[k]
                        p = (respIDs_L[k] != 0)
        
                        seqID = seqIDs_L[k][p]; respID = respIDs_L[k][p]; tcon = tconstrasts_L[k][p]
                        recon = recons_L[k][:,:,p,:]; recon = ifilt(recon,smth,0)
                        
                        if Li == 2:
                            p = (tcon==np.unique(tcon)[0])
                            ID = seqID
                            color='k'
                            lss='--'
                        elif Li == 1:
                            p = (seqID == respID) & (tcon==np.unique(tcon)[-1])
                            ID = seqID
                            color='k'
                            lss='-'
                        elif Li == 0:
                            p = (tcon==np.unique(tcon)[0])
                            ID = respID
                            color=colors[3]
                            lss='-'
                        
                        recon = recon[:,:,p,:];tcon = tcon[p]
                        seqID = seqID[p];respID = respID[p]; ID = ID[p]
                        
                        reconi=[]
                        ci = tcon; ciuni=np.unique(ci)
                        for i in range(len(ciuni)):
                            for l in range(6):
                                p = (ci==ciuni[i]) & (ID==np.unique(ID)[l])
                                reconi.append(recon[l,j,p,:])
                        reconi = np.concatenate(reconi,axis=0)
                        reconis.append(reconi)

                        if Li==0:
                            if j==0: reconw.append(reconi[:,int(tp[k]+tr1):int(tp[k]+tr2+tr2)].mean(1))
                            else: reconw.append(reconi[:,int(tp[k]+tr2+tr2):].mean(1))
                        else:
                            if j==0: reconw.append(reconi[:,int(tp[k]+tr1):int(tp[k]+tr2)].mean(1))
                            else: reconw.append(reconi[:,int(tp[k]+tr2):].mean(1))
                        
                        print(c1l[Li],',',len(reconi),end=', ')
                        
                        x=times;y=reconi.mean(0);yerr=reconi.std(0)/np.sqrt(len(reconi))
                        plt.plot(x,y,label=c1l[Li],color=color,lw=1,ls=lss)
                        plt.fill_between(x, y-yerr, y+yerr,color=color, alpha=0.2)
                        
                        if j==0: plt.ylabel('decoding accuracy',fontsize=fs)
                        if (pn==3)|(pn==5): plt.xticks(tt[:2],labels=ttlabel[:2],fontsize=fs)
                        else: plt.xticks([])
                        if pn==2: plt.legend(fontsize=fs-3,frameon=False,loc='upper right');
                        plt.axvline(tt[k],c='gray',ls=':',lw=1,alpha=0.2)
                        plt.axhline(1/6,c='gray',ls=':',lw=1,alpha=0.2)
                        plt.axvline(int(tp[k]+tr1)/sftp,c='k',ls='--',lw=1)
                        plt.axvline(int(tp[k]+tr2)/sftp,c='k',ls='--',lw=1)
                        plt.axvline(int(tp[k]+tr2+tr2)/sftp,c='k',ls='--',lw=1)
                        
                        plt.gca().spines['top'].set_visible(False);plt.gca().spines['right'].set_visible(False)
                        plt.gca().spines['bottom'].set_visible(True);plt.gca().spines['left'].set_visible(True)
                    print(';')

    elif plotType == 'null2':
        c1l=['response\n (0%)','stimulus\n (100%)','shuffle\n (0%)']
        cmpn = ['entry','rank1','rank2'];kl=[3,1,3];pn=1
        
        
        # ====================== 数据收集（合并前两个 & 后两个） ======================
        merged_data = {0: {0: [], 1: [], 2: []},  # panel 0 (左): 3个条件
                       1: {0: [], 1: [], 2: []}}  # panel 1 (右)
        
        plot_count = 0
        
        for j in range(3):
            for k in range(2):
                if not ((j == 0) | ((j == 1) and (k == 0)) | ((j == 2) and (k == 1))):
                    continue
                
                panel_idx = 0 if plot_count <= 1 else 1
                
                for Li in range(3):        # 3个条件：response, stimulus, shuffle
                    t = tconstrasts_L[k]
                    p = (respIDs_L[k] != 0)
                    seqID = seqIDs_L[k][p]
                    respID = respIDs_L[k][p]
                    tcon = tconstrasts_L[k][p]
                    recon = recons_L[k][:, :, p, :]
                    recon = ifilt(recon, smth, 0)
                    
                    if Li == 2:      # shuffle
                        p = (tcon == np.unique(tcon)[0])
                        ID = seqID
                        color = 'k'
                        ls_style = '--'
                    elif Li == 1:    # stimulus 100%
                        p = (seqID == respID) & (tcon == np.unique(tcon)[-1])
                        ID = seqID
                        color = 'k'
                        ls_style = '-'
                    elif Li == 0:    # response 0%
                        p = (tcon == np.unique(tcon)[0])
                        ID = respID
                        color = colors[3]      # 注意：colors 需要提前定义
                        ls_style = '-'
                    
                    recon = recon[:, :, p, :]
                    tcon = tcon[p]
                    seqID = seqID[p]
                    respID = respID[p]
                    ID = ID[p]
                    
                    reconi_list = []
                    ci = tcon
                    ciuni = np.unique(ci)
                    for i in range(len(ciuni)):
                        for l in range(6):
                            p_cond = (ci == ciuni[i]) & (ID == np.unique(ID)[l])
                            reconi_list.append(recon[l, j, p_cond, :])
                    
                    reconi = np.concatenate(reconi_list, axis=0)
                    reconi = reconi[:, int(tp[k] - tc1):int(tp[k] + tc2)]
                    
                    # 存入对应面板 + 对应条件
                    merged_data[panel_idx][Li].append(reconi)
                
                plot_count += 1
        
        # ====================== 绘图（两个大面板） ======================
        fig = plt.figure(figsize=[3.2 * redrat, 2.4 * redrat])
        
        dats = []; nts = []; dats_err=[]
        for panel_idx in [0, 1]:
            ax = plt.subplot(1, 2, panel_idx + 1)
            
            title = "entry" if panel_idx == 0 else "rank"
            plt.title(title, fontsize=fs)
            dat = []; nt = []; dat_err=[]
            for Li in range(len(c1l)):
                if merged_data[panel_idx][Li]:
                    all_reconi = merged_data[panel_idx][Li]
                    merged_reconi = np.concatenate(all_reconi, axis=0)   # 相同条件跨子图合并
                    
                    y = merged_reconi.mean(0)
                    n = merged_reconi.shape[0]
                    yerr = merged_reconi.std(0) / np.sqrt(max(n, 1))
                    
                    color = 'k' if Li in [1, 2] else colors[3]
                    ls_style = '--' if Li == 2 else '-'
        
                    nt.append(n)
                    dat.append(y)
                    dat_err.append(yerr)
                    plt.plot(times_cut, y, 
                             label=c1l[Li], 
                             color=color, 
                             ls=ls_style, 
                             lw=1.8)
                    
                    plt.fill_between(times_cut, y - yerr, y + yerr, 
                                     color=color, alpha=0.25)
            dats.append(np.array(dat));nts.append(np.array(nt))
            dats_err.append(np.array(dat_err))
            plt.axhline(1/6, c='gray', ls=':', lw=2, alpha=1)
            plt.axvline(0, c='gray', ls=':', lw=2, alpha=1)
            
            if panel_idx == 0:
                plt.ylabel('decoding accuracy', fontsize=fs)
                plt.legend(fontsize=fs-3, frameon=False, loc='upper right')
        
            
            plt.xticks(fontsize=fs-2)
            plt.yticks(fontsize=fs-2)
            
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['bottom'].set_visible(True)
            plt.gca().spines['left'].set_visible(True)
        
        
        plt.tight_layout()
        plt.show()
        
        plot_data = {'animName':animName,'c1l':c1l, 'times_cut':times_cut, 'dats':dats,'dats_err':dats_err,  'nts':nts}
        save_dictionary_pickle(plot_data, outputdir+'/volitionDynamics_'+animID+'.pkl')
    
    plt.tight_layout()
    return reconw,reconis



def plot_contrast_regression(reconw,
                             Np=60,
                             n_perm=15,
                             c1l=None,
                             tls=None,
                             figsize_scale=3,
                             seed=42,
                             title="Stimulus contrasts (% Weber)",
                             isplot=True):
    """
    绘制对比度（contrast）与 decoding accuracy 的回归图（Entry vs Rank）
    
    Parameters:
        reconw : list or array - 包含所有条件的 decoding 值列表
        Np : int - 每个条件每个 permutation 抽取的样本数
        n_perm : int - 置换次数
        c1l : list - x轴标签（对比度）
        tls : list - 两个子图的标题
        figsize_scale : int - 控制图像大小
        seed : int - 随机种子
        title : str - 总标题
        isplot : bool - 是否绘制并显示图像 (默认 True)
    """
    
    # 默认参数
    if c1l is None:
        c1l = ['4', '8', '15', '100']
    if tls is None:
        tls = ['entry', 'rank']
    
    fs = 6 * figsize_scale
    
    slope_d = []
    dat = []
    corrs = []
    
    np.random.seed(seed)
    
    for Li in range(2):
        xs_list = []
        ys_list = []
        
        for i in range(len(c1l)):
            # 合并对应条件
            idx1 = i + 1 + Li * 10
            idx2 = i + 1 + 5 + Li * 10
            pool = np.concatenate([reconw[idx1], reconw[idx2]])
            
            for perm in range(n_perm):
                # Balanced resampling
                if len(pool) >= Np:
                    sample_idx = np.random.choice(len(pool), size=Np, replace=False)
                else:
                    sample_idx = np.random.choice(len(pool), size=Np, replace=True)
                
                sample_mean = pool[sample_idx].mean()
                ys_list.append(sample_mean)
                xs_list.append(i)
        
        xs2 = np.array(xs_list)
        ys2 = np.array(ys_list)
        dat.append(np.array([xs2, ys2]))
        
        # 线性回归
        slope, intercept = np.polyfit(xs2, ys2, 1)
        slope_d.append(slope)
        corr = pearsonr(xs2, ys2)
        corrs.append(corr[0])
        
        if isplot: print(f"{tls[Li]:6s} | slope = {slope:.5f} | r = {corr[0]:.3f} | p = {corr[1]:.4f}")
        
        # ==================== Plot (仅当 isplot=True 时执行) ====================
        if isplot:
            if Li == 0:  # 第一次循环创建 figure
                fig = plt.figure(figsize=[2*figsize_scale, 1.5*figsize_scale])
            
            ax = plt.subplot(1, 2, Li + 1)
            
            jitter = np.random.normal(0, 0.08, size=len(xs2))
            ax.scatter(xs2 + jitter, ys2,
                       s=45, color='k', alpha=0.13, marker='o', edgecolors='none')
            
            # 回归线
            x_reg = np.array([0, len(c1l)-1])
            ax.plot(x_reg, slope * x_reg + intercept,
                    c='k' if Li == 0 else 'gray', lw=2.8)
            
            ax.set_title(f"{tls[Li]}\nr={corr[0]:.2f}, p={corr[1]:.3f}", fontsize=fs)
            
            ax.set_xticks(range(len(c1l)))
            ax.set_xticklabels(c1l, fontsize=fs)
            
            if Li == 0:
                ax.set_ylabel('Decoding accuracy', fontsize=fs)
            
            ax.tick_params(axis='y', labelsize=fs)
            
            # 美化
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
    
    if isplot:
        plt.suptitle(title, x=0.55, y=0.03, fontsize=fs)
        plt.tight_layout(rect=[0, 0.04, 1, 0.96])
        plt.show()
    
    return corrs, slope_d, dat


def scatER(reconw, plotType = 'type1',
           figsize_scale=3.0,
           mks=40,
           alpha=0.1,
           title="Decoding Accuracy"):
    """
    绘制 Entry vs Rank subspace 的 decoding accuracy 散点图 + 回归线
    
    Parameters:
        reconw : list/array - 你的 reconw 列表，至少包含 4 个元素
        figsize_scale : float - 控制图像大小 (默认 3.0)
        mks : int - 散点大小
        alpha : float - 散点透明度
        title : str - 图像总标题
    """
    
    fs = 6 * figsize_scale
    dat = []
    if plotType == 'type1':
        fig = plt.figure(figsize=[1*figsize_scale, 1.8*figsize_scale])
        plt.suptitle(title, x=0.55, y=0.95, fontsize=fs)

        for i in range(2):

            x = reconw[0+i]; y = reconw[2+i]
            
            corr = pearsonr(x, y); print(corr)
            slope, intercept = np.polyfit(x, y, 1)
            y_reg = slope * x + intercept
            
            ax1 = plt.subplot(2, 1, 1+i)
            ax1.scatter(x, y, s=mks, color='gray', alpha=alpha)
            ax1.plot(x, y_reg, color='k', lw=2)
            
            ax1.set_xlabel('T'+str(i+1)+' Entry', fontsize=fs)
            ax1.set_ylabel('T'+str(i+1)+' Rank', fontsize=fs)
            ax1.tick_params(axis='both', labelsize=fs)
            
            ax1.set_title(f'T{i+1}: r={corr[0]:.2f}, p={corr[1]:.3f}', fontsize=fs-1)
            
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.spines['bottom'].set_visible(True)
            ax1.spines['left'].set_visible(True)
        
        
        plt.tight_layout(rect=[0, 0, 1, 0.93])   # 为 suptitle 留空间
        plt.show()

    elif plotType == 'type2':
        
        fig = plt.figure(figsize=[2*figsize_scale, 1.8*figsize_scale])
        plt.suptitle(title, x=0.55, y=0.95, fontsize=fs)

        
        for i in range(4):

            x = reconw[0+i%2]; y = reconw[2+i//2]
            
            corr = pearsonr(x, y); print(corr)
            slope, intercept = np.polyfit(x, y, 1)
            y_reg = slope * x + intercept
            
            ax1 = plt.subplot(2, 2, 1+i)
            ax1.scatter(x, y, s=mks, color='gray', alpha=alpha)
            ax1.plot(x, y_reg, color='k', lw=2)
            
            ax1.set_xlabel('T'+str(i%2+1)+' Entry', fontsize=fs)
            ax1.set_ylabel('T'+str(i//2+1)+' Rank', fontsize=fs)
            ax1.tick_params(axis='both', labelsize=fs)
            
            ax1.set_title(f'r={corr[0]:.2f}, p={corr[1]:.3f}', fontsize=fs-1)
            
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.spines['bottom'].set_visible(True)
            ax1.spines['left'].set_visible(True)
        
        
        plt.tight_layout(rect=[0, 0, 1, 0.93])   # 为 suptitle 留空间
        plt.show()
    elif plotType == 'type3':
        fig = plt.figure(figsize=[0.8*figsize_scale, 0.9*figsize_scale])
        x = np.concatenate([reconw[0],reconw[1]])
        y = np.concatenate([reconw[2],reconw[3]])
        dat.append(x)
        dat.append(y)
        corr = pearsonr(x, y);print(corr)
        slope, intercept = np.polyfit(x, y, 1)
        y_reg = slope * x + intercept

        ax1 = plt.gca()
        ax1.scatter(x, y, s=mks, color='gray', alpha=alpha)
        ax1.plot(x, y_reg, color='k', lw=2)
        
        ax1.set_xlabel('Entry', fontsize=fs)
        ax1.set_ylabel('Rank', fontsize=fs)
        ax1.tick_params(axis='both', labelsize=fs)
        
        ax1.set_title(title+'\n'+f'r={corr[0]:.2f}, p={corr[1]:.3f}', fontsize=fs-1)
        
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(True)
        ax1.spines['left'].set_visible(True)
        plt.show()
    elif plotType == 'type4':
        redrat = 3; fs=6*redrat;mks=40
        fig=plt.figure(figsize=[1.8*redrat,1*redrat]);
        plt.suptitle(title, x=0.55, y=0.95, fontsize=fs)
        
        x = np.concatenate([reconw[0],reconw[1]]);
        y = np.concatenate([reconw[2],reconw[3]]);
        dat.append(x)
        dat.append(y)
        corr = pearsonr(x,y)
        print(corr)
        slope, intercept = np.polyfit(x, y, 1)
        y_reg = slope * x + intercept
        plt.subplot(1,2,1)
        plt.scatter(x,y,s=mks,color='gray',alpha=0.1)
        plt.plot(x,y_reg, color='k')
        
        
        plt.xlabel('entry',fontsize=fs)
        plt.ylabel('rank',fontsize=fs)
        # plt.ylim([0,1]);plt.xlim([0,1])
        # plt.yticks([0.5],fontsize=fs);plt.xticks([0.25,0.75],fontsize=fs)
        plt.title('within\n'+f' r={corr[0]:.2f}, p={corr[1]:.3f}',fontsize=fs-2)
        # plt.xlim([0,0.75]);plt.ylim([0,0.75])
        plt.gca().spines['top'].set_visible(False);plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(True);plt.gca().spines['left'].set_visible(True)
        
        
        x = np.concatenate([reconw[0],reconw[1]]);
        y = np.concatenate([reconw[3],reconw[2]]);
        
        dat.append(x)
        dat.append(y)
        corr = pearsonr(x,y)
        print(corr)
        slope, intercept = np.polyfit(x, y, 1)
        y_reg = slope * x + intercept
        plt.subplot(1,2,2)
        plt.scatter(x,y,s=mks,color='gray',alpha=0.1)
        plt.plot(x,y_reg, color='k')
        
        
        plt.xlabel('entry',fontsize=fs)
        plt.ylabel('rank',fontsize=fs)
        # plt.ylim([0,1]);plt.xlim([0,1])
        # plt.yticks([0.5],fontsize=fs);plt.xticks([0.25,0.75],fontsize=fs)
        plt.title('between\n'+f' r={corr[0]:.2f}, p={corr[1]:.3f}',fontsize=fs-2)
        # plt.xlim([0,0.75]);plt.ylim([0,0.75])
        plt.gca().spines['top'].set_visible(False);plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(True);plt.gca().spines['left'].set_visible(True)
        
        plt.tight_layout()

    return dat

def compute_entry_rank_perm_corrs(reconw,numP,permNum):
    
    dat1 = np.concatenate([reconw[0],reconw[1]])
    dat2 = np.concatenate([reconw[2],reconw[3]])
    
    corrs=[]
    for perm in range(permNum):
        random.seed(12+perm)
        p=random.sample(range(0, len(dat1)), numP)
        dat1p = dat1[p]
        dat2p = dat2[p]
        x = dat1p; y = dat2p
        corrs.append(pearsonr(x,y)[0])
    corrs1=corrs
    
    dat1 = np.concatenate([reconw[0],reconw[1]])
    dat2 = np.concatenate([reconw[3],reconw[2]])
    
    corrs=[]
    for perm in range(permNum):
        random.seed(12+perm)
        p=random.sample(range(0, len(dat1)), numP)
        dat1p = dat1[p]
        dat2p = dat2[p]
        x = dat1p; y = dat2p
        corrs.append(pearsonr(x,y)[0])
    corrs2=corrs
    return corrs1,corrs2


def calc_latency(data, Params, rid, avgNum=50,latency_type='onset',stdf=1):
    """
    Parameters:
    data: array-like, ntrials x ntimes
    times: array-like, time points
    rid: rank id
    tt: time of stimulus onsets
    avgNum: average trial number
    latency_type: 'onset' or 'peak'
    maxlat: maximum latency
    stdf: stdf * baseline_std as threshold factor
    baseline_window: choose a time range for baseline

    return:
    latency: float, ntrials, with outliers e.g. 0, or extremely longer latency, 
    require further inspections 
    """
    times = Params['times']; tt = Params['tt']
    baseline_window = Params['baseline_window']

    np.random.seed(42); n_trials = data.shape[0]
    latencies=[];
    for i in range(1000):
            
        pick=np.random.choice(n_trials, size=avgNum, replace=True)
        
        y=data[pick].mean(0)
        y = scipy.signal.savgol_filter(y,window_length=11,polyorder=1)
        
        bmean = y[baseline_window[0]:baseline_window[1]].mean(0);
        bstd = y[baseline_window[0]:baseline_window[1]].std(0)

        baseline = bmean + stdf*bstd
        if sum(y>baseline)!=0:
            onset_time = times[(y>baseline)*(times>tt[rid])][0]
        else:
            onset_time=0
        
        peak_amp = y[scipy.signal.find_peaks(y)[0]].max()
        # peak_latency = times[y>=(0.8*peak_amp)][0]
        
        if latency_type == 'peak':
            latency = peak_latency-tt[rid]
        elif latency_type == 'onset':
            latency = onset_time-tt[rid]
            
        plt.plot(y)
        plt.axhline(baseline,ls='--')
        
        latencies.append(latency)
        
    latencies = np.array(latencies)
    return latencies

def compute_all_latencies(reconis,Params,stdf=6,avgNum=200, latency_type='onset'):

    pls=[];
    plt.figure(figsize=[16,4]);
    plt.subplot(1,4,1);pls.append(calc_latency(reconis[0],Params, 0, avgNum,latency_type,stdf))
    plt.subplot(1,4,2);pls.append(calc_latency(reconis[1],Params, 1, avgNum,latency_type,stdf))
    plt.subplot(1,4,3);pls.append(calc_latency(reconis[2],Params, 0, avgNum,latency_type,stdf))
    plt.subplot(1,4,4);pls.append(calc_latency(reconis[3],Params, 1, avgNum,latency_type,stdf))
    plt.tight_layout()

    pls2=[]
    minlat = 0.01;
    p = (pls[0]>minlat)&(pls[0]<1)&(pls[2]>minlat)&(pls[2]<2.5) & (pls[1]>minlat)&(pls[1]<1)&(pls[3]>minlat)&(pls[3]<2.5)
    pls2.append(pls[0][p])
    pls2.append(pls[1][p])
    pls2.append(pls[2][p])
    pls2.append(pls[3][p])
    
    return pls2

def plot_comparison(pls, colors=None, figsize=(4, 4.5), 
                                     title="Onset Latency: entry vs rank"):
    """
    entry vs rank latency
    """
    if colors is None:
        colors = ['#2c3e50', '#2c3e50', '#95a5a6', '#e74c3c']
    
    pl1 = np.concatenate([pls[0], pls[1]])   # Item / Entry
    pl2 = np.concatenate([pls[2], pls[3]])   # Rank
    
    print("=== Latency Statistics ===\n")
    print(f"Item (Entry) : n = {len(pl1):4d} | mean = {pl1.mean():.4f}s | std = {pl1.std():.4f}s")
    print(f"Rank         : n = {len(pl2):4d} | mean = {pl2.mean():.4f}s | std = {pl2.std():.4f}s")
    print(f"Difference   : mean = {(pl1 - pl2).mean():.4f}s\n")
    
    # ====================== 统计检验 ======================
    # 1. Paired t-test
    t, p_t = stats.ttest_rel(pl1, pl2)
    
    # 2. Wilcoxon signed-rank test (非参数)
    wilcox = stats.wilcoxon(pl1, pl2)
    
    # 3. Effect size (Cohen's d for paired)
    diff = pl1 - pl2
    cohen_d = diff.mean() / diff.std()
    
    # 4. 置信区间
    ci_low, ci_high = np.percentile(diff, [2.5, 97.5])
    
    print(f"Paired t-test      : t = {t:6.3f}, p = {p_t:.2e}")
    print(f"Wilcoxon test      : W = {wilcox.statistic:6.1f}, p = {wilcox.pvalue:.2e}")
    print(f"Cohen's d          : {cohen_d:6.3f}  (large effect if >0.8)")
    print(f"95% CI of diff     : [{ci_low:.4f}, {ci_high:.4f}] s")
    print(f"Item faster than Rank? p = {p_t:.2e} | Δ = {diff.mean():.4f}s")
    
    # ====================== 绘图 ======================
    fig = plt.figure(figsize=figsize)
    xlocs = [0, 0.75]
    
    # Item Violin
    vp1 = plt.violinplot(pl1, positions=[xlocs[0]], showextrema=False, showmeans=True)
    for pc in vp1['bodies']:
        pc.set_facecolor(colors[0])
        pc.set_alpha(0.6)
    if 'cmeans' in vp1:
        vp1['cmeans'].set_color(colors[0])
        vp1['cmeans'].set_linewidth(2)
    
    xs1 = np.random.normal(xlocs[0], 0.03, len(pl1))
    plt.scatter(xs1, pl1, alpha=0.4, c=colors[0], s=40, edgecolors='none')
    
    # Rank Violin
    vp2 = plt.violinplot(pl2, positions=[xlocs[1]], showextrema=False, showmeans=True)
    for pc in vp2['bodies']:
        pc.set_facecolor(colors[3])
        pc.set_alpha(0.55)
    if 'cmeans' in vp2:
        vp2['cmeans'].set_color(colors[3])
        vp2['cmeans'].set_linewidth(2)
    
    xs2 = np.random.normal(xlocs[1], 0.03, len(pl2))
    plt.scatter(xs2, pl2, alpha=0.4, c=colors[3], s=40, edgecolors='none')
    
    # 美化
    plt.ylabel('Onset latency (s)', fontsize=16)
    plt.xticks(xlocs, labels=['entry', 'rank'], fontsize=15)
    plt.tick_params(axis='x', length=0)
    plt.title(title, fontsize=15, pad=20)
    
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 在图上标注统计结果
    max_y = max(pl1.max(), pl2.max()) * 1.05
    plt.text(0.35, max_y*0.85, f"Δ = {diff.mean():.3f}s\np < {p_t:.1e}", 
             fontsize=13, ha='center', bbox=dict(boxstyle="round,pad=0.4", facecolor="white"))
    
    plt.tight_layout()
    plt.show()
    
    return pl1, pl2

def compute_onset_slope(data,data2,Params,rid,rit,avgNum):
    times=Params['times']; tt=Params['tt']; tp=Params['tp']
    tr1=Params['tr1']; tr2=Params['tr2'];sftp=Params['sftp']

    np.random.seed(42); n_trials = data.shape[0]
    slopes=[];activs=[]
    for i in range(1000):
            
        pick=np.random.choice(n_trials, size=avgNum, replace=True)
        
        y=data[pick].mean(0)
        y2=data2[pick].mean(0)
        
        start_idx = int(tp[rid])
        end_idx = int(tp[rid]+rit*sftp) # 0-300 ms
            
        amp1 = y[start_idx]
        amp2 = y[end_idx]
        deltaT = (times[end_idx] - times[start_idx])
        amp = amp2 - amp1
    
        slope = amp/deltaT

        plt.plot(y)
        plt.axvline(start_idx,c='k',ls='--')
        plt.axvline(end_idx,ls='--')
    
        slopes.append(slope)
        activs.append(y2[int(tp[rid]+tr1):int(tp[rid]+tr2)].mean())
    slopes = np.array(slopes)
    activs = np.array(activs)
    return slopes,activs


def onset_slope(reconis,Params,avgNum,r1t=0.3,r2t=0.2):
    slps=[];actis=[];
    
    plt.figure(figsize=[8,4]);
    plt.subplot(1,2,1);
    slp,acti = compute_onset_slope(reconis[2],reconis[0],Params, 0, r1t, avgNum)
    slps.append(slp);actis.append(acti)
    
    plt.subplot(1,2,2);
    slp,acti = compute_onset_slope(reconis[3],reconis[1],Params, 1, r2t, avgNum)
    slps.append(slp);actis.append(acti)
    plt.tight_layout()

    pls=[]
    p = (slps[0]>0) & (slps[1]>0)
    pls.append(actis[0][p])
    pls.append(actis[1][p])
    pls.append(slps[0][p])
    pls.append(slps[1][p])
    return pls





def plot_comparison_stimvol(reconw, figsize=(5.5, 3.8), 
                                  label="decoding accuracy"):
    """
    绘制 0% vs 100% 在 Entry 和 Rank subspace 的 decoding accuracy 对比图
    
    输入: reconw (list)
    输出: dats (list) = [entry_0%, entry_100%, rank_0%, rank_100%]
    """
    ## activity strength: 0% vs 100%
    dat = reconw; dats = []
    
    fig=plt.figure(figsize=figsize)
    # plt.title('0% vs 100%')
    rmin=1;rmax=5; xlocs=np.arange(rmin,rmax,(rmax-rmin)/4)
    condis=['entry','rank']; 
    
    
    for Li in range(2):
        pl1 = np.concatenate([dat[6*Li],dat[6*Li+3]])
        pl2 = np.concatenate([dat[6*Li+1],dat[6*Li+4]])
        
        dats.append(pl1); dats.append(pl2)
        
        print(condis[Li]+' subspace')
        print(stats.ttest_1samp(pl1,popmean=1/6))
        print(stats.ttest_1samp(pl2,popmean=1/6))
        print(stats.ttest_ind(pl1,pl2))
        
        boxprops = dict(linestyle='-', linewidth=1, color='black')
        meanlineprops = dict(linestyle='-', linewidth=1, color='black')
        medianprops = dict(linestyle='-', linewidth=0, color='white')
        
        xloc = xlocs[2*Li]
        violin_parts = plt.violinplot(pl1,positions=[xloc],showextrema=False,showmeans=True)
        for pc in violin_parts['bodies']:
            pc.set_facecolor(colors[3])  # Set the color of the violin body
        #     pc.set_edgecolor('k')    # Set the color of the edge
            pc.set_alpha(0.5)           # Set transparency
        if 'cmeans' in violin_parts:
            violin_parts['cmeans'].set_edgecolor(colors[3]) # Median line color
        
        xs1 = np.random.normal(loc=xloc, scale=0.02, size=len(pl1))
        plt.scatter(xs1, pl1, alpha=0.3, c=colors[3])
        
        
        
        xloc = xlocs[2*Li+1]
        violin_parts = plt.violinplot(pl2,positions=[xloc],showextrema=False,showmeans=True)
        for pc in violin_parts['bodies']:
            pc.set_facecolor('k')  # Set the color of the violin body
        #     pc.set_edgecolor('gray')    # Set the color of the edge
            pc.set_alpha(0.3)           # Set transparency
        if 'cmeans' in violin_parts:
            violin_parts['cmeans'].set_edgecolor('k') # Median line color
        xs2 = np.random.normal(loc=xloc, scale=0.02, size=len(pl2))
        plt.scatter(xs2, pl2, alpha=0.3, c='k')
    
    plt.axhline(1/6,ls=':',c='gray')
    # plt.ylim([-0.2,1.2]);plt.yticks([0,0.5,1],fontsize=15)
    # plt.yticks(fontsize=15)
    plt.ylabel(label,fontsize=15);
    plt.xticks(xlocs,labels=['0%\n entry','100%\n entry','0%\n rank','100%\n rank'],fontsize=15);
    plt.tick_params(axis='x',length=0)
    
    
    
    plt.gca().spines['top'].set_visible(False);plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(True);plt.gca().spines['left'].set_visible(True)

    
    return dats



