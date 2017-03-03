#! /bin/bash
cd {{ wd }}
git clone {{ sourceapp.git_url }}
cd {{ sourceapp.sub_dir }}
{{ sourceapp.compile_tool.bin_name }}  {{ sourceapp.compile_tool.opts }}
cd {{ sourceapp.compile_tool.target_path }}
{{ sourceapp.engine_type.bin_name }} -cp *.jar {{ sourceapp.engine_opts }} {{ sourceapp.main_func }} {{ sourceapp.main_func_opts }}