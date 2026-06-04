## 
from _defs._init import *
import mne
from mne.stats import permutation_cluster_1samp_test



def cluster_permutation_test_onesample(data, times, chance=1/6.0, 
                                       n_permutations=2000, 
                                       threshold=None, 
                                       tail=1,          # 1 = greater than chance
                                       seed=42,
                                       verbose=True):
    """
    Cluster-based permutation test for time series data against chance level.
    
    参数:
        data : np.ndarray, shape = (n_trials, n_times)   ← 你的 reconi 形状
        times : 1D array，时间点数组
        chance : float，默认 1/6 ≈ 0.1667
        n_permutations : 置换次数（推荐 1000~5000，越多越精确）
        threshold : 初始聚类阈值（None 时自动用 t=3 左右）
        tail : 1 表示 one-sided (greater), 0 表示 two-sided
        seed : 随机种子
    
    返回:
        t_obs : 观测的 t 值 (n_times,)
        clusters : 显著集群的索引列表
        cluster_p_values : 每个集群的校正后 p-value
        H0 : 置换分布
    """
    np.random.seed(seed)
    
    # 数据形状转为 MNE 要求的 (n_observations, n_times)
    X = data - chance                          # (n_trials, n_times)
    
    # 如果没有指定 threshold，常用一个较严格的 t 阈值
    if threshold is None:
        from scipy.stats import t
        df = X.shape[0] - 1
        threshold = t.ppf(1 - 0.001, df=df)    # p < 0.001 的 t 值作为聚类起点
    
    # 执行集群置换检验（one-sample）
    t_obs, clusters, cluster_p_values, H0 = permutation_cluster_1samp_test(
        X,
        n_permutations=n_permutations,
        threshold=threshold,
        tail=tail,
        n_jobs=1,                  # 可改为 -1 使用所有 CPU
        seed=seed,
        out_type='indices',        # 返回时间点索引
        verbose=verbose
    )
    
    # 打印显著集群信息
    sig_clusters = np.where(cluster_p_values < 0.05)[0]
    print(f"Found {len(sig_clusters)} significant cluster(s) at p < 0.05")
    for i, clu_idx in enumerate(sig_clusters):
        cluster_times = times[clusters[clu_idx]]
        print(f"  Cluster {i+1}: p = {cluster_p_values[clu_idx]:.4f}, "
              f"time range: {cluster_times.min():.3f} ~ {cluster_times.max():.3f} s")
    
    return t_obs, clusters, cluster_p_values, H0


def permsplot(reconi,times,chance,n_permutations,p_thres,tail,seed,ms,c,sig_y):

    t_obs, clusters, cluster_p_values, H0 = cluster_permutation_test_onesample(
                reconi, 
                times=times,
                chance=chance,
                n_permutations=n_permutations,     # 可增加到 5000
                tail=1,                  # greater than chance
                seed=42)
    
    for clu_idx, p_val in enumerate(cluster_p_values):
                if p_val < p_thres:
                    cluster_mask = np.zeros(len(times), dtype=bool)
                    cluster_mask[clusters[clu_idx]] = True
                    if ms==0:
                        plt.scatter(x=times[cluster_mask],y=np.ones(cluster_mask.sum()) * sig_y,c=c,alpha=0.3,marker='o')
                    else:
                        plt.scatter(x=times[cluster_mask],y=np.ones(cluster_mask.sum()) * sig_y,c=c,alpha=1,marker='o',s=ms)


def i2anova(labels, situations,conditions,dats):
    data = []; i=0;
    for sit in situations:
        for cond in conditions:
            values=dats[i]
            i=i+1
            for v in values:
                data.append([sit, cond, v])
    
    df = pd.DataFrame(data, columns=[labels[0], labels[1], 'Value'])
    
    # 两因素ANOVA
    model = ols('Value ~ C('+labels[0]+') + C('+labels[1]+') + C('+labels[0]+'):C('+labels[1]+')', data=df).fit()
    anova_table = anova_lm(model, typ=2)
    
    print("Two-Way ANOVA Results:")
    print(anova_table)
    
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    tukey = pairwise_tukeyhsd(df['Value'], df['subspace'] + '-' + df['contrast'])
    print("\nTukey HSD Post-Hoc Test:")
    print(tukey)

def downNsample(data1,data2,n_perm,avgNum):
    # M = int(data1.shape[0]/N)
    data1_new=[];data2_new=[]
    for i in range(n_perm):
        np.random.seed(42+i)
        indices = np.random.choice(data1.shape[0], size=avgNum, replace=True)
        data1_new.append(data1[indices].mean(0))
        data2_new.append(data2[indices].mean(0))
    return np.array(data1_new),np.array(data2_new)

def down1sample(data1,n_perm,avgNum):
    # M = int(data1.shape[0]/N)
    data1_new=[]
    for i in range(n_perm):
        np.random.seed(42+i)
        indices = np.random.choice(data1.shape[0], size=avgNum, replace=True)
        data1_new.append(data1[indices].mean(0))
    return np.array(data1_new)







