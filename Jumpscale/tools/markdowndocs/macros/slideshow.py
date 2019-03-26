from Jumpscale import j
from Jumpscale.tools.googleslides.slides2html.google_links_utils import get_presentation_id
import collections

EXPORT_TMP_DIR = "/tmp"
CRED_FILE_PATH = "/sandbox/var/cred.json"


def slideshow(doc, **kwargs):
    presentation = Presentations()

    for key in kwargs:
        if key.startswith("presentation"):
            presentation_num = int(key.split("_")[1].strip())
            if ("width" and "height")in kwargs:
                slides, presntation_dest = render(
                    doc, kwargs[key],
                    width=int(kwargs["width"]),
                    height=int(kwargs["height"]))
                presentation.presenation_add(slides, presntation_dest, presentation_num)

            else:
                slides, presntation_dest = render(doc, kwargs[key])
                presentation.presenation_add(slides, presntation_dest, presentation_num)

        elif key.casefold().startswith("slide"):
            footer = ""

            if j.data.types.list.check(kwargs[key]) and len(kwargs[key]) > 1:
                footer = kwargs[key][1]
                presentation_args = kwargs[key][0]

            slide_num = key.split("_")[1].strip()
            presentation_num = presentation_args.split("_")[1].strip().split("[")[0].strip()
            slide_num_of_presentation = presentation_args.split(
                "_")[1].strip().split("[")[1].strip().split("]")[0].strip()

            if "id" in slide_num_of_presentation:
                slide, dest = get_slide_from_presntation(presentation, int(presentation_num), slide_num_of_presentation)
            else:
                slide, dest = get_slide_from_presntation(presentation, int(presentation_num),
                                                         int(slide_num_of_presentation))

            presentation.slide_add(slide, footer, dest, int(slide_num))

    output = "```slideshow\n"
    for slide in presentation.slides_get():
        dirbasename = j.sal.fs.getBaseName(slide.dest)
        image_tag = '<img src="./{docsite_name}/{dirbasename}/{p}" alt="{p}" />'.format(
            docsite_name=doc.docsite.name, dirbasename=dirbasename, p=slide.url)
        output += """
            <section>
               <div class="slide-image">
                   {image}
                   <div style="font-size: 200%;">
                   {footer}
                   </div>
               </div>
            </section>""".format(image=image_tag, footer=slide.footer)
    output += "\n```"
    return output


def render(doc, url, width=0, height=0):
    if width != 0 and height != 0:
        j.tools.googleslides.export(url, credfile=CRED_FILE_PATH, serviceaccount=True,
                                    websitedir=EXPORT_TMP_DIR, resize=(width, height))
    else:
        j.tools.googleslides.export(url, credfile=CRED_FILE_PATH, serviceaccount=True, websitedir=EXPORT_TMP_DIR)
    pres_id = get_presentation_id(url)
    source = j.sal.fs.joinPaths(EXPORT_TMP_DIR, pres_id)
    dest = j.sal.fs.joinPaths(doc.docsite.outpath, pres_id)
    if j.sal.fs.exists(dest):
        j.sal.fs.remove(dest)
    j.sal.fs.moveDir(source, dest)

    files = [j.sal.fs.getBaseName(x) for x in j.sal.fs.listFilesInDir(dest)
             if x.endswith("png") and "_" in x and "background_" not in x]

    files.sort(key=lambda k: int(k.split("_")[0]))

    return files, dest


def get_slide_from_presntation(presentation, presentation_num, slide_num_of_presentation):
    # check if send index of slide or id of slide

    if j.data.types.int.check(slide_num_of_presentation):
        for presentation in presentation.presenation_get():
            if presentation.order == presentation_num:
                return presentation.slides[slide_num_of_presentation-1], presentation.dest

    for presentation in presentation.presenation_get():
        if presentation.order == presentation_num:
            for slide in presentation.slides:
                if slide_num_of_presentation.split(".")[1] in slide:
                    return slide, presentation.dest


class Presentations:
    def __init__(self):
        self.presentation = []
        self.slides = []

    def slide_add(self, url, footer, dest, order):
        self.slides.append(Slide(url, footer, order, dest))

    def slides_get(self):
        return sorted(self.slides, key=lambda slide: slide.order)

    def sorter(self, slide):
        return slide.order

    def presenation_add(self, slides, dest, order):
        self.presentation.append(presentation(slides, dest, order))

    def presenation_get(self):
        return sorted(self.presentation, key=lambda presentation: presentation.order)


class Slide:
    def __init__(self, url, footer, order, dest):
        self.url = url
        self.footer = footer
        self.order = order
        self.dest = dest


class presentation:
    def __init__(self, slides, dest, order):
        self.slides = slides
        self.order = order
        self.dest = dest
