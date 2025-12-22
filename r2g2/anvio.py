#!/usr/bin/env python
# -*- coding: utf-8

"""A script to convert anvi'o python scripts to Galaxy Tools."""
import argparse as argparse_original
import sys
import json
import os
from collections import OrderedDict
from xml.sax.saxutils import quoteattr
from jinja2 import Template
# import anvio

sys.path.append( os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir ) ) )#, 'anvi')))

PROVIDES_TO_TOOL_TYPE=OrderedDict(interactive='interactive')
DEFAULT_TOOL_TYPE = '' # 'default' #default is not allowed by planemo lint
#profile="19.01"
TOOL_TEMPLATE = """<tool id="{{id}}" name="{{name}}" version="{{version}}"{{tool_type}}{{profile}}>
{%- if description %}
    <description>{{ description }}</description>
{%- endif %}
{%- if macros %}
    <macros>
        <import>macros.xml</import>
    </macros>
    <expand macro="requirements" />
    <expand macro="stdio" />
{%- if version_command %}
    <expand macro="version_command" />
{%- endif %}
{%- else %}
    <requirements>
{%- for requirement in requirements %}
        {{ requirement }}
{%- endfor %}
{%- for container in containers %}
        {{ container }}
{%- endfor %}
    </requirements>
{%- if realtime %}
    <entry_points>
{%- for ep in realtime %}
        <entry_point name="{{ ep['name'] }}" requires_domain="true">
            <port>{{ ep.get('port', DEFAULT_INTERACTIVE_PORT) }}</port>
            {%- if 'url' in ep and ep['url']%}
            <url><![CDATA[{{ ep['url'] }}]]></url>
            {%- endif %}
        </entry_point>
{%- endfor %}
    </entry_points>
{%- endif %}
    <stdio>
        <exit_code range="1:" />
    </stdio>
{%- if version_command %}
    <version_command>{{ version_command }}</version_command>
{%- endif %}
{%- endif %}
    <command><![CDATA[
{%- if command %}
        {{ command }}
{%- else %}
        TODO: Fill in command template.
{%- endif %}
    ]]></command>
    <inputs>
{%- for input in inputs %}
        {{ input }}
{%- endfor %}
    </inputs>
    <outputs>
{%- for output in outputs %}
        {{ output | safe }}
{%- endfor %}
    </outputs>
{%- if tests %}
    <tests>
{%- for test in tests %}
        <test>
{%- for param in test.params %}
            <param name="{{ param[0]}}" value="{{ param[1] }}"/>
{%- endfor %}
{%- for output in test.outputs %}
            <output name="{{ output[0] }}" file="{{ output[1] }}"/>
{%- endfor %}
        </test>
{%- endfor %}
    </tests>
{%- endif %}
    <help><![CDATA[
{%- if help %}
{{ help }}
{%- else %}
        TODO: Fill in help.
{%- endif %}
    ]]></help>
{%- if macros %}
    <expand macro="citations" />
{%- else %}
{%- if doi or bibtex_citations %}
    <citations>
{%- for single_doi in doi %}
        <citation type="doi">{{ single_doi }}</citation>
{%- endfor %}
{%- for bibtex_citation in bibtex_citations %}
        <citation type="bibtex">{{ bibtex_citation }}</citation>
{%- endfor %}
    </citations>
{%- endif %}
{%- endif %}
</tool>
"""

MACROS_TEMPLATE = """<macros>
    <xml name="requirements">
        <requirements>
{%- for requirement in requirements %}
        {{ requirement }}
{%- endfor %}
            <yield/>
{%- for container in containers %}
        {{ container }}
{%- endfor %}
        </requirements>
    </xml>
    <xml name="stdio">
        <stdio>
            <exit_code range="1:" />
        </stdio>
    </xml>
    <xml name="citations">
        <citations>
{%- for single_doi in doi %}
            <citation type="doi">{{ single_doi }}</citation>
{%- endfor %}
{%- for bibtex_citation in bibtex_citations %}
            <citation type="bibtex">{{ bibtex_citation }}</citation>
{%- endfor %}
            <yield />
        </citations>
    </xml>
{%- if version_command %}
    <xml name="version_command">
        <version_command>{{ version_command }}</version_command>
    </xml>
{%- endif %}
</macros>
"""

galaxy_tool_citation ='''@ARTICLE{Blankenberg21-anvio,
   author = {Daniel Blankenberg Lab, et al},
   title = {In preparation..},
   }'''


