
# from Jumpscale.core.JSBase import JSBase
import os
import sys
from Jumpscale import j

{% for syspath in md.syspaths %}
if "{{syspath}}" not in sys.path:
    sys.path.append("{{syspath}}")
{%- endfor %}

class JSGroup():
    pass


{% for name, jsgroup in md.jsgroups.items() %}
class group_{{jsgroup.name}}(JSGroup):
    def __init__(self):
        {% for module in jsgroup.jsmodules %}
        self._{{module.jname}} = None
        {%- endfor %}

    {% for module in jsgroup.jsmodules %}
    @property
    def {{module.jname}}(self):
        if self._{{module.jname}} is None:
            # print("LOAD:{{module.name}}")
            from {{module.importlocation}} import {{module.name}}
            # try:
            #     from {{module.importlocation}} import {{module.name}}
            # except Exception as e:
            #     msg = j.core.application.error_init("import", "{{module.importlocation}}", e)
            #     raise e
            # # print("RUN:{{module.name}}")

            self._{{module.jname}} =  {{module.name}}()

            # try:
            #     self._{{module.jname}} =  {{module.name}}()
            # except Exception as e:
            #     msg = j.core.application.error_init("execute","{{module.importlocation}}",e)
            #     return None
            # print("OK")
        return self._{{module.jname}}
    {%- endfor %}

{{jsgroup.jdir}} = group_{{jsgroup.name}}()
j.core._groups["{{name}}"] = {{jsgroup.jdir}}

{% endfor %}


