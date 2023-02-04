from cmt_data import *
from sklearn.decomposition import PCA

def generate_cmt_factors(mDate, par_cp_map, back_look = 60):


    allDates = list(par_cp_map.keys())
    yld_chg_map = {}
    for i, j in zip(allDates[:-1], allDates[1:]):
        d, lastd = par_cp_map[j], par_cp_map[i]
        diff = [d[_] - lastd[_] for _ in range(len(d))]
        yld_chg_map[j] = diff

    index = allDates.index(mDate)

    considered_date = allDates[index - back_look:index]

    data = [yld_chg_map[d] for d in considered_date]
    stdL = [np.std([d[i] for d in data]) for i in range(len(data[0]))]
    mL = [np.mean([d[i] for d in data]) for i in range(len(data[0]))]
    for l in data:
        for i in range(len(data[0])):
            l[i] = (l[i] - mL[i]) / stdL[i]

    X = np.array(data)
    pca = PCA(n_components=3)
    pca.fit(X)

    plt.plot(cmt_list, -pca.components_[0], label="F1 - explain " + str(round(pca.explained_variance_ratio_[0], 4)))
    plt.plot(cmt_list, -pca.components_[1], label="F2 - explain " + str(round(pca.explained_variance_ratio_[1], 4)))
    plt.plot(cmt_list, -pca.components_[2], label="F3 - explain " + str(round(pca.explained_variance_ratio_[2], 4)))
    plt.legend()
    plt.title("Bond Yield Shift PCA")
    plt.show()

    scale1 = 1 / pca.components_[0][2]
    scale2 = 1 / (pca.components_[1][4] - pca.components_[1][1])

    scaled_f1 = [scale1 * f for f in pca.components_[0]]
    scaled_f2 = [scale2 * f for f in pca.components_[1]]

    return scaled_f1, scaled_f2

