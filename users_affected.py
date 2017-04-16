from analysis import init_default, process_user_settings

def find_user_space_for_each_setting(list_of_users,dict_of_settings, settings_to_remove):
    settings_individual_user_space = []   
    #Process user space affected for single setting 
    for setting in settings_to_remove:
        percentage = dict_of_settings[setting].changedPercentage()
        settings_individual_user_space.append((setting, percentage))
    return settings_individual_user_space

def find_total_users_affected(list_of_users,dict_of_settings, settings_to_remove):
    user_space_inc = 0
    total_users = 0
    for user in list_of_users:
        total_users += 1
        for setting in settings_to_remove:
            if setting in user.getChangedSettings():
                user_space_inc += 1
                break
    percentage = round(100*user_space_inc/total_users,2)
    return percentage

default_settings = init_default('Tanda Settings Info.csv')
user_settings = process_user_settings('Tanda Organisation Settings.csv', default_settings)

while True:
    print(" \n\n\n")
    print("See the user space affected from removing/hiding settings. Type 'q' to quit")
    print("Type comma seperated setting names you want to remove")
    print("eg 'breaks_enabled' or 'breaks_enabled,managers_can_see_costs")
    settings_to_remove = input()
    if settings_to_remove == "q":
        break
    settings_to_remove = settings_to_remove.split(",")
    print(" ")
    try:
        individual = find_user_space_for_each_setting(user_settings,default_settings,settings_to_remove)
        total = find_total_users_affected(user_settings,default_settings,settings_to_remove)
        for setting_name,percentage in individual:
            print("Setting: "+setting_name +"; Users affected: "+ str(percentage)+"%")
        print("\nTotal user space affected: "+str(total)+"%\n")
    except KeyError as e:
        print("Invalid setting name: " + str(e))
    input("Press enter to go again ")



