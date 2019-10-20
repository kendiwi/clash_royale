
# coding: utf-8

# # Clash Royale - Acompanhamento de desempenho semanal

# ## Importando as bibliotecas

# In[19]:


import pandas as pd
import csv
import requests
import numpy as np
from datetime import date


name_clan=['nargal_team','capa_preta']
tag_clan=['8VYPYGGQ','2UG290GY']

lista = list(zip(name_clan,tag_clan))

today = date.today()


# In[20]:


def action(x):

    if (x["wins"] == 0) & (x["loss"] >= 4):
        return "kick"

    elif (x["wins"] ==1) & (x["loss"] >=5):
        return "kick"

    elif (x["wins"] ==2) & (x["loss"] >=6):
        return "kick"

    elif (x["wins"] ==3) & (x["loss"] >=8):
        return "kick"

    elif (x["wins"] ==4) & (x["loss"] >=9):
        return "kick"

    elif (x["wins"] ==5) & (x["loss"] >=10):
        return "kick"



    elif (x["wins"] ==0) & (x["loss"] ==3):
        return "warning"    

    elif (x["wins"] ==1) & (x["loss"] ==4):
        return "warning"

    elif (x["wins"] ==2) & (x["loss"] ==5):
        return "warning"

    elif (x["wins"] ==3) & (x["loss"] ==7):
        return "warning"

    elif (x["wins"] ==4) & (x["loss"] ==8):
        return "warning"

    elif (x["wins"] ==5) & (x["loss"] ==9):
        return "warning"



    elif x["rank"] <= ref_Coleader:

        if x["role"] == "member":
            return "upgrade to elder"

        elif x["role"] == "elder":
            return "upgrade to coLeader"


    elif (x["rank"] > ref_Coleader) & (x["rank"] <= ref_Elder):

        if x["role"] == "member":
            return "upgrade to elder"

    elif x["rank"] > ref_Elder:

        if x["role"] == "elder":
            return "downgrade to member"

        elif x["role"] == "coLeader":
            return "downgrade to elder"

    else:
        return "ok"


# In[23]:


