import warnings
import os
import json
import re
from datetime import datetime
import ipywidgets as widgets

# import das_lib.das_core as das
from prof_test_upl import *
from prof_dataset_cmp_services import *


class SanityTester:
    operating_environment_map = {
        'Production': das.OperatingEnvironment.PROD,
        'OSA': das.OperatingEnvironment.OSA,
        'Integration': das.OperatingEnvironment.INTG
    }

    operating_mode_map = {
        'Online (through agents)': das.OperatingMode.ONLINE,
        'Offline (from local storage)': das.OperatingMode.OFFLINE
    }

    config_file = 'upl_test_config.json'

    # Test configuration
    try:
        tester_name = re.match("jupyter-(.+)", os.uname()[1]).group(1).replace("-20", " ") if re.match("jupyter-(.+)",
                                                                                                   os.uname()[
                                                                                                       1]) else "tester"
    # uname not supported on Windows
    except AttributeError as e:
        tester_name = "tester"

    config = {
        # GUI parameters (with default assignments)
        'tester': tester_name,
        'test_session_id': datetime.now().strftime('%Y-%m-%d'),
        'reports_root': '/home/jovyan/shared/UPLValidation/',
        'source_system': 'Epoque',
        'source_operating_environment': 'Production',        
        'source_operating_mode': 'Online (through agents)',
        'target_system': 'KimeAPI',
        'target_operating_environment': 'Production',
        'target_operating_mode': 'Online (through agents)',       
        'dosys_fields_selection': [],
        'rp_dump': False,
        'rp_project': '',
        'rp_max_num_tests': 0,
        'rp_dump_failures_only': False,
        'rp_test_suite_name_header': '',
        'generate_status_matrix': False,
        'input_data': [],

        # Additional parameters NOT included in the GUI (at least, not yet)
        'confirmation_threshold': 100000,
        'chunk_size': 50000,
        'persistent_mode': False,
        'dump_repository': None,
        'parity_batch_size': 2000,
        'log_individual_match_checks': False,
        'empty_counted': False,
        'display_type': 'none',
        'dbg': False,
        'csv_repository': None,
        'output_format': 'xls'
    }

    # GUI configuration widgets
    wid_tester = None
    wid_test_session_id = None
    wid_reports_root = None
    wid_source_system = None
    wid_source_operating_environment = None
    wid_source_operating_mode = None
    wid_target_system = None
    wid_target_operating_environment = None
    wid_target_operating_mode = None
    wid_field = None
    wid_rp_dump = None
    wid_rp_project = None
    wid_rp_max_num_tests = None
    wid_rp_dump_failures_only=None
    wid_rp_test_suite_name_header=None
    wid_generate_status_matrix = None
    wid_input_files_container = None
    wid_input_queries_container = None
    wid_out = None

    # the gui widget
    wid_gui = None

    def __init__(self):
        pass

    def test_session_config(self):
        style = {'description_width': 'initial'}

        # session id
        self.wid_test_session_id = widgets.Text(
            value=self.config['test_session_id'],
            placeholder='Session identifier e.g. 20190327',
            description='Session Identifier',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # reports root
        self.wid_reports_root = widgets.Text(
            value=self.config['reports_root'],
            placeholder='location of the reports',
            description='Reports root',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # tester
        self.wid_tester = widgets.Text(
            value=self.config['tester'],
            placeholder='The name of the tester',
            description='Tester name',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # source system
        self.wid_source_system = widgets.Dropdown(
            options=['Epoque', 'KimeAPI'],
            value=self.config['source_system'],
            description='Reference system',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # source operating environment (e.g. INTG/OSA/PROD for source system)
        self.wid_source_operating_environment = widgets.Dropdown(
            options=self.operating_environment_map.keys(),
            value=self.config['source_operating_environment'],
            description='Operating environment of reference system',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # operating mode for source
        self.wid_source_operating_mode = widgets.Dropdown(
            options=self.operating_mode_map.keys(),
            value=self.config['source_operating_mode'],
            description='Data access mode of reference system',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # target system
        self.wid_target_system = widgets.Dropdown(
            options=['KimeAPI', 'SSL'],
            value=self.config['target_system'],
            description='Target system',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # target operating environment (e.g. OSA/PROD for target system)
        self.wid_target_operating_environment = widgets.Dropdown(
            options=self.operating_environment_map.keys(),
            value=self.config['target_operating_environment'],
            description='Operating environment of target system',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # operating mode for target (kimeAPI or SSL)
        self.wid_target_operating_mode = widgets.Dropdown(
            options=self.operating_mode_map.keys(),
            value=self.config['target_operating_mode'],
            description='Data access mode of target system',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))


        grid = widgets.GridspecLayout(12, 20)
        grid[0, 2:13] = self.wid_test_session_id
        grid[1, 2:13] = self.wid_reports_root
        grid[2, 2:13] = self.wid_tester

        grid[4, 2:13] = self.wid_source_system
        grid[5, 2:13] = self.wid_source_operating_environment
        grid[6, 2:13] = self.wid_source_operating_mode

        grid[8, 2:13] = self.wid_target_system
        grid[9, 2:13] = self.wid_target_operating_environment
        grid[10, 2:13] = self.wid_target_operating_mode

        return grid

    def dosys_fields_config(self):
        style = {'description_width': 'initial'}

        field_list_gds = ["APL", "CPRE", "DS", "EAPP", "IC", "IN", "INA", "INC", "PA", "PAA", "PAC", "PRLA", "RP",
                          "RPA", "RPC", "TI", "TIDE", "TIFR", "TIOL"]
        field_list_gds_kime_docdb = ['DOB', 'LINK', 'ORAP', 'PR']
        field_list_kime_docdb = ["AP", "C2", "C2NP", "CA", "CCA", "CCI", "CCLS", "CDIR", "CI", "CL", "CLC", "CLEA",
                                 "CPRO", "CT", "CTNP", "EX", "EXAM", "EXNP", "FAMN", "FLDS", "IS", "ISNP", "KW", "NC",
                                 "NCNP", "OC", "OCAP", "OCNP", "OCNS", "OP", "OPAP", "OPNP", "PD", "PN", "PNFP", "REXM",
                                 "RF", "RFAP", "RFNP", "ROSS", "TXT"]
        all_fields = field_list_gds + field_list_gds_kime_docdb + field_list_kime_docdb

        fields_selection = self.config['dosys_fields_selection']

        ncols = 14
        grid = widgets.GridspecLayout(10, ncols)

        wid_field = {}
        for field in all_fields:
            wid_field[field] = widgets.Checkbox(
                value=(field in fields_selection),
                description=field,
                disabled=False,
                style=style,
                layout=widgets.Layout(height="auto", width="auto"))
        grid[1, 0:] = widgets.HTML(value="<b>GDS Fields</b>")
        for index, field in enumerate(field_list_gds):
            grid[2 + index // ncols, index % ncols] = wid_field[field]

        grid[4, 0:] = widgets.HTML(value="<b>GDS-Kime-DocDB Fields</b>")
        for index, field in enumerate(field_list_gds_kime_docdb):
            grid[5 + index // ncols, index % ncols] = wid_field[field]

        grid[6, 0:] = widgets.HTML(value="<b>Kime-DocDB Fields</b>")
        for index, field in enumerate(field_list_kime_docdb):
            grid[7 + index // ncols, index % ncols] = wid_field[field]

        self.wid_field = wid_field

        wid_selections = widgets.Dropdown(
            options=['-', 'Select All', 'Unselect All',
                     'Select GDS', 'Unselect GDS',
                     'Select GDS-KIME-DOCDB', 'Unselect GDS-KIME-DOCDB',
                     'Select KIME-DOCDB', 'Unselect KIME-DOCDB'],
            value='-',
            description='',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))
        grid[0, 2:7] = wid_selections

        def select_group(change):
            sel = set()
            for wdb in wid_field.values():
                if wdb.value:
                    sel.add(wdb.description)
            if change['new'] == 'Select All':
                sel = set(all_fields)
            elif change['new'] == 'Unselect All':
                sel = set()
            elif change['new'] == 'Select GDS':
                sel = sel | set(field_list_gds)
            elif change['new'] == 'Select GDS-KIME-DOCDB':
                sel = sel | set(field_list_gds_kime_docdb)
            elif change['new'] == 'Select KIME-DOCDB':
                sel = sel | set(field_list_kime_docdb)
            elif change['new'] == 'Unselect GDS':
                sel = sel - set(field_list_gds)
            elif change['new'] == 'Unselect GDS-KIME-DOCDB':
                sel = sel - set(field_list_gds_kime_docdb)
            elif change['new'] == 'Unselect KIME-DOCDB':
                sel = sel - set(field_list_kime_docdb)
            else:
                return
            for wdb in wid_field.values():
                wdb.value = (wdb.description in sel)

        wid_selections.observe(select_group, names='value')
        return grid

    ###
    def report_portal_config(self):
        style = {'description_width': 'initial'}

        # report portal dump
        self.wid_rp_dump = widgets.Checkbox(
            value=self.config['rp_dump'],
            description='<b>Perform dump</b>',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # project name
        self.wid_rp_project = widgets.Text(
            value=self.config['rp_project'],
            placeholder='',
            description='Project Name',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # Max number of tests
        self.wid_rp_max_num_tests = widgets.BoundedIntText(
            value=self.config['rp_max_num_tests'],
            min=1,
            max=1000000,
            step=1,
            placeholder='1000',
            description='Max number of tests',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))
        
        # report only failures 
        self.wid_rp_dump_failures_only = widgets.Checkbox(
            value=self.config['rp_dump_failures_only'],
            description='<b>Report only failures</b>',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        # Launch name
        self.wid_rp_test_suite_name_header = widgets.Text(
            value=self.config['rp_test_suite_name_header'],
            placeholder='',
            description='Launch Name',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        grid = widgets.GridspecLayout(5, 20)
        grid[0, 2:7] = self.wid_rp_dump
        grid[1, 2:12] = self.wid_rp_project
        grid[2, 2:12] = self.wid_rp_max_num_tests
        grid[3, 2:12] = self.wid_rp_dump_failures_only 
        grid[4, 2:12] = self.wid_rp_test_suite_name_header
        return grid

    ###
    def generate_status_matrix_config(self):
        style = {'description_width': 'initial'}

        # report portal dump
        self.wid_generate_status_matrix = widgets.Checkbox(
            value=self.config['generate_status_matrix'],
            description='<b>Generate status matrix</b>',
            disabled=False,
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))
        
        grid = widgets.GridspecLayout(1, 20)
        grid[0, 2:7] = self.wid_generate_status_matrix
        return grid

    ###
    def test_input_file_config(self):
        style = {'description_width': 'initial'}
        wid_rows_container = widgets.VBox()

        wid_add_button = widgets.Button(
            description='',
            disabled=False,
            button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Add new input data file',
            icon='plus',
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        def add_row(set_id='', path=''):
            local_grid = widgets.GridspecLayout(1, 30)
            local_grid[0, 0:5] = widgets.Text(value=set_id,
                                              placeholder='set unique identifier',
                                              description='',
                                              style=style,
                                              layout=widgets.Layout(height="auto", width="auto"))
            local_grid[0, 5:25] = widgets.Text(value=path,
                                               placeholder='path to AN file',
                                               description='',
                                               style=style,
                                               layout=widgets.Layout(height="auto", width="auto"))
            wid_delete_button = widgets.Button(
                description='',
                disabled=False,
                icon='trash',
                button_style='danger',  # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Remove',
                style=style,
                layout=widgets.Layout(height="auto", width="auto"))
            local_grid[0, 25:27] = wid_delete_button
            wid_rows_container.children += (local_grid,)

            def sel_delete_onclick(d):
                new_chil = []
                for gr in wid_rows_container.children:
                    if gr[0, 25] != d:
                        new_chil.append(gr)
                wid_rows_container.children = new_chil

            wid_delete_button.on_click(sel_delete_onclick)

        for row in self.config['input_data']:
            if row['type'] == 'file':
                add_row(row['set_id'], row['path'])

        self.wid_input_files_container = wid_rows_container

        def sel_add_onclick(b):
            b.disabled = True
            add_row()
            b.disabled = False

        wid_add_button.on_click(sel_add_onclick)

        grid_label_button = widgets.GridspecLayout(2, 30)
        grid_label_button[0, 1:12] = widgets.HTML('<b>Configure input test sets from files</b>')
        grid_label_button[1, 2:4] = wid_add_button
        grid_rows_container = widgets.GridspecLayout(1, 30)
        grid_rows_container[0, 2:27] = wid_rows_container
        grid_empty_row = widgets.GridspecLayout(1, 1)
        grid_empty_row[0, 0] = widgets.HTML(" ")
        stack = widgets.VBox([grid_empty_row, grid_label_button, grid_rows_container, grid_empty_row],
                             layout=widgets.Layout(border='1px solid #bbb'))
        return stack

        ###

    def test_input_query_config(self):
        style = {'description_width': 'initial'}
        wid_rows_container = widgets.VBox()

        wid_add_button = widgets.Button(
            description='',
            disabled=False,
            button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Add new input data file',
            icon='plus',
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        def add_row(set_id='', query='', n_samples=0):
            local_grid = widgets.GridspecLayout(1, 30)
            local_grid[0, 0:5] = widgets.Text(value=set_id,
                                              placeholder='set unique identifier',
                                              description='',
                                              style=style,
                                              layout=widgets.Layout(height="auto", width="auto"))
            local_grid[0, 5:25] = widgets.Text(value=query,
                                               placeholder='query in EPOQUE language',
                                               description='',
                                               style=style,
                                               layout=widgets.Layout(height="auto", width="auto"))
            local_grid[0, 25:27] = widgets.IntText(value=n_samples,
                                                   placeholder='nsamples',
                                                   description='',
                                                   style=style,
                                                   layout=widgets.Layout(height="auto", width="auto"))
            wid_delete_button = widgets.Button(
                description='',
                disabled=False,
                icon='trash',
                button_style='danger',  # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Remove',
                style=style,
                layout=widgets.Layout(height="auto", width="auto"))
            local_grid[0, 27:29] = wid_delete_button
            wid_rows_container.children += (local_grid,)

            def sel_delete_onclick(d):
                new_chil = []
                for gr in wid_rows_container.children:
                    if gr[0, 27] != d:
                        new_chil.append(gr)
                wid_rows_container.children = new_chil

            wid_delete_button.on_click(sel_delete_onclick)

        for row in self.config['input_data']:
            if row['type'] == 'query':
                add_row(row['set_id'], row['query'], row['num_samples'])

        self.wid_input_queries_container = wid_rows_container

        def sel_add_onclick(b):
            b.disabled = True
            add_row()
            b.disabled = False

        wid_add_button.on_click(sel_add_onclick)

        grid_label_button = widgets.GridspecLayout(2, 30)
        grid_label_button[0, 1:12] = widgets.HTML('<b>Configure input test sets from queries</b>')
        grid_label_button[1, 2:4] = wid_add_button
        grid_rows_container = widgets.GridspecLayout(1, 30)
        grid_rows_container[0, 2:27] = wid_rows_container
        grid_empty_row = widgets.GridspecLayout(1, 1)
        grid_empty_row[0, 0] = widgets.HTML(" ")
        stack = widgets.VBox([grid_empty_row, grid_label_button, grid_rows_container, grid_empty_row],
                             layout=widgets.Layout(border='1px solid #bbb'))
        return stack

        ###

    def test_actions_config(self):
        style = {'description_width': 'initial'}

        # Button for loading configuration
        wid_load_config_button = widgets.Button(
            description='Load Configuration',
            disabled=False,
            button_style='info',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Load last saved configuration',
            icon='',
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        def sel_load_config_onclick(b):
            b.disabled = True
            self.load_config()
            b.disabled = False

        wid_load_config_button.on_click(sel_load_config_onclick)

        # Button for saving configuration
        wid_save_config_button = widgets.Button(
            description='Save Configuration',
            disabled=False,
            button_style='info',
            tooltip='Save this configuration',
            icon='',
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        def sel_save_config_onclick(b):
            b.disabled = True
            self.save_config()
            b.disabled = False

        wid_save_config_button.on_click(sel_save_config_onclick)

        # Button for executing the Test
        wid_run_test_button = widgets.Button(
            description='Perform Test',
            disabled=False,
            button_style='success',
            tooltip='Start the configured test session',
            icon='check',
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        def sel_run_test_onclick(b):
            b.disabled = True
            with self.wid_out:
                self.acquire_config()
                self.run_test()
            b.disabled = False

        wid_run_test_button.on_click(sel_run_test_onclick)

        # Button for executing the DASHBOARD GENERATION
        wid_perform_dashboard_button = widgets.Button(
            description='Update Dashboard',
            disabled=False,
            button_style='info',
            tooltip='Generate the dashboard for all available sessions',
            icon='',
            style=style,
            layout=widgets.Layout(height="auto", width="auto"))

        def sel_perform_dashboard_onclick(b):
            b.disabled = True
            with self.wid_out:
                self.acquire_config()
                self.perform_summary_report_generation()
                self.perform_dashboard_generation()
            b.disabled = False

        wid_perform_dashboard_button.on_click(sel_perform_dashboard_onclick)

        grid_actions = widgets.GridspecLayout(3, 31, layout=widgets.Layout(border='1px solid #bbb'))
        grid_actions[1, 2:6] = wid_load_config_button
        grid_actions[1, 6:10] = wid_save_config_button
        grid_actions[1, 11:16] = wid_run_test_button
        grid_actions[1, 17:21] = wid_perform_dashboard_button
        return grid_actions

    ###
    def test_output_config(self):
        self.wid_out = widgets.Output(layout=widgets.Layout(height='600px', overflow='auto'))
        title = widgets.HTML('<b><center>Output</center></b>')
        return widgets.VBox([title, self.wid_out], layout=widgets.Layout(border='1px solid #bbb'))

    # GUI instantiation method
    def start(self, nogui=False, useconfig=True):

        if nogui:
            try:
                with open(self.config_file, 'r') as fp:
                    self.config = json.load(fp)
                    self.run_test()
                    return
            except Exception as e:
                print("Could not load configuration!", e)
                return

        if useconfig:
            try:
                with open(self.config_file, 'r') as fp:
                    self.config = json.load(fp)
            except Exception as e:
                pass

        wid_test_session_conf = self.test_session_config()
        wid_dosys_fields_conf = self.dosys_fields_config()
        wid_report_portal_conf = self.report_portal_config()
        wid_generate_status_matrix_conf = self.generate_status_matrix_config()

        wid_test_conf = widgets.Accordion(
            children=[wid_test_session_conf, wid_dosys_fields_conf, wid_report_portal_conf, wid_generate_status_matrix_conf])
        wid_test_conf.set_title(0, 'Test session configuration')
        wid_test_conf.set_title(1, 'Dosys fields selection')
        wid_test_conf.set_title(2, 'Report Portal configuration')
        wid_test_conf.set_title(3, 'Status Matrix configuration')

        wid_test_input_file = self.test_input_file_config()
        wid_test_input_query = self.test_input_query_config()
        wid_test_actions = self.test_actions_config()
        wid_test_output = self.test_output_config()

        gui_style = """<style>
                              @import url('https://fonts.googleapis.com/css?family=MYFONT&display=swap');
                              .gui input { background-color:#f5f5f5 !important;
                                           font-family: 'MYFONT', sans-serif !important;}
                              .gui select { background-color:#f5f5f5 !important; 
                                            font-family: 'MYFONT', sans-serif !important;} 
                              .gui button { font-family: 'MYFONT', sans-serif !important;} 
                              .gui .p-Collapse-header { background-color:#f3f3f3 !important; }
                              .gui .p-Collapse-contents { background-color:#fcfcfc !important; }
                              .gui .widget-html-content { font-size:16px !important}
                              .gui .widget-output { background-color:#fefefe !important; }
                              .gui { background-color:#fcfcfc !important; 
                                     font-family: 'MYFONT', sans-serif !important;
                                     font-size: medium !important;}  
                       </style>""".replace("MYFONT", "Rubik")

        wid_gui = widgets.VBox([widgets.HTML(gui_style),
                                wid_test_conf,
                                wid_test_input_file,
                                wid_test_input_query,
                                wid_test_actions,
                                wid_test_output])
        wid_gui.add_class('gui')
        display(wid_gui)
        self.wid_gui = wid_gui

    ###
    def acquire_config(self):
        config = self.config

        # Custom header for the reports, additional parameters are filled in automatically
        config['tester'] = self.wid_tester.value

        # Session identifier (by default assigned to the timestamp)
        config['test_session_id'] = self.wid_test_session_id.value

        # Root directory containing the reports
        config['reports_root'] = self.wid_reports_root.value

        # Source system for test execution
        config['source_system'] = self.wid_source_system.value

        # Source operating environment
        config['source_operating_environment'] = self.wid_source_operating_environment.value

        # Operating mode source
        config['source_operating_mode'] = self.wid_source_operating_mode.value

        # Target system for test execution
        config['target_system'] = self.wid_target_system.value

        # Target operating environment
        config['target_operating_environment'] = self.wid_target_operating_environment.value

        # Operating mode target (KimeAPI or SSL)
        config['target_operating_mode'] = self.wid_target_operating_mode.value

        # DOSYS Fields
        config['dosys_fields_selection'] = []
        for wdb in self.wid_field.values():
            if wdb.value:
                config['dosys_fields_selection'].append(wdb.description)

                # Report Portal dump
        config['rp_dump'] = self.wid_rp_dump.value

        # Report Portal project name
        config['rp_project'] = self.wid_rp_project.value

        # Report Portal max number of tests
        config['rp_max_num_tests'] = self.wid_rp_max_num_tests.value
        
        # Report Portal report only failures
        config['rp_dump_failures_only'] = self.wid_rp_dump_failures_only.value
        
        # Report Portal Launch Name
        config['rp_test_suite_name_header'] = self.wid_rp_test_suite_name_header.value

        # Perform status matrix generation 
        config['generate_status_matrix'] = self.wid_generate_status_matrix.value
        
        # Retrieve the test sets settings
        input_data = []

        # 1. Input Data from Files
        for g in self.wid_input_files_container.children:
            line_cfg = {'type': 'file',
                        'set_id': g[0, 0].value,
                        'path': g[0, 5].value}
            input_data.append(line_cfg)

        # 2. Input Data from Query
        for g in self.wid_input_queries_container.children:
            line_cfg = {'type': 'query',
                        'set_id': g[0, 0].value,
                        'query': g[0, 5].value,
                        'num_samples': g[0, 25].value}
            input_data.append(line_cfg)

        config['input_data'] = input_data

    ###
    def load_config(self):
        try:
            with open(self.config_file, 'r') as fp:
                config = json.load(fp)
        except Exception as e:
            print("Could not load configuration!", e)
            return

        self.config = config
        self.wid_tester.value = config['tester']
        self.wid_test_session_id.value = config['test_session_id']
        self.wid_reports_root.value = config['reports_root']

        self.wid_source_system.value = config['source_system']
        self.wid_source_operating_environment.value = config['source_operating_environment']
        self.wid_source_operating_mode.value = config['source_operating_mode']

        self.wid_target_system.value = config['target_system']
        self.wid_target_operating_environment.value = config['target_operating_environment']
        self.wid_target_operating_mode.value = config['target_operating_mode']
        self.wid_rp_dump.value = config['rp_dump']
        self.wid_rp_project.value = config['rp_project']
        self.wid_rp_max_num_tests.value = config['rp_max_num_tests']
        self.wid_rp_dump_failures_only.value = config['rp_dump_failures_only']
        self.wid_rp_test_suite_name_header.value = config['rp_test_suite_name_header'] 

        self.wid_generate_status_matrix.value = config['generate_status_matrix']

        for wdb in self.wid_field.values():
            wdb.value = wdb.description in config['dosys_fields_selection']

        self.wid_gui.children = self.wid_gui.children[:2] + (
            self.test_input_file_config(), self.test_input_query_config()) + self.wid_gui.children[4:]

    ###
    def save_config(self):
        self.acquire_config()
        try:
            with open(self.config_file, 'w') as fp:
                json.dump(self.config, fp)
        except Exception as e:
            print("Could not save configuration!! ", e)

    ###
    def run_test(self):

        config = self.config

        # Initialization of test execution parameters
        source_system = config['source_system']
        source_operating_mode = self.operating_mode_map[config['source_operating_mode']]
        source_operating_environment = self.operating_environment_map[config['source_operating_environment']]
        target_system = config['target_system']
        target_operating_mode = self.operating_mode_map[config['target_operating_mode']]
        target_operating_environment = self.operating_environment_map[config['target_operating_environment']]
        dump_repository = config['dump_repository']
        field_list = config['dosys_fields_selection']
        rp_dump = config['rp_dump']
        rp_project = config['rp_project']
        rp_max_nb_tests = config['rp_max_num_tests']
        generate_status_matrix = config['generate_status_matrix']
        rp_dump_failures_only = config['rp_dump_failures_only'] 
        rp_test_suite_name_header = config['rp_test_suite_name_header'] 
        
        parity_batch_sz = config['parity_batch_size']
        log_individual_match_checks = config['log_individual_match_checks']
        empty_counted = config['empty_counted']
        display_type = config['display_type']
        dbg = config['dbg']
        output_format = config['output_format']
        if config['csv_repository'] is None:
            csv_repository = os.path.join(config['reports_root'], config['test_session_id'])
        else:
            csv_repository = os.path.join(config['csv_repository'])

        warnings.filterwarnings('ignore')

        # Data Providers initialization
        dp_sampler = das.DataProvider()
        dp_sampler.forward_exceptions(True)
        dp_sampler.set_operating_mode(source_operating_mode)
        dp_sampler.init_storage(dump_repository)
        try:
            dp_sampler.init_epoque(source_operating_environment)
        except:
            print("Cannot initiate Sampler!")

        dp_ref = das.DataProvider()
        dp_ref.forward_exceptions(True)
        dp_ref.set_operating_mode(source_operating_mode)
        dp_ref.init_storage(dump_repository)
        if source_system == "Epoque":  # only initialize if explicitly requested, to avoid error if system is down
            dp_ref.init_epoque(source_operating_environment)
        dp_ref.init_kimeapi(source_operating_environment)

        dp_target = das.DataProvider()
        dp_target.forward_exceptions(True)
        dp_target.set_operating_mode(target_operating_mode)
        dp_target.init_storage(dump_repository)
        dp_target.init_kimeapi(target_operating_environment)
        dp_target.init_ssl(target_operating_environment)

        # Results repository initialization
        reports_repository = os.path.join(config['reports_root'], config['test_session_id'])
        if not os.path.isdir(reports_repository):
            try:
                os.mkdir(reports_repository)
            except OSError:
                print("Warning: Failed to create reports directory", reports_repository)
            else:
                print("Successfully created reports directory", reports_repository)

        # Run test for each set
        dataset_cfg_list = config['input_data']

        self.dbg_dicts = {}
        for dataset_cfg in dataset_cfg_list:
            set_id = dataset_cfg['set_id']
            print("====================================================")
            print("Generating report for set:", set_id)

            if dataset_cfg['type'] == 'file':
                an_list = pd.read_csv(dataset_cfg['path'], sep=';')
            elif dataset_cfg['type'] == 'query':
                dr = das.DataRequest(service_type="Sampled_Query",
                                     input_data=das.InputData(
                                         query=dataset_cfg['query'],
                                         database='DOSYS',
                                         n_samples=dataset_cfg['num_samples'],
                                         randomize=False,
                                         fields=["AN"]),
                                     output_type="Text",
                                     identifier=dataset_cfg['set_id'])
                try:
                    an_list = dp_sampler.get_data(dp_sampler.epoque, dr, verbose=False)
                except Exception as e:
                    print("Could not generate samples", e)
                    continue
                print("Using a total of", len(an_list), "samples to test from Query:", dataset_cfg['query'])
            else:
                continue

            an_list = list(map(lambda x: UplTextMappers.get_unique_AN(x), list(an_list["AN"])))
                        
            # Need to adapt the AN format if the target system is SSL (EPAxxxxx -> EPxxxxxA)
            if target_system == 'SSL':
                an_list = [an[:2]+an[3:]+an[2] for an in an_list]

            self.dbg_dicts[set_id] = {}
            upl_parity_tester = UPLParityTester(an_list=an_list,
                                                field_list=field_list,
                                                das_data_provider_ref=dp_ref,
                                                das_data_provider_target=dp_target,
                                                output_repository=csv_repository,
                                                reference=source_system.upper(),
                                                target=target_system.upper(),
                                                output_format=output_format,
                                                output_prefix=set_id,
                                                parity_batch_sz=parity_batch_sz,
                                                empty_counted=empty_counted,
                                                display_type=display_type,
                                                set_id=set_id,
                                                log_individual_match_checks=log_individual_match_checks,
                                                
                                                dbg=dbg,
                                                rp_dump=rp_dump or generate_status_matrix, 
                                                rp_dump_failures_only=rp_dump_failures_only,
                                                rp_test_suite_name_header=rp_test_suite_name_header,
                                                dbg_dict=self.dbg_dicts[set_id])
            upl_parity_tester.configure()
            upl_parity_tester.exec()
            if rp_dump:
                upl_parity_tester.rp_dump_test_status(project=rp_project, max_nb_tests=rp_max_nb_tests)
                
            if generate_status_matrix:
                # 1
                test_status_matrix = upl_parity_tester.pcc.cmp_ds.dataset_incompleteness_test_status_matrices["PL"]
                print(len(test_status_matrix[test_status_matrix["incomplete_vs_PL"] == 1].index))
                test_status_matrix.to_excel(os.path.join(csv_repository, set_id + "_dataset_completeness_status_matrix.xls"))

                # 2
                test_status_matrix = upl_parity_tester.pcc.cmp_ds.incompleteness_test_status_matrices["PL"]
                col_names = [col_name for col_name in sorted(list(test_status_matrix.columns)) if not col_name.find("_values") > 0]
                print(col_names)
                print(len(col_names))
                print(len(test_status_matrix.index))
                test_status_matrix.to_excel(os.path.join(csv_repository, set_id + "_completeness_status_matrix.xls"))

                # 3
                test_status_matrix = upl_parity_tester.pcc.cmp_ds.inconsistency_test_status_matrices["PL"]
                col_names = [col_name for col_name in sorted(list(test_status_matrix.columns)) if not col_name.find("_values") > 0]
                print(col_names)
                print(len(col_names))
                print(len(test_status_matrix.index))
                test_status_matrix.to_excel(os.path.join(csv_repository, set_id + "_consistency_status_matrix_kime_docdb.xls"))

            print("====================================================")
        print("Reports generation completed")

    ###
    def perform_summary_report_generation(self):
        config = self.config

        print("Preparing summary report for dashboard")
        session_id = config['test_session_id']

        # Additional extrapolated parameters used for report generation
        # test session description

        # Create the report JSON container and fill the header part
        session_report = {
            'description': 'DOSYS vs PDM comparison session ' + config['test_session_id'],
            'tester': config['tester'],
            'date': datetime.now().strftime('%d-%m-%Y'),
            'reports_link': os.path.join(config['reports_root'], session_id),
            'data': {}
        }

        # Now iterate over each generated JSON report to fill the data part for each session
        dataset_cfg_list = config['input_data']

        for dataset_cfg in dataset_cfg_list:

            set_id = dataset_cfg['set_id']
            json_report_file = os.path.join(config['reports_root'], config['test_session_id'],
                                            set_id + "_prof_out.json")

            json_report = {}
            if os.path.isfile(json_report_file):
                with open(json_report_file, 'r') as f:
                    json_report = json.load(f)

            set_description = dataset_cfg['type']

            dataset_report = {
                'collection': set_id,
                'set_description': set_description,
                'report_link': '',  # set_id + "_sanity_test_report.html",
                'set_data': json_report
            }

            session_report['data'][set_id] = dataset_report

        # Finally store the whole test session report (json) in the report directory
        session_report_file = os.path.join(config['reports_root'], config['test_session_id'],
                                           session_id + "_summary_prof.json")

        with open(session_report_file, 'w') as json_file:
            json.dump(session_report, json_file)
        print("done...")
        print("====================================================")

    ###
    def perform_dashboard_generation(self):
        print("Generating dashboard from all detectable test sessions")

        config = self.config

        json_f = {}
        for root, dirs, files in os.walk(config['reports_root']):
            for d in dirs:
                print(d)
                json_report_file = os.path.join(root, d, d + '_summary_prof.json')
                if os.path.isfile(json_report_file):
                    print("Found report for session: ", d)
                    with open(json_report_file, 'r') as f:
                        json_report = json.load(f)
                        json_f[d] = json_report

        template = os.path.join("/home/jovyan/shared/Epyque", "test_lib", "upl_dashboard_template.html")

        # Read in the file
        with open(template, 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('@@@@@@', json.dumps(json_f, indent=4, sort_keys=True))

        # Write the file out again
        with open(os.path.join(config['reports_root'], 'dashboard.html'), 'w') as file:
            file.write(filedata)

        