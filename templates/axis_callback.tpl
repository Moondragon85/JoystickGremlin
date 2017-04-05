<%page args="input_item, decorator_name, mode_index, parameter_list, device_name, code_block"/>
<%namespace name="util" module="templates.functions"/>
@${decorator_name}.axis(${input_item.input_id}, always_execute=${input_item.always_execute})
def ${device_name}_${mode_index}_axis_${input_item.input_id}(${parameter_list}):
    """${input_item.description}"""
    value = event.value
    ${util.indent(code_block.body, 4)}