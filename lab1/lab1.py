import numpy as np
from matplotlib import pyplot as plt
import itertools
from scipy.spatial import distance


tests_number = 10
points_number = 100
start_dim = 2
end_dim = 101

dims = np.arange(start_dim, end_dim)
dims_num = end_dim - start_dim

# np.random.seed(1234)

############### utils ###############

def plot_with_error_bars(title, x, y, yerr, xlabel, ylabel, show=False, save_dir=None):
    plt.errorbar(x, y, yerr=yerr, linestyle='None',
                 capsize=2.5, marker='.', color='blue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    if show:
        plt.show()
    if save_dir is not None:
        plt.savefig(save_dir)
    plt.clf()

############### zad. 1 ###############

def inside_outside_ratios(dim):
    # generate random points
    points = np.random.uniform(low=-1, high=1, size=(points_number, dim))
    # find the radii - dist between points and (0, ..., 0)
    radii = np.sqrt(np.sum(np.square(points), axis=1))

    # find the ratios
    inside_points = points[radii <= 1]
    inside_ratio = len(inside_points) / points_number
    outside_ratio = 1 - inside_ratio

    return np.array([inside_ratio, outside_ratio])

def zad1():
    avgs = np.empty(shape=(dims_num, 2))   # columns: 0: inside, 1 - outside
    stds = np.empty(shape=(dims_num, 2))

    for i, dim in enumerate(dims):
        ratios = np.empty(shape=(tests_number, 2))
        for j in range(tests_number):
            ratios[j] = inside_outside_ratios(dim)

        avgs[i] = np.average(ratios, axis=0)
        stds[i] = np.std(ratios, axis=0)

    plot_with_error_bars(title=f'Zadanie 1 - punkty w środku hiperkuli\npowtórzenia={tests_number}, punkty={points_number}',
        x=dims, y=avgs[:, 0], yerr=stds[:, 0], xlabel='wymiarowość', ylabel='punkty w środku / wszystkie wygenerowane punkty',
        save_dir='plots/zad1/inside')

    plot_with_error_bars(title=f'Zadanie 1 - punkty na zewnątrz hiperkuli\npowtórzenia={tests_number}, punkty={points_number}',
        x=dims, y=avgs[:, 1], yerr=stds[:, 1], xlabel='wymiarowość', ylabel='punkty na zewnątrz / wszystkie wygenerowane punkty',
        save_dir='plots/zad1/outside')

############### zad. 2 ###############

def zad2():
    avg_dists = np.empty(shape=(dims_num, 2))   # columns: 0: value, 1: std
    avg_stds = np.empty(shape=(dims_num, 2))
    avg_ratios = np.empty(shape=(dims_num, 2))

    for i, dim in enumerate(dims):
        dim_dists = np.empty(shape=(tests_number))
        dim_stds = np.empty(shape=(tests_number))
        dim_ratios = np.empty(shape=(tests_number))
        for j in range(tests_number):
            points = np.random.uniform(
                low=-1, high=1, size=(points_number, dim))
            combinations = itertools.combinations(points, 2)
            dists = np.empty(shape=(points_number * (points_number - 1) // 2))
            for k, (A, B) in enumerate(combinations):
                dists[k] = distance.euclidean(A, B)

            dim_dists[j] = np.average(dists)
            dim_stds[j] = np.std(dists)
            dim_ratios[j] = dim_stds[j] / dim_dists[j]

        avg_dists[i][0] = np.average(dim_dists)
        avg_dists[i][1] = np.std(dim_dists)
        avg_stds[i][0] = np.average(dim_stds)
        avg_stds[i][1] = np.std(dim_stds)
        avg_ratios[i][0] = np.average(dim_ratios)
        avg_ratios[i][1] = np.std(dim_ratios)

    plot_with_error_bars(title=f'Zadanie 2 - średnia odległość\npowtórzenia={tests_number}, punkty={points_number}',
        x=dims, y=avg_dists[:, 0], yerr=avg_dists[:, 1], xlabel='wymiarowość', ylabel='średnia średnich odległości między punktami',
        save_dir='plots/zad2/average')

    plot_with_error_bars(title=f'Zadanie 2 - średnie odchylenie standardowe\npowtórzenia={tests_number}, punkty={points_number}',
        x=dims, y=avg_stds[:, 0], yerr=avg_stds[:, 1], xlabel='wymiarowość', ylabel='średnia odchyleń standardowych odległości między punktami',
        save_dir='plots/zad2/std')

    plot_with_error_bars(title=f'Zadanie 2 - stosunek średniego odchylenia do średniej odległości\npowtórzenia={tests_number}, punkty={points_number}',
        x=dims, y=avg_ratios[:, 0], yerr=avg_ratios[:, 1], xlabel='wymiarowość', ylabel='średnia stosunków odchylenia\ndo średniej odległości między punktami',
        save_dir='plots/zad2/ratio')

############### zad. 3 ###############

def find_angle(v1, v2):
    v1 /= np.linalg.norm(v1)
    v2 /= np.linalg.norm(v2)
    dot_product = np.dot(v1, v2)
    return np.arccos(dot_product)

def zad3():
    for dim in dims:
        dim_angles = np.empty(shape=(tests_number * (points_number // 4)))
        angle_idx = 0
        for _ in range(tests_number):
            points = np.random.uniform(low=-1, high=1, size=(points_number, dim))
            for _ in range(points_number // 4):
                idx = np.random.choice(points.shape[0], size=4, replace=False)
                dim_angles[angle_idx] = find_angle(points[idx[1]] - points[idx[0]], points[idx[3]] - points[idx[2]])
                angle_idx += 1

        # histogram
        plt.hist(dim_angles, bins=50, range=(0, np.pi))
        plt.title(f'Zadanie 3 - Histogram kątów między losowymi wektorami\n\
wymiarowość={dim}, powtórzenia={tests_number}, punkty={points_number}\n\
$\mu={round(np.average(dim_angles), 2)}$, $\sigma={round(np.std(dim_angles), 2)}$')
        plt.xlabel('kąt [rad]')

        plt.tight_layout()
        plt.savefig(f'plots/zad3/dim {dim}')
        plt.clf()

######################################

if __name__ == "__main__":
    # zad1()
    zad2()
    # zad3()
