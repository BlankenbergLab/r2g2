import argparse
import subprocess
import tempfile
import os, sys
import shutil
from r2g2.core import TOOL_TEMPLATE
from r2g2.dependency_generator import  return_galax_tag, detect_package_channel
import xml.etree.ElementTree as ET
from xml.dom import minidom
import time 

#TBD: temparily anvio import, in the future will be replace by the independant anvio package 
from r2g2.anvio import format_help, galaxy_tool_citation
from jinja2 import Template

from r2g2.parsers.r_parser import (
    edit_r_script,
    json_to_python,
    return_dependencies,
    json_to_python_for_param_info,
    extract_simple_parser_info,
    #TBD: R's logical type need be handled correctly while building galaxy input params. 
    logical, 
    pretty_xml, 
    output_param_generator_from_argparse
)

def generate_galaxy_xml(xml_str):
    
    xml_str = ET.tostring(xml_str, encoding="unicode")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")

def main(r_script, out_dir, profile, dep_info, description, tool_version, citation_doi, user_define_output_param=False, user_define_input_param=None):

    if not citation_doi:
        citation_doi = ''

    if not description:
        description = r_script.split('/')[len(r_script.split('/'))-1].split('.')[0] + " tool"

    dependency_tag = "\n".join([return_galax_tag(*detect_package_channel(i), False) for i in return_dependencies(r_script)])

    current_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp(dir=current_dir)

    try:
        if not out_dir:
            out_dir_path = os.path.join("../", "out")
        else:
            out_dir_path = out_dir

        if not os.path.exists(out_dir_path):
            os.makedirs(out_dir_path)
            
        edited_r_script  = os.path.join(temp_dir, "%s_edited.r"%(r_script.split('/')[len(r_script.split('/'))-1].split('.')[0])) 
        
        print("####################################################################")
        print("R script with argument parsing edited and processed successfully...")
        print("####################################################################")

        json_out  = os.path.join(temp_dir, "%s.json"%(r_script.split('/')[len(r_script.split('/'))-1].split('.')[0]))  

        print("####################################################################")
        print("Extracted arguments have been written to a JSON file successfully...")  
        print("####################################################################")
    
        edit_r_script(r_script, edited_r_script, json_file_name=json_out )

        subprocess.run(['Rscript',  edited_r_script])

        data_params_list = None
        if user_define_input_param:
            if ':' in user_define_input_param:
                data_params_list = {}
                for block in user_define_input_param.split(';'):
                    if not block.strip(): continue
                    props = {}
                    for item in block.split(','):
                        if ':' in item:
                            k, v = item.split(':', 1)
                            props[k.strip()] = v.strip()
                    if 'name' in props:
                        name = props.pop('name')
                        data_params_list[name] = props
            else:
                data_params_list = [p.strip() for p in user_define_input_param.split(',')]

        output_args_list = []
        if user_define_output_param:
            print("User defined output parameters detected...")
            output_params, output_command, output_args_list = output_param_generator_from_argparse(user_define_output_param)
            output_params, output_command = "\n".join(output_params), "\t\t\t\t\t".join(output_command)
        
        else:
            # output_params  = "\n".join(list(set([i.to_xml_param() for i in  blankenberg_parameters.oynaxraoret_to_outputs(params)])))
            # output_command  = "\t\t\t\t\t".join(list(set([i.to_cmd_line() for i in  blankenberg_parameters.oynaxraoret_to_outputs(params)])))
            pass

        python_code_as_string = json_to_python(json_out, data_params=data_params_list, ignore_params=output_args_list)
        param_info_dict = {}
        argument_string = json_to_python_for_param_info(json_out)
        argument_string.replace('logical', 'boolean')

        exec(argument_string, globals(), param_info_dict)

        param_info = param_info_dict.get('param_info')

        print("####################################################################")
        print("Converted R arguments to Python argparse successfully...")
        print("####################################################################")

        input = python_code_as_string
        params = {}
        __provides__ = [] # Reset provides since it is not always declared
        local_dict={}
        global_dict={}
        local_dict = {}

        exec(input, globals(), local_dict)

        combined_xml = []
        combined_command = []

        blankenberg_parameters = local_dict.get('blankenberg_parameters')
        blankenberg_parameters.param_cat = extract_simple_parser_info(param_info)

        flat_param, flat_command = blankenberg_parameters.flat_param_groups(blankenberg_parameters.param_cat )

        if not blankenberg_parameters.param_cat['subparsers']:
            cond_section_param, cond_param_command = None, None
        else:
            cond_section_param, cond_param_command =  blankenberg_parameters.dict_to_xml_and_command(   blankenberg_parameters.param_cat )

        mut_input_param, mut_command = blankenberg_parameters.mutual_conditional(blankenberg_parameters.param_cat )
    
        output_args_list = []
        if user_define_output_param:
            print("User defined output parameters detected...")
            output_params, output_command, output_args_list = output_param_generator_from_argparse(user_define_output_param)
            output_params, output_command = "\n".join(output_params), "\t\t\t\t\t".join(output_command)
        
        else:
            output_params  = "\n".join(list(set([i.to_xml_param() for i in  blankenberg_parameters.oynaxraoret_to_outputs(params)])))
            output_command  = "\t\t\t\t\t".join(list(set([i.to_cmd_line() for i in  blankenberg_parameters.oynaxraoret_to_outputs(params)])))
            # pass

        if flat_command :
            combined_command.append(flat_command )
        
        if flat_param:
            combined_xml.append(flat_param)

        if output_command :
            combined_command.append(output_command )

        if cond_param_command:
            combined_xml.append("\n".join(pretty_xml(cond_section_param ).split("\n")[1:]))

        if mut_input_param:
            combined_xml.append(mut_input_param)

        if cond_param_command:
            combined_command.append(cond_param_command)   

        if  mut_command:
            combined_command.append( mut_command)

        print("####################################################################")
        print("Tool parameters have been extracted successfully...")
        print("####################################################################")

        DEFAULT_TOOL_TYPE = "test_tools"
        tool_type = DEFAULT_TOOL_TYPE
        filename = r_script.split('/')[len(r_script.split('/'))-1]
        cleaned_filename = filename.lower().replace( '-', '_').replace('.r', '')

        try:
            formated_string = format_help(blankenberg_parameters.format_help().replace(os.path.basename(__file__), filename))
        except Exception as e:
            print(f"Error formatting help: {e}")    
            formated_string = " No help available."

        template_dict = {
            'id': cleaned_filename ,
            'tool_type': tool_type,
            'profile': profile,
            'name': cleaned_filename,   
            'version': tool_version,
            'description': description,
            #'macros': None,
            'version_command': '%s --version' % filename,
            'requirements': dependency_tag,
            'command':"\n".join(combined_command), 
            'inputs': ["\n".join(combined_xml)],
            'outputs': [output_params],
            #'tests': None,
            'help': formated_string,
            'doi': citation_doi.split(','),
            'bibtex_citations': galaxy_tool_citation,
            'bibtex_citations': '',
            'file_name':filename
            }

        tool_xml = Template(TOOL_TEMPLATE).render( **template_dict )

        print("xml wrapper generated", os.path.join (out_dir_path, "%s.xml" % cleaned_filename ))

        with open( os.path.join (out_dir_path, "%s.xml" % cleaned_filename ), 'w') as out:
            out.write(tool_xml)

    finally:
        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        else:
            print(f"Directory does not exist: {temp_dir}")


