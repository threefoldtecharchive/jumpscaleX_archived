from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.schema.test(name="load_data")'

    test loading of data from toml source

    """

    toml = """
        enable = true
        #unique name with dot notation for the package
        name = "digitalme.base"
        
        
        [[loaders]]
        giturl = "https://github.com/threefoldtech/digital_me/tree/development960/packages/system/base"
        dest = ""
        
        [[loaders]]
        giturl = "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/static"
        dest = "blueprints/base/static"

        """

    schema_package = """
        @url =  jumpscale.digitalme.package
        name = "UNKNOWN" (S)           #official name of the package, there can be no overlap (can be dot notation)
        enable = true (B)
        args = (LO) !jumpscale.digitalme.package.arg
        loaders= (LO) !jumpscale.digitalme.package.loader
        
        @url =  jumpscale.digitalme.package.arg
        key = "" (S)
        val =  "" (S)
        
        @url =  jumpscale.digitalme.package.loader
        giturl =  "" (S)
        dest =  "" (S)
        enable = true (B)
        
        ##ENDSCHEMA

        """

    data = j.data.serializers.toml.loads(toml)

    schema_object = j.data.schema.get(schema_package)
    data = schema_object.get(data=data)

    assert(
        j.core.text.strip_to_ascii_dense(str(data)) ==
        "_args_enable_true_loaders_dest_enable_true_giturl_https_github.com_threefoldtech_digital_me_tree_development960_packages_system_base_dest_blueprints_base_static_enable_true_giturl_https_github.com_threefoldtech_jumpscale_weblibs_tree_master_static_name_digitalme.base")

    self._logger.info("TEST DONE LOADDATA")

    return ("OK")
