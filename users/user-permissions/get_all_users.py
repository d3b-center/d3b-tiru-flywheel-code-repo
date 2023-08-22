# Generate a list of all Flywheel users & output to Excel file
#   Includes group membership and permission info
#
#   Ariana Familiar
#   April 2021


import flywheel
import pandas as pd

api_key = '<API-key>'

fw = flywheel.Client(api_key)

## Generate dataframe of info for all users on the instance
usr_list = fw.get_all_users()

df = pd.DataFrame()
for usr in usr_list:
    row = dict()
    row['FirstName'] = usr['firstname']
    row['LastName'] = usr['lastname']
    row['E-mail'] = usr['email']
    row['Disabled'] = usr['disabled']
    df = df.append(row, ignore_index=True)

## Add group information (membership & permissions)
group_col = (['None'] * len(df))
groupP_col = (['None'] * len(df))
for group in fw.groups():
    for usr in group.permissions:
        ## match this user to full list
        row_ind=df.index[df['E-mail']==usr.id].tolist()
        ## add group
        if 'None' in group_col[row_ind[0]]: # replace "None" if this is the first group for the user
            group_col[row_ind[0]] = group.id
            groupP_col[row_ind[0]] = usr.access
        else: # otherwise add this group to the list for the user
            group_col[row_ind[0]] = group_col[row_ind[0]]+', '+group.id
            groupP_col[row_ind[0]] = groupP_col[row_ind[0]]+', '+usr.access

df['Groups'] = group_col
df['GroupPermissions'] = groupP_col

## Save to output file
df = df[['FirstName','LastName','E-mail','Disabled','Groups','GroupPermissions']]
df.to_csv('Flywheel_users.csv')