SHED_YML ="""name: anvio
owner: blankenberglab
description: "Anvi’o: an advanced analysis and visualization platform for ‘omics data"
homepage_url: https://github.com/merenlab/anvio
long_description: |
    Anvi’o is an analysis and visualization platform for ‘omics data. 
    It brings together many aspects of today’s cutting-edge genomic, metagenomic, and metatranscriptomic analysis practices to address a wide array of needs.
remote_repository_url: https://github.com/blankenberglab/tool-generator-anvio
type: unrestricted
categories:
- Metagenomics
auto_tool_repositories:
  name_template: "{{ tool_id }}"
  description_template: "Wrapper for the Anvi'o tool suite: {{ tool_name }}"
suite:
  name: "suite_anvio"
  description: "Anvi’o: an advanced analysis and visualization platform for ‘omics data"
  long_description: |
    Anvi’o is an analysis and visualization platform for ‘omics data. 
    It brings together many aspects of today’s cutting-edge genomic, metagenomic, and metatranscriptomic analysis practices to address a wide array of needs.
"""

class Parameter( object ):
    _output_startswith = ('output', 'export')
    _default_default = ''
    def __init__( self, name, arg_short, arg_long, info_dict ):
        self._name = name
        self.name = name.replace( "-", '_' )
        self.arg_short = arg_short
        self.arg_long = arg_long
        self.info_dict = info_dict
        self.required = info_dict.get( 'required', False )
        self.is_output = name.lower().startswith( self._output_startswith )
        self.is_input = not self.is_output

    def copy(self, name=None, arg_short=None, arg_long=None, info_dict = None):
        orig_dict = self.info_dict.copy()
        if info_dict:
            orig_dict.update( info_dict )
        return self.__class__( name or self.name, arg_short or self.arg_short, arg_long or self.arg_long, orig_dict )
    def get_name( self ):
        return quoteattr( self.name )
    def get_output_cmd_name(self):
        return self.name
    def get_input_cmd_name(self):
        return self.name
    def get_type( self ):
        return 'text'
    def get_label( self ):
        return quoteattr( self.name.replace( '_', " " ).title() )
    def get_default( self ):
        default = self.info_dict.get( 'default', None )
        if default is None:
            default = self._default_default
        return quoteattr( str( default ) )
    def get_argument( self ):
        return quoteattr( self.arg_long )
    def is_positional_arg( self ):
        return not ( self.arg_short or self.arg_long )
    def get_arg_text( self ):
        arg = self.arg_long or self.arg_short or ''
        return arg
    def get_help( self, extra=None ):
        help = self.info_dict.get('help', '')
        try:
            help = help.format(**self.info_dict)
        except KeyError as e:
            print('FIXME: formatting help failed')
            # print(e)
        if extra:
            help = "%s %s" % (help, extra)
        help = help.replace( '\n', ' ' ).replace( '\r', ' ' ).replace( '\t', ' ' ).strip()
        while '  ' in help:
            help = help.replace( '  ', ' ' )
        return quoteattr( help )
    def get_optional( self ):
        if self.info_dict.get( 'required', False ):
            return 'False'
        return 'True'
    def to_xml_param( self ):
        choices = self.info_dict.get('choices')
        if choices and isinstance(choices, (list, tuple)) and len(choices) > 0:
            default_raw = self.info_dict.get('default')
            # Build <option> tags
            option_lines = []
            for ch in choices:
                ch_str = str(ch)
                selected_attr = ''
                if default_raw is not None and str(default_raw) == ch_str:
                    selected_attr = ' selected="true"'
                option_lines.append(
                    "            <option value=%s%s>%s</option>" % (
                        quoteattr(ch_str), selected_attr, ch_str
                    )
                )
            options_block = "\n".join(option_lines)
            return (
                "<param name=%s type=\"select\" label=%s optional=\"%s\" argument=%s help=%s>\n" % (
                    quoteattr(self.get_input_cmd_name()),
                    self.get_label(),
                    self.get_optional(),
                    self.get_argument(),
                    self.get_help(),
                )
                + options_block + "\n        </param>"
            )
        # Fallback: original single-value parameter

        if self.is_input:

            return """<param name=%s type="%s" label=%s value=%s optional="%s" argument=%s help=%s/>""" % (
                quoteattr( self.get_input_cmd_name() ), 
                self.get_type(),  
                self.get_label(), 
                self.get_default(), 
                self.get_optional(),
                self.get_argument(), 
                self.get_help(),
            )
        else:
            try:
                format = self.get_format().split(',')[0]
            except Exception as e:
                format = ' '
                print("Error occurred while getting format:", e, "Please set appropriate format in the tool xml for", f'"{self.name}"', "output data")

            try:
                format_source = self.get_format_source()
            except Exception as e:
                format_source = ' '
                print("Error occurred while getting format source:", e) 

            try:
                metadata_source = self.get_metadata_source()
            except Exception as e:
                metadata_source = ' '
                print("Error occurred while getting metadata source:", e)

            try:
                label = self.get_output_label()
            except Exception as e:
                label = ' '
                print("Error occurred while getting output label:", e, "Please set appropriate label in the tool xml for", self.name, "output data")

            return """<data name=%s format="%s" %s %s label=%s/>""" % \
            (
                quoteattr(self.get_output_cmd_name() ), 
                format,
                format_source,
                metadata_source,
                label,
            )

    
    def to_xml_output( self ):
    
        return self 
     
    def get_pre_cmd_line( self ):
        return ''
    def get_post_cmd_line( self ):
        return ''
    def to_cmd_line( self ):
        text = ''
        cmd_txt =  "%s '${%s}'" % ( self.get_arg_text(), self.get_input_cmd_name() )
        if not self.required:
            text = """
#if $str( $%s ):
    %s
#end if\n""" % ( self.get_input_cmd_name(), cmd_txt )
        else:
            text = "%s\n" % cmd_txt
        return text
    def __str__( self ):
        return "%s\n%s\n" % ( self.to_xml_param(), self.to_cmd_line() )


