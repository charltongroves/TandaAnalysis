import csv
import numpy as np
import scipy.stats as stats
import pylab as pl

"""
A class which stores and processes settings information
"""
class GenericSetting():
    def getName(self):
       return self.name

    def getDefault(self):
       return self.default

    def getImpact(self):
       return self.impact

    def getChanged(self):
        return self.changed

    def getNotChanged(self):
        return self.not_changed

    def changedPercentage(self):
        total = (self.changed+self.not_changed)
        if total == 0:
            return -1
        return round(100*self.changed/total,2)
    def getMostCommon(self):
        return max(self.commonSetting, key=self.commonSetting.get)
    def addSettingValue(self,value):
        if value in self.commonSetting:
            self.commonSetting[value] += 1
        else:
            self.commonSetting[value] = 1
    def processActual(self, value):
        value = value.lower()
        self.addSettingValue(value)
        if (value == self.default):
            self.not_changed += 1
        else:
            self.changed += 1

    def isDefault(self, value):
        value = value.lower()
        return (value == self.default)

    def __init__(self, name, default, data_type, impact):
        self.name = name
        self.impact = impact
        self.data_type = data_type
        self.default = default.lower()
        self.commonSetting = {default:0}
        self.changed = 0
        self.not_changed = 0
    
"""
A class that inherits GenericSettings and overrides its functionality
to suit numeric values
"""
class NumericSetting(GenericSetting):
    def isDefault(self, value):
        value = str(float(value)) #numbers are always floats
        return (value == self.default)

    def processActual(self, value):
        value = str(float(value)) #numbers are always floats
        self.addSettingValue(value)
        if (value == self.default):
            self.not_changed += 1
        else:
            self.changed += 1
    def __init__(self, name, default, data_type, impact):
        default = str(float(default)) #numbers are always floats
        super().__init__(name, default, data_type, impact)

"""
A class that processes a users settings
"""
class UserSettings():
    def getChangedSettings(self):
        return self.changed_settings
    def appendChangedSetting(self, setting_name):
        self.changed_settings.append(setting_name)
    def changedPercentage(self):
        total = (self.changed_implicit+self.changed_explicit+\
                self.not_changed_implicit+ self.not_changed_explicit)
        changed = self.changed_implicit + self.changed_explicit
        return round((changed/total)*100, 2)

    def addChange(self, isDefault, impact, name):
        if isDefault:
            if impact == "Implicit":
                self.not_changed_implicit += 1
            else:
                self.not_changed_explicit += 1
        else:
            self.appendChangedSetting(name)
            if impact == "Implicit":
                self.changed_implicit += 1
            else:
                self.changed_explicit += 1

    def __init__(self):
        self.changed_explicit = 0
        self.not_changed_explicit = 0
        self.changed_implicit = 0
        self.not_changed_implicit = 0
        self.changed_settings = []
"""
Creates a GenericSettings object for each setting located in a settings info csv
Returns a dict of Settings names to their corresponding object
"""
def init_default(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        default_settings_list = list(reader)
    default_settings_list.pop(0) #remove meta info
    default_settings = {}
    for s in default_settings_list:
        if s[2] == "Numeric":
            default_settings[s[0]] = NumericSetting(s[0],s[1],s[2],s[3])
        else:
            default_settings[s[0]] = GenericSetting(s[0],s[1],s[2],s[3])
    return default_settings
"""
Iterates through users' settings and creats a UsersSettings object for them.
Processes their defined settings and updates the GenericSettings/UsersSettings objects accordingly
Returns a list of UserSettings objects
"""
def process_user_settings(filename, default_settings):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        user_settings_list = list(reader)
    setting_names = user_settings_list.pop(0)
    user_settings = []
    i = 0
    for user in user_settings_list:
        user_settings.append(UserSettings())
        j = 0
        for value in user:
            setting = default_settings.get(setting_names[j])
            isDefault = setting.isDefault(value)
            user_settings[i].addChange(isDefault, setting.getImpact, setting.getName())
            setting.processActual(value)
            j += 1
        i += 1
    return user_settings
"""
Creates a histogram plot of the distribution of users who change >x% of settings.
Saves it to results/dist.png
"""
#The distribution of users that change > x% of settings overall.
def get_std_dist_users(user_settings):
    percentages = []
    for user in user_settings:
        percentages.append(user.changedPercentage()/100)
    percentages.sort()
    pl.title('Distribution of users that change > x% of settings overall')
    pl.xlabel('Percentage of settings changed from default: 1.0=100%')
    pl.ylabel('Distribution of Users: 1.0=100%')
    pl.hist(percentages,100, normed=True,cumulative=-1)
    pl.savefig('results/Dist.png')

"""
Saves processed information to .csv files in the results folder
"""
def print_info(default_settings, user_settings):

    #The percentage of users which change each setting.
    with open("results/Settings Percent Changed.csv", 'w') as f:
        f.write("Setting Name,Percent Changed,Impact\n")
        for name, setting in default_settings.items():
            percent_string = str(setting.changedPercentage()) +"%" if (setting.changedPercentage() >= 0) else "no data"
            new_entry = name + "," + str(percent_string) + "," + setting.getImpact() +  "\n"
            f.write(new_entry)
    #A general method for determining the user space which will be affected should a 
    #setting (or set of settings) be removed/hidden.
    with open("results/Impact Percent Changed.csv", 'w') as f:
        f.write("Impact, Avg Settings Changed\n")
        implicit_total = 0
        implicit_inc = 0
        explicit_total = 0
        explicit_inc = 0
        for name, setting in default_settings.items():
            if setting.getImpact() == "Explicit":
                explicit_inc += 1
                explicit_total += setting.changedPercentage()
            elif setting.getImpact() == "Implicit":
                implicit_inc += 1
                implicit_total += setting.changedPercentage()
            else:
                print(setting.getName() + "has an invalid impact: " + setting.getImpact())
        implicit_percent = round(implicit_total/implicit_inc,2)
        implicit_entry = "Implicit," + str(implicit_percent)+"%\n"
        explicit_percent = round(explicit_total/explicit_inc,2)
        explicit_entry = "Explicit," + str(explicit_percent)+"%\n"
        f.write(explicit_entry)
        f.write(implicit_entry)
    #The difference in configuration between explicit and implicit settings 
    with open("results/Most Common Setting Value.csv", 'w') as f:
        f.write("Setting Name, Default Setting,Most Common Setting\n")
        for name, setting in default_settings.items():
            entry = name + "," + setting.getDefault() +"," + setting.getMostCommon() + "\n"
            f.write(entry)

if __name__ == "__main__":
    default_settings = init_default('Tanda Settings Info.csv')
    user_settings = process_user_settings('Tanda Organisation Settings.csv', default_settings)
    print_info(default_settings, user_settings)
    get_std_dist_users(user_settings)