def run_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--r_script_name', required=False, default=None, help="Provide the path of an R script... ")
    parser.add_argument('-f', '--r_scripts', required=False, default=None, help="A path of a text file containing full path of R scripts.")
    parser.add_argument('-o', '--output_dir', required=False, default=None)
    parser.add_argument('-p', '--profile', required=False, default="22.01")
    parser.add_argument('-d', '--description', required=False, default=None, help="tool based on R script")
    parser.add_argument('-s', '--dependencies', required=False,  default=False, help=" Extract dependency information..")
    parser.add_argument('-v', '--tool_version', required=False,  default='0.0.1', help="Galaxy tool version..")
    parser.add_argument('-c', '--citation_doi', required=False,  default=None, help="Comma separated Citation DOI.")
    parser.add_argument('-u', '--user_define_output_param', required=False, default=False, help="Rather guessing output params, user can define output params in specific format. Ex. 'name:protein,format:pdb,label:protein file,from_work_directory;name:ligand,format:pdb,label:ligand file,from_work_directory'")
    parser.add_argument('-i', '--user_define_input_param', required=False, default=None, help="List of input parameters to be treated as data inputs, comma separated. Ex. 'input_file,reference_data'")

    args = parser.parse_args()

    if not args.r_scripts and not args.r_script_name:
        print("\n\nPlease provide either a single Rscript or a text file containing paths to R scripts. See the details below...\n\n")
        parser.print_help() 
        sys.exit(1)
        
    if args.r_scripts:
        file = open(args.r_scripts)
        r_scrtips_list  = [i.strip("\n") for i in file.readlines()]
    else:
        r_scrtips_list = [args.r_script_name]

    total_files = len(r_scrtips_list)

    start_time = time.time()  # total processing start

    for idx, r_spt in enumerate(r_scrtips_list, start=1):
        file_start = time.time()
        print(f"[{idx}/{total_files}] Processing: {r_spt} ...")

        # try:
        main(r_spt, args.output_dir, args.profile, args.dependencies, args.description, args.tool_version, args.citation_doi, args.user_define_output_param, args.user_define_input_param)
        status = "Success"
        # except Exception as e:
        #     status = f"Failed ({e})"

        file_end = time.time()
        elapsed = file_end - file_start
        print(f"[{idx}/{total_files}] Finished: {r_spt} | Status: {status} | Time taken: {elapsed:.2f}s\n")

    total_elapsed = time.time() - start_time
    print(f"All files processed. Total time: {total_elapsed:.2f}s")

if __name__ == "__main__":
    run_main()