class ParameterDiscard( Parameter ):
    def get_type(self):
        return "string"
    def to_xml_param( self ):
        return ''
    def to_cmd_line( self ):
        return ''

class ParameterBooleanAlwaysTrue( Parameter ):
    def get_type(self):
        return "boolean"
    def to_xml_param( self ):
        return ''
    def to_cmd_line( self ):
        return self.arg_long

class ParameterAlwaysDefault( Parameter ):
    def get_type(self):
        return "text"
    def to_xml_param( self ):
        return ''
    def to_cmd_line( self ):
        return "%s '%s'" % (self.arg_long, self.get_default())

class ParameterAlwaysValue( Parameter ):
    value = None
    def get_type(self):
        return "text"
    def to_xml_param( self ):
        return ''
    def to_cmd_line( self ):
        return "%s '%s'" % (self.arg_long, self.value)


class ParameterBoolean( Parameter ):
    _default_default = 'False'
    def get_type(self):
        return "boolean"
    def to_xml_param( self ):
        return """<param name=%s type="%s" label=%s truevalue="%s" falsevalue="" checked=%s optional="%s" argument=%s help=%s/>""" % \
            (
                self.get_name(), 
                self.get_type(),  
                self.get_label(),
                self.arg_long,
                self.get_default(), 
                self.get_optional(),
                self.get_argument(), 
                self.get_help(),

            )
    def to_cmd_line( self ):
        return "${%s}\n" % ( self.name )


class ParameterINT( Parameter ):
    def get_type(self):
        return "integer"

class ParameterFLOAT( Parameter ):
    def get_type(self):
        return "float"

class ParameterNUM_CPUS( ParameterINT ):
    def to_xml_param( self ):
        return ''
    def to_cmd_line( self):
        return '%s "\\${GALAXY_SLOTS:-1}"\n' % ( self.get_arg_text() )


DEFAULT_PARAMETER = Parameter

PARAMETER_BY_METAVAR = {

    'INT': ParameterINT,
    'INTEGER': ParameterINT,
    'FLOAT': ParameterFLOAT,
    'LEEWAY_NTs': ParameterINT,
    'WRAP': ParameterINT,
    'NUM_SAMPLES': ParameterINT,
    'PERCENT_IDENTITY': ParameterFLOAT,
    'GENE_CALLER_ID': ParameterINT,
    'E-VALUE': ParameterFLOAT,
    'NUM_POSITIONS': ParameterINT,
    'NUM_CPUS': ParameterNUM_CPUS,
    'RATIO': ParameterFLOAT,
    'NUM_THREADS': ParameterNUM_CPUS,
    'IP_ADDR': ParameterDiscard,
}

PARAMETER_BY_NAME = {
    'just-do-it': ParameterBooleanAlwaysTrue,
    'temporary-dir-path': ParameterDiscard,
    'browser-path': ParameterDiscard,
    'server-only': ParameterBooleanAlwaysTrue,
    'password-protected': ParameterDiscard,
    'user-server-shutdown': ParameterBooleanAlwaysTrue,
    'dry-run': ParameterDiscard,
    'export-svg': ParameterDiscard,
}

