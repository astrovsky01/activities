import activities
from unittest.mock import patch

def test_yaml_import():
   testyaml = "./test-data/test.yaml"
   test = activities.Activity(testyaml)
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
   testxml =  "./test-data/test.xml"
   test =  activities.Shedlist(testxml)
   test2 = OrderedDict([('section', [OrderedDict([('@id', 'testing123'), ('@name', 'test'), ('@version', ''), ('tool', [OrderedDict([('@id', 'upload1')]), OrderedDict([('@id', 'starsolo')]), OrderedDict([('@id', 'ucsc_table_direct_archaea1')]), OrderedDict([('@id', 'ebi_sra_main')]), OrderedDict([('@id', 'modENCODEfly')]), OrderedDict([('@id', 'kallistobus')])])]), None, OrderedDict([('@id', 'asdf')])])])
   assert test.toolbox == test2

def test_step_tools(monkeypatch):
    testyaml = "./test-data/test.yaml"
    test = activities.Activity(testyaml)
    with patch('builtins.input', return_value="align"):
        test.step_tools()
    assert test.steps == {'alignmap': {
    'kallisto': {'description': 'qwerty', 'tool_id': 'kallistobus'}},
    'quant': {'alevin': {'description': 'qwerty3', 'tool_id': 'alevin'}}}

def test_tool_select():
    testyaml = "./test-data/test.yaml"
    test = activities.Activity(testyaml)
    test.steps = {'alignmap': {
        'star': {'description': 'qwerty2', 'tool_id': 'starsolo'},
        'moon': {'description': 'qwerty2', 'tool_id': 'moonuno'}}}
    with patch('builtins.input', return_value="star"):
        test.tool_select()
    assert test.final_list == {'alignmap': 'starsolo'}

def test_tool_remove():
    testyaml = "./test-data/test.yaml"
    test = activities.Activity(testyaml)
    tool_list = ['starsolo']
    test.tools_remove(tool_list)
    assert test.full_file == {'alignmap': {'description': 'asdfasdf',
                'multi': True,
                'align': {'description': 'TEST123',
                    'kallisto': {'description': 'qwerty', 'tool_id': 'kallistobus'}},
                'map': {'description': 'TEST345',
                    'moon': {'description': 'qwerty2', 'tool_id': 'moonuno'}}},
            'quant': {'description': 'asdfasdf2',
                'multi': False,
                'alevin': {'description': 'qwerty3', 'tool_id': 'alevin'}}}

def test_installed_list():
    testxml =  "./test-data/test.xml"
    test =  activities.Shedlist(testxml)
    test.installed_list()
    test2 = ["upload1", "starsolo", "ucsc_table_direct_archaea1", "ebi_sra_main", "modENCODEfly", "kallistobus"]
    assert test.installed == test2

def test_tools_need():
   testyaml = "./test-data/test.yaml"
   test = activities.Activity(testyaml)
   test.tools_need()
   test2 = ["kallistobus", "moonuno", "starsolo", "alevin"]
   assert test.need == test2

def test_missing():
    testyaml = "./test-data/test.yaml"
    testyaml = activities.Activity(testyaml)
    testyaml.tools_need()
    testxml =  "./test-data/test.xml"
    testxml =  activities.Shedlist(testxml)
    testxml.installed_list()
    miss = activities.missing(testyaml, testxml)
    assert sorted(miss) == ['alevin', 'moonuno']
