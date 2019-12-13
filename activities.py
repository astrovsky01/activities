import yaml
import xmltodict

class Activity:
    '''
    When all is run, available vars:
    activities: full yaml dict
    need: list of all tools from yaml
    steps: list of all steps in workflow
    final_list: dict of tools selected for each step
    '''

    def __init__(self, activities_yaml):
        self._load(activities_yaml)

    def _load(self, src):
        with open(src) as f:
            self.full_file = yaml.load(f, Loader=yaml.FullLoader)

    def tools_need(self):
        '''
        List of all possible tool ids from the yaml file
        '''
        need = []
        for step in self.full_file:
            if self.full_file[step]["multi"] == True:
                versions = list(self.full_file[step].keys())[2:]
                for version in versions:
                    for x in self.full_file[step][version]:
                        if x != "description" and x != 'multi':
                            need.append(self.full_file[step][version][x]["tool_id"])
            else:
                for x in self.full_file[step]:
                    if x == "description" or x == "multi":
                        pass
                    else:
                        need.append(self.full_file[step][x]["tool_id"])
        self.need = need

    def _get_step_options(self, activity_step):
        '''Breaks an activity step into all possible versions'''
        return list(self.full_file[activity_step])[2:]

    def _get_step(self):
        selection = input("Which version of this step would you like to use? ")
        return selection

    def _step_select(self, step):
        '''
        For steps with multiple possiblities, return just the tools from selected option
        '''
        for option in self._get_step_options(step):
            print(option + ":", self.full_file[step][option]["description"])
        return self._get_step()

    def step_tools(self):
        '''
        From activities yaml, returns list of viable tools for each step
        '''
        steps = {}
        for step in self.full_file.keys():
            if self.full_file[step]["multi"] == True:
                choice = self._step_select(step)
                tools = self.full_file[step][choice]
                tools.pop("description")
            else:
                tools = self.full_file[step]
                tools.pop("multi")
                tools.pop("description")
            steps[step] = tools
        self.steps = steps

    def tool_select(self):
        '''
        Takes in output from step_tools() to allow user to select a final tool for each step
        Format of final dictionary:
        key: step_name
        value: galaxy tool_id
        '''
        final_list = {}
        for x in self.steps:
            if len(self.steps[x]) > 1:
                print("There are multiple tool choices for", x)
                for y in self.steps[x]:
                    print(y, self.steps[x][y]["description"])
                tool_choice = input("Which tool to use? ")
                tool_choice = self.steps[x][tool_choice]["tool_id"]
            else:
                tool_choice = "".join(list(self.steps[x].keys()))
                tool_choice = self.steps[x][tool_choice]["tool_id"]
            final_list[x] = tool_choice
        self.final_list = final_list

    def tools_remove(self, missing_list):
        '''
        Removes all tools not installed on the instance from the activities dict and tells user what is not avaliable
        '''
        remove = []
        for step in self.full_file:
            if self.full_file[step]["multi"] == True:
                versions = list(self.full_file[step].keys())[2:]
                for version in versions:
                    for x in self.full_file[step][version]:
                        if x == "description":
                            pass
                        else:
                            if self.full_file[step][version][x]["tool_id"] in missing_list:
                                print("Missing tool:", x + ". Retrieve from toolshed to make available.")
                                remove.append([step, version, x])
            else:
                for x in self.full_file[step]:
                        if x == "description" or x == "multi":
                            pass
                        else:
                            if self.full_file[step][x]["tool_id"] in missing_list:
                                print("Missing tool:", x + ". Retrieve from toolshed to make available.")
                                remove.append([step, x])
        for tool in remove:
            if len(tool) == 3:
                del(self.full_file[tool[0]][tool[1]][tool[2]])
            else:
                 del(self.full_file[tool[0]][tool[1]])

class Shedlist:

    def __init__(self, tool_xml):
        self._load(tool_xml)

    def _load(self, src):
        with open(src) as f:
            self.toolbox = xmltodict.parse(f.read())["toolbox"]

    def installed_list(self):
        '''
        List of all currently installed tools
        '''
        installed = []
        for section in self.toolbox['section']:
            if isinstance(section, str):
                #only a single section in toolshed for some reason
                for tool in self.toolbox['section']['tool']:
                    installed.append(tool["@id"])
            elif type(section) == type(None):
                pass
            else:
                if 'tool' in section:
                    tools = section['tool']
                    if isinstance(tools, list):  # we have many
                        for tool in tools:
                            installed.append(tool['@id'])
                    else:
                        installed.append(tools['@id'])
        if "tool" in self.toolbox.keys():
            #outside a section
            for entry in self.toolbox["tool"]:
                installed.append(entry['@id'])
        self.installed = installed

def missing(activities_obj, shed_obj):
    '''
    Return list of tools not present in toolshed
    '''
    miss = list(set(activities_obj.need).difference(set(shed_obj.installed)))
    return(miss)