#FIXME. make skip just reuse ParameterDiscard
SKIP_PARAMETER_NAMES = ['help', 'temporary-dir-path', 'modeller-executable', 'program', 'log-file', 'gzip-output']
SKIP_PARAMETER_NAMES = list(map( lambda x: x.replace( "-", '_' ), SKIP_PARAMETER_NAMES ))

'''
<param name="ip_address" type="text" label="Ip Address" value="0.0.0.0" optional="True" argument="--ip-address" help="IP address for the HTTP server. The default ip address (%(default)s) should work just fine for most."/>
        <param name="port_number" type="integer" label="Port Number" value="" optional="True" argument="--port-number" help="Port number to use for anvi'o services. If nothing is declared, anvi'o will try to find a suitable port number, starting from the default port number, 8080."/>
        <param name="browser_path" type="data" label="Browser Path" format="txt" optional="True" multiple="False" argument="--browser-path" help="By default, anvi'o will use your default browser to launch the interactive interface. If you would like to use something else than your system default, you can provide a full path for an alternative browser using this parameter, and hope for the best. For instance we are using this parameter to call Google's experimental browser, Canary, which performs better with demanding visualizations."/>
        <param name="read_only" type="boolean" label="Read Only" truevalue="--read-only" falsevalue="" checked="False" optional="True" argument="--read-only" help="When the interactive interface is started with this flag, all 'database write' operations will be disabled."/>
        <param name="server_only" type="boolean" label="Server Only" truevalue="--server-only" falsevalue="" checked="False" optional="True" argument="--server-only" help="The default behavior is to start the local server, and fire up a browser that connects to the server. If you have other plans, and want to start the server without calling the browser, this is the flag you need."/>
        <param name="password_protected" type="boolean" label="Password Protected" truevalue="--password-protected" falsevalue="" checked="False" optional="True" argument="--password-protected" help="If this flag is set, command line tool will ask you to enter a password and interactive interface will be only accessible after entering same password. This option is recommended for shared machines like clusters or shared networks where computers are not isolated."/>

'''

def get_parameter( param_name, arg_short, arg_long, info_dict ):

  
    if param_name in PARAMETER_BY_NAME:
        param = PARAMETER_BY_NAME[param_name]
    elif 'action' in info_dict and info_dict['action'] not in [ 'help', 'store' ]:

        if info_dict['action'] == 'store_true':
            param = ParameterBoolean
        else:
            param = ParameterBoolean
    else:
        # Prefer explicit Python argparse 'type' when available (e.g., int/float)
        ptype = info_dict.get('type')
        param = None
        if ptype is not None:
            # Handle both callable types (int/float) and string descriptors
            try:
                # Some callables may not be directly comparable; stringify as fallback
                if ptype is int or (isinstance(ptype, str) and ptype.lower() in ('int', 'integer')):
                    param = ParameterINT
               
                elif ptype is float or (isinstance(ptype, str) and ptype.lower() in ('float', 'double', 'numeric')):
                    param = ParameterFLOAT
            except Exception:
                # Fallback to string-based checks
                if isinstance(ptype, str):
                    low = ptype.lower()
                    if low in ('int', 'integer'):
                        param = ParameterINT
                    elif low in ('float', 'double', 'numeric'):
                        param = ParameterFLOAT

        # If 'type' didn't resolve it, try metavar-based mapping
        if param is None:
            metavar = info_dict.get( 'metavar' )
            # print("metavar is dan: %s, %s, %s" % ( param_name, metavar, info_dict ) )
            if metavar is None:
                pass
            elif metavar not in PARAMETER_BY_METAVAR:
                pass
            param = PARAMETER_BY_METAVAR.get( metavar, DEFAULT_PARAMETER )


    return param( param_name, arg_short, arg_long, info_dict )