for v,j in lista:
## Download das bases API Royale

    URL_war = 'https://royaleapi.com/clan/'+ j +'/war/analytics/csv'
    with requests.Session() as s:
        download = s.get(URL_war)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_war = list(cr)



    URL_clan = 'https://royaleapi.com/clan/'+ j +'/csv'
    with requests.Session() as s:
        download = s.get(URL_clan)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_clan = list(cr)


    ##Criando os dfs

    df = pd.DataFrame(my_war,columns=my_war[0])
    df_war=df.drop(df.index[0])

    df = pd.DataFrame(my_clan,columns=my_clan[0])
    df_clan=df.drop(df.index[0])

    df_clan_num = ["trophies", "expLevel", "clanRank", "previousClanRank", "donations", "donationsReceived"]

    for i in df_clan_num:
        df_clan[i] = df_clan[i].astype(int)

    df_clan["tag"]=df_clan.tag.str.replace("#","")

    df_war_num = ["battles_dict_0_cards_earned","battles_dict_0_battles_played","battles_dict_0_wins",
                 "battles_dict_1_cards_earned","battles_dict_1_battles_played","battles_dict_1_wins",
                 "battles_dict_2_cards_earned","battles_dict_2_battles_played","battles_dict_2_wins",
                 "battles_dict_3_cards_earned","battles_dict_3_battles_played","battles_dict_3_wins",
                 "battles_dict_4_cards_earned","battles_dict_4_battles_played","battles_dict_4_wins",
                 "battles_dict_5_cards_earned","battles_dict_5_battles_played","battles_dict_5_wins",
                 "battles_dict_6_cards_earned","battles_dict_6_battles_played","battles_dict_6_wins",
                 "battles_dict_7_cards_earned","battles_dict_7_battles_played","battles_dict_7_wins",
                 "battles_dict_8_cards_earned","battles_dict_8_battles_played","battles_dict_8_wins",
                 "battles_dict_9_cards_earned","battles_dict_9_battles_played","battles_dict_9_wins"
                 ]

    for i in df_war_num:
        df_war[i]=df_war[i].replace("",0).astype(int)

    df_war.drop("name",axis=1,inplace=True)

    ## Criando features

    cols_battles_played = ["battles_dict_0_battles_played",
                           "battles_dict_1_battles_played",
                           "battles_dict_2_battles_played",
                           "battles_dict_3_battles_played",
                           "battles_dict_4_battles_played",
                           "battles_dict_5_battles_played",
                           "battles_dict_6_battles_played",
                           "battles_dict_7_battles_played",
                           "battles_dict_8_battles_played",
                           "battles_dict_9_battles_played"]

    cols_cards_earned = ["battles_dict_0_cards_earned",
                           "battles_dict_1_cards_earned",
                           "battles_dict_2_cards_earned",
                           "battles_dict_3_cards_earned",
                           "battles_dict_4_cards_earned",
                           "battles_dict_5_cards_earned",
                           "battles_dict_6_cards_earned",
                           "battles_dict_7_cards_earned",
                           "battles_dict_8_cards_earned",
                           "battles_dict_9_cards_earned"]

    cols_wins = ["battles_dict_0_wins",
                           "battles_dict_1_wins",
                           "battles_dict_2_wins",
                           "battles_dict_3_wins",
                           "battles_dict_4_wins",
                           "battles_dict_5_wins",
                           "battles_dict_6_wins",
                           "battles_dict_7_wins",
                           "battles_dict_8_wins",
                           "battles_dict_9_wins"]

    df_war["card_earned"] = df_war[cols_cards_earned].sum(axis=1)
    df_war["battles_played"] = df_war[cols_battles_played].sum(axis=1)
    df_war["wins"] = df_war[cols_wins].sum(axis=1)
    df_war["loss"] = df_war.battles_played - df_war.wins

    ## Merge nas duas tabelas

    dfs=pd.merge(df_clan,df_war,how="left", left_on="tag", right_on="tag")
    dfs.fillna(0,inplace = True)

    ## Calculo do APR

    dfs=dfs[["tag","name","role","expLevel","trophies","donations","card_earned","battles_played","wins","loss"]]

    cols_percent = ["donations","card_earned","battles_played","wins","loss"]

    for i in cols_percent:
        col_name = "perc_"+ i

        dfs[col_name]= dfs[i]/dfs[i].sum()

    dfs["perc_tot"] = 0.5*(dfs.perc_donations) + dfs.perc_card_earned + dfs.perc_battles_played + dfs.perc_wins - dfs.perc_loss

    ref_donations= dfs.perc_donations.max()
    ref_card_earned= dfs.perc_card_earned.max()
    ref_battles_played= dfs.perc_battles_played.max()
    ref_wins= dfs.perc_wins.max()
    ref_loss= dfs.perc_loss.min()
    ref_sum = 0.5*(ref_donations) + ref_card_earned + ref_battles_played + ref_wins - ref_loss

    dfs["apr"] = round((dfs.perc_tot/ref_sum),4)

    df_end=dfs[["tag","name","role","expLevel","trophies","donations","card_earned","battles_played","wins","loss","apr"]].sort_values(by="apr",ascending=False)

    df_end.reset_index(drop=True,inplace=True)
    df_end["rank"] =  np.arange(1, len(df_end) + 1)

    df_end['apr'] = df_end['apr'].apply(lambda x: "{0:.2f}%".format(x*100))

    df_end["wins"]=df_end.wins.astype(int)
    df_end["loss"]=df_end.loss.astype(int)
    df_end["battles_played"]=df_end.battles_played.astype(int)
    df_end["card_earned"]=df_end.card_earned.astype(int)

    ## Regras para promocao, downgrade e kick

    tot_players=df_end.shape[0]

    ref_Coleader = round(0.1 * tot_players ,0)
    ref_Elder= round(0.4 * tot_players,0) + ref_Coleader

    df_end["action"] = df_end.apply(action,axis=1)

    base=df_end[["rank","tag", 'name', 'role', 'expLevel', 'trophies', 'donations',
           'card_earned', 'battles_played', 'wins', 'loss', 'apr',"action"]]

    base.to_excel("./bases/base_" + v +"_"+ str(today)+ ".xlsx", index=False)

print('Feito!')

