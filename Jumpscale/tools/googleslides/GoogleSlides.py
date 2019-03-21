
from Jumpscale import j
import os.path

JSBASE = j.application.JSBaseClass

SLIDES2HTML_NOT_FOUND_MESSAGE = "Can't import slides2html. `pip3 install git+https://github.com/threefoldtech/slides2html` to install"


class GoogleSlides(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.tools.googleslides"
        self.__imports__ = "Pillow"
        JSBASE.__init__(self)

    def export(self, slideid, credfile, serviceaccount=False, background=None, websitedir="", indexfile="", themefile="", imagesize="MEDIUM", resize=None, credjson=""):
        """export presentation to a reveal website directory.

        Arguments:
            slideid {[str} -- [presentation id or presentation full url]
            credfile {[str]} -- [service account credentials or oauth2 credentials file path]

        Keyword Arguments:
            serviceaccount {bool} -- [indicator for service account type credentials] (default: {False})
            background {[str]} -- [background slide full url] (default: {None})
            websitedir {str} -- [reveal website directory path] (default: {""})
            indexfile {str} -- [index file path] (default: {""})
            themefile {str} -- [special theme file path] (default: {""})
            imagesize {str} -- [control the exported images size medium or large] (default: {"MEDIUM"})

        Raises:
            ValueError -- [Invalid presentation id.]
            ValueError -- [Invalid credentials file.]
        """

        from Jumpscale.tools.googleslides.slides2html.google_links_utils import get_slide_id, get_presentation_id, link_info
        from Jumpscale.tools.googleslides.slides2html.image_utils import images_to_transparent_background, set_background_for_images, resize_images
        from Jumpscale.tools.googleslides.slides2html.generator import Generator
        from Jumpscale.tools.googleslides.slides2html.downloader import Downloader
        from Jumpscale.tools.googleslides.slides2html.revealjstemplate import BASIC_TEMPLATE
        from Jumpscale.tools.googleslides.slides2html.tool import Tool

        presentation_id = slideid
        try:
            presentation_id, slideid = link_info(slideid)
        except ValueError:  # not a url, people using id as in old version.
            pass
        imagesize = imagesize.upper()
        if imagesize not in ["MEDIUM", "LARGE"]:
            raise ValueError(
                "Invalid image size should be MEDIUM or LARGE")

        if resize and "," in resize:
            try:
                newwidth, newheight = map(
                    lambda x: int(x.strip()), resize.split(","))
            except:
                raise ValueError(
                    "invalid size for --resize {}: should be 'width,height' ".format(resize))

        if not indexfile:
            indexfilepath = j.sal.fs.joinPaths(
                websitedir, "{}.html".format(presentation_id))
        else:
            indexfilepath = j.sal.fs.joinPaths(
                websitedir, "{}.html".format(indexfile))

        destdir = j.sal.fs.joinPaths(websitedir, presentation_id)
        credfile = os.path.abspath(os.path.expanduser(credfile))
        if not os.path.exists(credfile) and not credjson:
            raise ValueError(
                "Invalid credential file: {}".format(credfile))

        theme = ""
        themefilepath = os.path.expanduser(themefile)
        if os.path.exists(themefilepath):
            with open(themefilepath) as f:
                theme = f.read()
        else:
            theme = BASIC_TEMPLATE

        p2h = Tool(presentation_id, credfile,
                   serviceaccount=serviceaccount)
        p2h.downloader.thumbnailsize = imagesize
        p2h.build_revealjs_site(destdir, indexfilepath, template=theme)

        if background is not None:
            bgpath = p2h.downloader.get_background(background, destdir)
            p2h.convert_to_transparent_background(destdir)
            p2h.set_images_background(destdir, bgpath)

        if resize:
            newwidth, newheight = resize
            resize_images(destdir, (newwidth, newheight))