class FakeArg( argparse_original.ArgumentParser ):
    def __init__( self, *args, **kwd ):
        self._oynaxraoret_args = []
        super( FakeArg, self ).__init__( *args, **kwd )

    def add_argument( self, *args, **kwd ):
        self._oynaxraoret_args.append( ( args, kwd ) )
        super( FakeArg, self ).add_argument( *args, **kwd )

    def oynaxraoret_params_by_name( self, params ):
        rval = {}#odict()
        for args in self._oynaxraoret_args:
            name = ''
            for arg in args[0]:
                if arg.startswith( '--' ):
                    name = arg[2:]
                elif arg.startswith( '-'):
                    if not name:
                        name = arg[1]
                else:
                    name = arg
            rval[name] = args[1]
            if 'metavar' not in args[1]:
                pass
                # print('no metavar', name)
        return rval
    def oynaxraoret_get_params( self, params ):
        rval = []
        for args in self._oynaxraoret_args:
      
            name = ''
            arg_short = ''
            arg_long = ''
            for arg in args[0]:
                if arg.startswith( '--' ):
                    name = arg[2:]
                    arg_long = arg
                elif arg.startswith( '-' ):
                    arg_short = arg
                    if not name:
                        name = arg[1:]
                elif not name:
                    name = arg
            param = None
            if name in params:
                # print("%s (name) is in params" % (name) )
                param = params[name]
    
            #if 'metavar' in args[1]:
                #if args[1]['metavar'] in params:
            #        param = params[args[1]['metavar']]
            if param is None:
                if name in PARAMETER_BY_NAME:
                    param = PARAMETER_BY_NAME[name]( name, arg_short, arg_long, args[1] )
            if param is None:
                # print("Param is None")
                metavar = args[1].get( 'metavar', None )
                # print("asdf metavar",args[1],metavar)
                if metavar and metavar in PARAMETER_BY_METAVAR:
                    param = PARAMETER_BY_METAVAR[metavar]( name, arg_short, arg_long, args[1] )
            if param is None:
                # print('no meta_var, using default', name, args[1])
                #param = DEFAULT_PARAMETER( name, arg_short, arg_long, args[1] )
                param = get_parameter( name, arg_short, arg_long, args[1] )
               
            #print 'before copy', param.name, type(param)
            param = param.copy( name=name, arg_short=arg_short, arg_long=arg_long, info_dict=args[1] )
            #print 'after copy', type(param)
            rval.append(param)
        
        return rval
    
    def oynaxraoret_to_cmd_line( self, params, filename=None ):
        pre_cmd = []
        post_cmd = []
        rval = filename or self.prog
        for param in self.oynaxraoret_get_params( params ):
            if param.name not in SKIP_PARAMETER_NAMES:
                pre = param.get_pre_cmd_line()
                if pre:
                    pre_cmd.append( pre )
                post = param.get_post_cmd_line()
                if post:
                    post_cmd.append( post )
                cmd = param.to_cmd_line()
                if cmd:
                    rval = "%s\n%s" % ( rval, cmd )
        pre_cmd = "\n && \n".join( pre_cmd )
        post_cmd = "\n && \n".join( post_cmd )
        if pre_cmd:
            rval = "%s\n &&\n %s" % ( pre_cmd, rval )
        rval = "%s\n&> '${GALAXY_ANVIO_LOG}'\n" % (rval)
        if post_cmd:
            rval = "%s\n &&\n %s" % ( rval, post_cmd )
        return rval #+ "\n && \nls -lahR" #Debug with showing directory listing in stdout
    
    def oynaxraoret_to_inputs( self, params ):
        rval = []
        for param in self.oynaxraoret_get_params( params ):
            if param.name not in SKIP_PARAMETER_NAMES and param.is_input:
                inp_xml = param.to_xml_param()
                if inp_xml:
                    rval.append( inp_xml )
        return rval
    
    def oynaxraoret_to_outputs( self, params ):
        rval = []
    
        for param in self.oynaxraoret_get_params( params ):
     
            if param.name not in SKIP_PARAMETER_NAMES and param.is_output:
                rval.append( param.to_xml_output() )
        return rval

def format_help(help_text):
    # Just cheat and make it a huge block quote
    rval = "::\n"
    for line in help_text.split('\n'):
        rval = "%s\n  %s" % (rval, line.rstrip())
    return "%s\n\n" % (rval)

def build_tool00000(plink_text_version):
    tool_type = 'default'
    description = ''
    
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    asset_path = os.path.join(script_path, 'assets')
    versioned_asset_path = os.path.join(asset_path, 'versions', plink_text_version)

    with open(os.path.join(versioned_asset_path, 'info.json')) as fh:
        info = json.load(fh)
    tool_id = info.get('tool_id')
    plink_cmd = info.get('plink_cmd')
    tool_name = info.get('tool_name')
    plink_help_input_start = info.get('plink_help_input_start')
    plink_help_input_stop = info.get('plink_help_input_stop')

    with open(os.path.join(versioned_asset_path, 'help.txt')) as fh:
        plink_help = fh.read()

    # Copy&Pasted From https://www.cog-genomics.org/plink/1.9/output
    with open(os.path.join(versioned_asset_path, 'outputs.txt')) as fh:
        PLINK_OUTPUTS_TXT = fh.read()

    with open(os.path.join(asset_path, 'tool_template.txt')) as fh:
        TOOL_TEMPLATE = fh.read()
