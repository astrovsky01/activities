import yaml
import xmltodict

class activity:

    '''
    When all is run, available vars:
    activities: full yaml dict
    need: list of all tools from yaml
    steps: list of all steps in workflow
    final_list: dict of tools selected for each step
    '''

    def __init__(self, act_yaml):
        self.act_yaml = act_yaml

    def parser(self):
        '''Create dictionaries from files'''
        with open(self.act_yaml) as f:
            flow = yaml.load(f, Loader=yaml.FullLoader)
        self.activities = flow

    def tools_need(self):
        '''
        List of all possible tool ids from the yaml file
        '''
        need = []
        for step in self.activities:
            if self.activities[step]["multi"] == True:
                versions = list(self.activities[step].keys())[2:]
                for version in versions:
                    for x in self.activities[step][version]:
                        if x == "description":
                            pass
                        else:
                            need.append(self.activities[step][version][x]["tool_id"])
            else:
                for x in self.activities[step]:
                    if x == "description" or x == "multi":
                        pass
                    else:
                        need.append(self.activities[step][x]["tool_id"])
        self.need = need

    def step_select(self, step):
        '''
        For steps with multiple possiblities, return just the tools from selected option
        '''
        options = list(self.activities[step])[2:]
        for x in options:
            print(x + ":", self.activities[step][x]["description"])
        selection = input("Which version of this step would you like to use? ")
        return(selection)

    def flow_parse(self):
        '''
        From activities yaml, returns list of viable tools for each step
        '''
        steps = {}
        for step in list(self.activities.keys()):
            if self.activities[step]["multi"] == True:
                choice = self.step_select(step)
                tools = self.activities[step][choice]
                tools.pop("description")
            else:
                tools = self.activities[step]
                tools.pop("multi")
                tools.pop("description")
            steps[step] = tools
        self.steps = steps

    def tool_select(self):
        '''
        Takes in output from flow_parse() to allow user to select a final tool for each step
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
        for step in self.activities:
            if self.activities[step]["multi"] == True:
                versions = list(self.activities[step].keys())[2:]
                for version in versions:
                    for x in self.activities[step][version]:
                        if x == "description":
                            pass
                        else:
                            if self.activities[step][version][x]["tool_id"] in missing_list:
                                print("Missing tool:", x + ". Retrieve from toolshed to make available.")
                                remove.append([step, version, x])
            else:
                for x in self.activities[step]:
                        if x == "description" or x == "multi":
                            pass
                        else:
                            if self.activities[step][x]["tool_id"] in missing_list:
                                print("Missing tool:", x + ". Retrieve from toolshed to make available.")
                                remove.append([step, x])
        for tool in remove:
            if len(tool) == 3:
                del(self.activities[tool[0]][tool[1]][tool[2]])
            else:
                 del(self.activities[tool[0]][tool[1]])

class shedlist:

    def __init__(self, tool_xml):
        self.toolbox = tool_xml

    def parser(self):
        with open(self.toolbox) as f:
            tools = xmltodict.parse(f.read())
        tools = tools["toolbox"]
        self.toolbox = tools

    def installed(self):
        '''
        List of all currently installed tools
        '''
        installed = []
        for section in self.toolbox['section']:
            if type(section) == str:
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

def test():
    testyaml = """{'alignmap': {'description': 'asdfasdf',
                                'multi': True,
                                'align': {'description': 'TEST123',
                                    'kallisto': {'tool_id': 'kallistobus', 'description': 'qwerty'}},
                                'map': {'description': 'TEST345',
                                    'star': {'tool_id': 'starsolo', 'description': 'qwerty2'},
                                    'raceid': {'tool_id': 'raceid', 'description': 'qwerty2'}}},
                                'quant': {'description': 'asdfasdf2', 'multi': False,
                                    'alevin': {'tool_id': 'alevin', 'description': 'qwerty3'}}}"""
    act1 = activity("test")
    act1.activities = yaml.load(testyaml, Loader=yaml.Loader)

    shed1 = shedlist("test")
    shed1.toolbox =  """<?xml version="1.0"?>
    <toolbox>
        <section id="testing123" name="test" version="">
            <tool id="upload1" />
            <tool id="starsolo" />
            <tool id="ucsc_table_direct_archaea1" />
            <tool id="ebi_sra_main" />
            <tool id="modENCODEfly" />
            <tool id="kallistobus" />
        </section>
        <section/>
        <section id="asdf">
        </section>
    </toolbox>"""
    shed1.toolbox = xmltodict.parse(shed1.toolbox)
    shed1.toolbox = shed1.toolbox["toolbox"]
    shed1.installed()
    act1.tools_need()
    miss = missing(act1, shed1)
    if miss == ["raceid", "alevin"]:
        print("pass")
    else:
        print("fail")
