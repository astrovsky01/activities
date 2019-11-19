import activities
from io import StringIO

stepstring = StringIO('align\n')

def test_yaml_import():
    testyaml = "./tests/test.yaml"
    test = activities.activity(testyaml)
    test.to_dict()
    test2 = {'alignmap': {'description': 'asdfasdf',
                'multi': True,
                'align': {'description': 'TEST123',
                    'kallisto': {'description': 'qwerty', 'tool_id': 'kallistobus'}},
                'map': {'description': 'TEST345',
                    'star': {'description': 'qwerty2', 'tool_id': 'starsolo'},
                    'moon': {'description': 'qwerty2', 'tool_id': 'moonuno'}}},
            'quant': {'description': 'asdfasdf2',
                'multi': False,
                'alevin': {'description': 'qwerty3', 'tool_id': 'alevin'}}}
    assert test.full_file == test2

def test_xml_import():
    from collections import OrderedDict
    testxml =  "./tests/test.xml"
    test =  activities.shedlist(testxml)
    test.to_dict()
    test2 = OrderedDict([('section', [OrderedDict([('@id', 'testing123'), ('@name', 'test'), ('@version', ''), ('tool', [OrderedDict([('@id', 'upload1')]), OrderedDict([('@id', 'starsolo')]), OrderedDict([('@id', 'ucsc_table_direct_archaea1')]), OrderedDict([('@id', 'ebi_sra_main')]), OrderedDict([('@id', 'modENCODEfly')]), OrderedDict([('@id', 'kallistobus')])])]), None, OrderedDict([('@id', 'asdf')])])])
    assert test.toolbox == test2

def test_installed():
    testxml =  "./tests/test.xml"
    test =  activities.shedlist(testxml)
    test.to_dict()
    test.installed_list()
    test2 = ["upload1", "starsolo", "ucsc_table_direct_archaea1", "ebi_sra_main", "modENCODEfly", "kallistobus"]
    assert test.installed == test2

def test_tools_need():
    testyaml = "./tests/test.yaml"
    test = activities.activity(testyaml)
    test.to_dict()
    test.tools_need()
    test2 = ["kallistobus", "moonuno", "starsolo", "alevin"]
    assert test.need == test2

def test_step_selection(patch):
    testyaml = "./tests/test.yaml"
    test = activities.activity(testyaml)
    test.to_dict()
    patch.setattr('sys.stdin', stepstring)
    assert step_selection() == ['align', 'quant']
