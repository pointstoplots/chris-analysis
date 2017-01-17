import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from radar import make_radar

def organize_playdata():
    """
    Organizes defensive play-type data from 2015-16.
    
    Returns:
        plays (dict): dict of individual play-type DataFrames
            key-vals are {play-type (str): data (pd.DataFrame)}
        all_data (pd.DataFrame): DataFrame of all play-types joined on player name
        ave_ppp (dict): Dict of {play-type: average_ppp}
            Example key:val {'handoff': 0.870}
    """

    # Read individual play types into Pandas DataFrame
    handoff = pd.read_csv('../data/handoff.csv')
    offscreen = pd.read_csv('../data/offscreen.csv')
    postup = pd.read_csv('../data/postup.csv')
    prrm = pd.read_csv('../data/prrm.csv')
    isolation = pd.read_csv('../data/isolation.csv')
    prbh = pd.read_csv('../data/prbh.csv')
    spotup = pd.read_csv('../data/spotup.csv')
    
    # Get all DataFrames into dict
    plays = {'handoff': handoff, 
             'offscreen': offscreen, 
             'postup': postup, 
             'prrm': prrm, 
             'isolation': isolation, 
             'prbh': prbh, 
             'spotup': spotup}
    
    # Get average PPP for each play
    ave_ppp = {}
    for play in plays:
        ave_ppp[play] = get_ave_ppp(plays[play])
        
    # Add "Competency" to DataFrame
    # A player is "Competent" to defend a play if they have
    # defended it more than 25 times and keep it below league ave
    def add_competency(df, play):
        df['COMPETENT' + play] = (df.PPP < ave_ppp[play]) & (df.POSS > 25)
        return df
        
    for play in plays:
        plays[play] = add_competency(plays[play], play)
        plays[play]['PPP' + play] = plays[play]['PPP']
        
    ##########################
    #### BEGIN MERGE HELL ####
    ##########################
    
    joined1 = pd.merge(isolation, postup, on='PLAYER', how='outer')
    joined2 = pd.merge(joined1, spotup, on='PLAYER', how='outer')
    joined3 = pd.merge(joined2, handoff, on='PLAYER', how='outer')
    joined4 = pd.merge(joined3, prrm, on='PLAYER', how='outer')
    joined5 = pd.merge(joined4, prbh, on='PLAYER', how='outer')
    joined = pd.merge(joined5, offscreen, on='PLAYER', how='outer')
    all_data = joined.fillna(0)
    
    # Count total number of plays each player is competent to defend
    all_data['TOTAL COMPETENT'] = all_data['COMPETENTspotup'] + \
                                  all_data['COMPETENThandoff'] + \
                                  all_data['COMPETENToffscreen'] + \
                                  all_data['COMPETENTpostup'] + \
                                  all_data['COMPETENTprbh'] + \
                                  all_data['COMPETENTprrm'] + \
                                  all_data['COMPETENTisolation']
    
    return (plays, all_data, ave_ppp)

def get_ave_ppp(df):
    # Calculates Average PPP
    return (df.PPP * df.POSS).sum() / df.POSS.sum()
             
def prelim_plots(plays_dict, all_data):
    """
    Some preliminary plots
    
    - How many possessions did each player have of each play type?
    - How much noise is there when a player has few possessions?
    - How many players are competent at 1 play type? 6 play types? etc.
    """
    plt.figure(figsize=(5,20))
    plt.subplots_adjust(hspace=0.75)
    for index, play in enumerate(plays):
        subplotnum = int('71' + str(index + 1))
        plt.subplot(subplotnum)
        plt.hist(plays[play]['POSS'], bins=30)
        plt.title(play)
        plt.ylabel('Number of players')
        plt.xlabel('Total Possessions')
    plt.show()
    
    plt.figure(figsize=(5,20))
    plt.subplots_adjust(hspace=0.75)
    for index, play in enumerate(plays):
        subplotnum = int('71' + str(index + 1))
        plt.subplot(subplotnum)
        plt.scatter(plays[play]['POSS'], plays[play]['PPP'])
        plt.title(play)
        plt.ylabel('Numer of Possessions')
        plt.xlabel('Average Points Per Possession')
    plt.show()

    plt.figure()
    competency_count = all_data.groupby('TOTAL COMPETENT').count()['PLAYER']
    sns.barplot(x=list(range(7)), y=list(competency_count), color='grey') 
    plt.ylabel('Number of Players')
    plt.xlabel('Number of Play-Types Defendable')
    plt.show()


def prelim_questions(plays_dict, all_data):
    """
    Scratch work for prelim questions.
    
    - Which players can defend 6 play-types?
    """
    elite_defenders = all_data[all_data['TOTAL COMPETENT'] == 6]['PLAYER']
    print('Defenders who can defend six play-types:')
    print(elite_defenders)


def make_player_barplot(player_name, plays_dict, ave_dict):  
    """
    Makes bar plot of how well a player can defend each play-type
    """
    league_ave = []
    for index, play in enumerate(ave_dict.keys()):
        league_ave.append(ave_dict[play])
    x = []
    y = []
    for play in plays_dict:
        df = plays_dict[play]
        df = df[df['PLAYER'] == player_name]
        y.append(float( df['PPP'] - ave_dict[play]))
        x.append(play)
    sns.barplot(x=x, y=y, color='grey')
    plt.ylabel('Points per possession (relative to league ave)')
    plt.title(player_name)

if __name__ == '__main__':
    # Organize Data
    plays, all_data, ave_ppp = organize_playdata()
    
    ##########################
    ### Some example plots ###
    ##########################
    
    #prelim_questions(plays, all_data)
    #make_player_barplot('Klay Thompson', plays, ave_ppp)
    #make_radar('Damian Lillard', all_data, ave_ppp)
    #make_radar('Mason Plumlee', all_data, ave_ppp)
    #prelim_plots(plays, all_data)
