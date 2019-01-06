
class Item():

    def __init__(self,name,children=[]):
        """
        name needs to be given snake case e.g. door_step
        :param name:
        """

        self.name = name
        self.name_lower = self.name.lower()

        out=""
        for item in name.split("_"):
            if item.strip()!="":
                out+=name[0].upper()+name[1:].lower()
        self.name_camel = out

        self.children = []
        for childname in children:
            self.children.append(Item(childname))

