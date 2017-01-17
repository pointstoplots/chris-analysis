import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Radar():
    """
    Modified from https://gist.github.com/kylerbrown/29ce940165b22b8f25f4
    """
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=6):
        angles = np.arange(0, 360, 360./len(variables))

        axes = [fig.add_axes([0.12,0.12,0.78,0.78],polar=True,
                label = "axes{}".format(i)) 
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles, 
                                         labels=variables)
        [txt.set_rotation(angle-90) for txt, angle 
             in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i], 
                               num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x,2)) 
                         for x in grid]
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1] # hack to invert grid
                          # gridlabels aren't reversed
            gridlabel[0] = "" # clean up origin
            ax.set_rgrids(grid, labels=gridlabel,
                         angle=angles[i])
            #ax.spines["polar"].set_visible(False)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]
    def plot(self, data, *args, **kw):
        self.ax.plot(self.angle, np.r_[data, data[0]], *args, **kw)
    def fill(self, data, *args, **kw):
        self.ax.fill(self.angle, np.r_[data, data[0]], *args, **kw)

def make_radar(player_name, all_data, ave_dict):
    """
    Radar Plot of how well a player defends each position
    """
    variables = list(ave_dict.keys())
    data =  list(all_data[all_data.PLAYER == player_name][['PPP' + key for key in ave_dict.keys()]].values[0])
    ranges = [(0.01, 1.5) for i in range(7)]         

    # Plot player values
    fig1 = plt.figure(figsize=(6, 6))
    radar = Radar(fig1, variables, ranges)
    radar.plot(data)
    radar.fill(data, alpha=0.2)
    
    # Plot League Ave
    league_ave = []
    for index, play in enumerate(ave_dict.keys()):
        league_ave.append(ave_dict[play])
    radar = Radar(fig1, variables, ranges)
    radar.plot(league_ave)
    plt.title(player_name + '\n')
    plt.show()
